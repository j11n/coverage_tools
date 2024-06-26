# 3rd
import pytest

# local
from test_files_test.coverage_helpers import coverage_scope
from test_files_src.subdir_1 import source_code as TO


def setup_function(func):
    TO.my_function(7)


def teardown_function(func):
    TO.my_function(7)


@coverage_scope('test_files_src.subdir_1.source_code.my_function')
def test_my_function():
    assert TO.my_function(3) == 20
    

@coverage_scope('test_files_src.subdir_1.source_code.get_var_value')
def test_get_var_value():
    expected_result = 10
    assert TO.get_var_value() == expected_result


@coverage_scope('test_files_src.subdir_1.source_code.mult_by_two')
@pytest.mark.parametrize("value", [2, 4, 6])
def test_mult_by_two(value):
    assert 2 * value == TO.mult_by_two(value)


def test_topclass_wo_decorator():
    inst = TO.TopClass()
    assert inst.get_inner_b() == 77