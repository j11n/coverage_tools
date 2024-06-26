# 3rd
import pytest

# local
from test_files_test.coverage_helpers import coverage_scope
from test_files_src import main as TO


@coverage_scope('test_files_src.main.main')
def test_main12():
    TO.main()


@coverage_scope('test_files_src.main.MyClass.number@setter')
def test_number_setter():
    inst = TO.MyClass()
    inst.number = 33
    assert inst._number == 33


@coverage_scope('test_files_src.main.MyClass.number@deleter')
def test_number_deleter():
    # Calls the @setter which will not be accounted for after recalculation
    inst = TO.MyClass()
    inst.number = 35
    assert inst._number == 35
