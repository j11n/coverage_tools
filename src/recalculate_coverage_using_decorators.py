#!/bin/env python
#
# Copyright ©️: 2024 Jonny Eliasson, Ulsholmen AB, Sweden
#
# License: 3-clause BSD, see the end of file.
#
"""


    This program reduces the coverage for a test function with the 
    use of decorators prepending the test function.

    TODO:

        * input all source files as:
            files, directories to be parsed
            a file with directory paths within

            feature: exclude some file or directory

        * handle @property, @x.setter, @x.deleter ✅️

        * handle contexts with special handling with []|run (replaced by |run) ✅️

        * handle contexts ending with |setup or |teardown (removed) ✅️

        * add --permissive [enforcing]

        * first case, one source directory ✅️

        * input test_files to be checked

        * input coverage database to be used ✅️

        * add excluded lines

"""
# std
import argparse
import ast
import inspect
import logging
import pathlib
import pprint
import sys

# 3rd
import coverage


status_code = 0
debug = False


def set_status_code(code):
    global status_code

    if not status_code and code:
        status_code = code


def set_debug(value):
    global debug

    debug = value


def func_name(call_depth: int = 0):
    call_depth += 1
    return inspect.stack()[call_depth][3]


def dbg(txt):
    if debug:
        print(txt)

def dbg_print(txt):
    dbg(f'\n{txt}')
    dbg('*' * len(txt))


def dbg_pprint(obj):
    block = pprint.pformat(obj, indent=4)
    dbg(block)


def dbg_print_func(call_depth: int = 0):
    call_depth += 1
    name = func_name(call_depth=call_depth)
    dbg_print(name)


def get_all_source_code_definitions(sources):
    result = {}
    for file in find_python_files(sources):
        result = result | parse_python_file(file)
    dbg_pprint(result)
    return result


def get_decorators_to_test_functions(test_dir):
    dbg_print_func()
    result = {}
    for file in find_python_files(test_dir):
        dbg(f'file = {file}')
        result = result | find_decorators(file)

    return result


def parse_python_file(filename: pathlib.Path):
    dbg_print_func()
    dbg(f'{filename}')
    result = {}
    c_and_f = extract_classes_and_functions(ast.parse(filename.read_text()))
    c_and_f.sort(key=lambda x: x[1])
    dbg_pprint(c_and_f)
    for x in range(1, len(c_and_f)):
        for y in reversed(range(0, x)):
            if c_and_f[y][1] <= c_and_f[x][1] and c_and_f[y][2] >= c_and_f[x][2]:
                if c_and_f[x][0] == '@property':
                    c_and_f[x][0] = f'{c_and_f[y][0]}{c_and_f[x][0]}'
                else:
                    c_and_f[x][0] = f'{c_and_f[y][0]}.{c_and_f[x][0]}'
                break
    for x in range(0, len(c_and_f)):
        c_and_f[x].append(f'{filename.resolve().as_posix()}')
        c_and_f[x][0] = f'{filename.as_posix().removesuffix(".py").replace("/", ".")}.{c_and_f[x][0]}'
        result[c_and_f[x][0]] = {'file': c_and_f[x][3], 'first': c_and_f[x][1], 'last': c_and_f[x][2]}
    dbg_pprint(result)
    return result


def extract_classes_and_functions(ast_tree):
    """ """
    classes = []
    functions = []
    for node in ast.walk(ast_tree):
        if isinstance(node, ast.ClassDef):
            class_details = [node.name, node.lineno, node.end_lineno]
            classes.append(class_details)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_len = len(functions)
            for decorator in node.decorator_list:
                if hasattr(decorator, 'id') and getattr(decorator, 'id') == 'property':
                    functions += [[node.name, node.lineno, node.end_lineno]]
                    functions += [[f'@property', node.lineno, node.end_lineno]]
                elif hasattr(decorator, 'attr') and getattr(decorator, 'attr') == 'setter':
                    functions += [[f'{node.name}@setter', node.lineno, node.end_lineno]]
                elif hasattr(decorator, 'attr') and getattr(decorator, 'attr') == 'deleter':
                    functions += [[f'{node.name}@deleter', node.lineno, node.end_lineno]]

            if len(functions) == func_len:
                function_details = [node.name, node.lineno, node.end_lineno]
                functions.append(function_details)

    return classes + functions


