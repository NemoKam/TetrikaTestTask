import pytest

from task1.solution import strict


@strict
def strict_test_sum(a: int, b: int) -> int:
    return a + b


@strict
def strict_test_mutiple(a: int, b: float, c: int) -> float:
    return a * b * c


@strict
def strict_test_different_types(a: bool, b: str, c: float, d: int) -> None:
    return None



def test_correct_sum_func():
    assert strict_test_sum(1, 2) == 3
    assert strict_test_sum(b=1, a=2) == 3
    assert strict_test_sum(a=10, b=5) == 15


def test_fail_sum_func():
    with pytest.raises(TypeError):
        strict_test_sum(1.0, 2.0)
    with pytest.raises(TypeError):
        strict_test_sum(1, 2.0)
    with pytest.raises(TypeError):
        strict_test_sum(1.0, 2)
    with pytest.raises(TypeError):
        strict_test_sum("1", "2")
    with pytest.raises(TypeError):
        strict_test_sum(1, "2")
    with pytest.raises(TypeError):
        strict_test_sum("1", 2)


def test_correct_multiple_func():
    assert strict_test_mutiple(1, 2.0, 3) == 6.0
    assert strict_test_mutiple(1, 0.5, 3) == 1.5


def test_fail_multiple_func():
    with pytest.raises(TypeError):
        strict_test_mutiple(1.0, 2, 3) == 6.0
    with pytest.raises(TypeError):
        strict_test_mutiple(1, 2, 3.0) == 6.0
    with pytest.raises(TypeError):
        strict_test_mutiple("1", "2", "3")
    with pytest.raises(TypeError):
        strict_test_mutiple(1, "2", "3")
    with pytest.raises(TypeError):
        strict_test_mutiple("1", 2, "3")


def test_correct_different_types_func():
    assert strict_test_different_types(True, "test", 1.0, 2) is None
    assert strict_test_different_types(False, "test", 1.0, 2) is None
    assert strict_test_different_types(True, "test", 1.5, 2) is None


def test_fail_different_types_func():
    with pytest.raises(TypeError):
        strict_test_different_types(False, "test", 1, 2)
    with pytest.raises(TypeError):
        strict_test_different_types("True", "test", 1.0, 2)
    with pytest.raises(TypeError):
        strict_test_different_types(True, "test", "1.0", 2)
    with pytest.raises(TypeError):
        strict_test_different_types(True, "test", 1.0, "2")