def find_python_files(directory: pathlib.Path) -> list[pathlib.Path]:
    """Finds all Python files (.py) recursively within a given directory.

    Args:
        directory: The directory to search for Python files.

    Returns:
        A list of Path objects representing the found Python files.
    """
    dbg_print_func()
    python_files = []
    for path in directory.rglob("**/*.py"):
        if path.is_file():
            python_files.append(path)
    return python_files


def find_decorators(file, result: dict | None = None) -> dict:
    dbg_print_func()
    """
    Extracts a list of decorators, their arguments, and the decorated functions/methods from Python source code.

    Args:
        source (str): The Python source code to analyze.

    Returns:
        list: A list of tuples, where each tuple contains:
            - decorator_name (str): The name of the decorator.
            - decorator_args (list): A list of the decorator's arguments.
            - decorated_function (str): The name of the decorated function or method.
            - decorated_lineno (int): The line number where the decorator is applied.
    """

    tree = ast.parse(file.read_text())
    filename = f'{file}'
    result = result if result else {}

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        for decorator in node.decorator_list:
            if hasattr(decorator, 'func') and hasattr(decorator.func, 'id') and decorator.func.id == 'coverage_scope':
                dbg(f'decorator.args = {decorator.args}')
                if filename not in result:
                    result[filename] = {}
                if node.name not in result[filename]:
                    result[filename][node.name] = []
                for args in decorator.args:
                    result[filename][node.name].append(args.value)
                    dbg(f'    value = {args.value}')

    return result


def get_file_and_linenumber_sets(item, src_defs):
    dbg_print_func()
    if item in src_defs:
        return src_defs[item]['file'], set(range(src_defs[item]['first'], src_defs[item]['last'] + 1))
    return None, set()


def get_allowed_contexts(src_defs, decs, permissive: bool = False, keep_setup: bool = False, keep_teardown: bool = False) -> dict:
    dbg_print_func()
    result = {}
    for file, test_func_src_items in decs.items():
        for test_func, src_items in test_func_src_items.items():
            cntxt = f'{file}::{test_func}|run'
            for item in src_items:
                src_file, line_numbers = get_file_and_linenumber_sets(item, src_defs)
                if src_file not in result:
                    result[src_file] = {}
                if cntxt not in result[src_file]:
                    result[src_file][cntxt] = set()
                result[src_file][cntxt] = result[src_file][cntxt] | line_numbers

    return result


def filter_coverage_db(cov_db, allowed_contexts, permissive: bool=False):
    dbg('\n\n****************************************')
    dbg_pprint(cov_db)
    dbg_pprint(allowed_contexts)
    for filename, line_numbers in sorted(list(cov_db.items())):
        allowed_contexts_for_file = allowed_contexts.get(filename, {})
        for line_no, context_list in list(line_numbers.items()):
            new_list = []
            for context in context_list:
                if context == '':
                    new_list.append(context)
                else:
                    if context in allowed_contexts_for_file:
                        allowed_lines = allowed_contexts_for_file[context]
                        if line_no in allowed_lines:
                            new_list.append(context)
                    elif permissive:
                        new_list.append(context)
            if not new_list:
                line_numbers.pop(line_no, None)
            else:
                line_numbers[line_no] = new_list
    dbg_pprint(cov_db)
    return cov_db


def rearrange_cov_db(db):
    ret_value = {}
    for file, line_no_cntxt in db.items():
        for line_no, cntxt in line_no_cntxt.items():
            for ct in cntxt:
                if ct not in ret_value:
                    ret_value[ct] = {}
                if file not in ret_value[ct]:
                    ret_value[ct][file] = []
                ret_value[ct][file].append(line_no)
    return ret_value


def save_cov_db(db, filename: pathlib.Path) -> None:
    if filename.exists():
        old_fn = filename.with_name(f'{filename.name}.orig')
        filename.rename(old_fn)

    out_c_data = coverage.CoverageData(basename=filename)
    for context, cntxt_data in db.items():
        dbg(f'Context {context}')
        dbg(f'cntxt_data {cntxt_data}')
        out_c_data.set_context(context)
        out_c_data.add_lines(cntxt_data)
    out_c_data.write()


def filter_contexts(db):
    new_db = {}
    for filename in db.keys():
        new_db[filename] = {}
        for line_no, contexts in db[filename].items():
            filtered_ctx = []
            for ctx in contexts:
                if ctx.lower().endswith('|setup') or ctx.lower().endswith('|teardown'):
                    continue
                if ctx.lower().endswith(']|run'):
                    ctx = ctx[:ctx.rindex('[')] + '|run'
                if ctx not in filtered_ctx:
                    filtered_ctx.append(ctx)
            if filtered_ctx:
                new_db[filename][line_no] = filtered_ctx
    return new_db


def update_coverage_db(*, db_path, allowed_contexts, permissive, keep_setup, keep_teardown):
    """
        Change name on old coverage file to old.orig
        Filter data
        Save data to file old

        set_context()
        add_lines()
        write()
    """
    dbg_print_func()
    cov = coverage.Coverage(db_path)
    cov.load()

    data = cov.get_data()

    files = data.measured_files()
    contexts = data.measured_contexts()

    dbg(f'files = {files}')
    dbg(f'contexts = {contexts}')

    db = {}
    for file in files:
        db[file] = data.contexts_by_lineno(file)
    db = filter_contexts(db)

    cov_db_2 = filter_coverage_db(db, allowed_contexts, permissive)
    cov_db_3 = rearrange_cov_db(cov_db_2)
    dbg_pprint(cov_db_3)
    save_cov_db(cov_db_3, pathlib.Path('.output_db'))


def parse_command_line(arguments):
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-s',
        '--source',
        type=pathlib.Path,
        action='store',
        required=True,
        help='The location of the source files',
    )
    parser.add_argument(
        '-t',
        '--test',
        type=pathlib.Path,
        action='store',
        required=True,
        help='The location of the test files',
    )
    parser.add_argument(
        '-c',
        '--coverage-db',
        type=pathlib.Path,
        action='store',
        required=True,
        help='Location of the coverage database',
    )
    parser.add_argument(
        '-p',
        '--permissive',
        action='store_true',
        help='If decorator is missing all executed lines will be accounted for',
    )
    parser.add_argument(
        '-k',
        '--keep-setup',
        action='store_true',
        help='',
    )
    parser.add_argument(
        '-l',
        '--keep-teardown',
        action='store_true',
        help='',
    )
    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help='',
    )

    return vars(parser.parse_args(arguments))


def main(*, source, test, coverage_db, permissive: bool = False, keep_setup: bool = False, keep_teardown: bool = False, debug: bool = False):
    set_debug(debug)
    try:
        src_defs = get_all_source_code_definitions(source)
        for key, value in src_defs.items():
            dbg(f'   {key} = {value}')
    except Exception as ex:
        logging.exception(ex)
        src_defs = {}

    try:
        decs = get_decorators_to_test_functions(test)
        for key, value in decs.items():
            dbg(f'   {key} = {value}')
    except Exception as ex:
        logging.exception(ex)

    try:
        allowed_contexts = get_allowed_contexts(src_defs, decs)
        for key, value in allowed_contexts.items():
            dbg(f'   {key} = {value}')
    except Exception as ex:
        logging.exception(ex)

    try:
        update_coverage_db(
            db_path=coverage_db, 
            allowed_contexts=allowed_contexts,
            permissive=permissive,
            keep_setup=keep_setup,
            keep_teardown=keep_teardown)
    except Exception as ex:
        logging.exception(ex)

    return status_code


def _main(arguments) -> int:
    args = parse_command_line(arguments)
    dbg(f'args = {args}')
    main(**args)
    return status_code


if __name__ == '__main__':
    _main(sys.argv[1:])
    raise SystemExit(status_code)

#
# Copyright ©️: 2024 Jonny Eliasson, Ulsholmen AB, Sweden
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
