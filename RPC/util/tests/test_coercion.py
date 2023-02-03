from enum import Enum

import pytest

from RPC.util.coercion import coerce_type


def test_coercion_basic():
    input_val = "True"
    coerce_to = bool
    expected = True

    actual = coerce_type(input_val, coerce_to)

    assert actual == expected
    assert type(actual) == coerce_to


def test_coercion_bool_unknown():
    input_val = "blort"
    coerce_to = bool
    expected = False

    actual = coerce_type(input_val, coerce_to)

    assert actual == expected


def test_coercion_enum_good():
    class TestEnum(Enum):
        ONE = 1
        UNO = 1
        TWO = 2
        DOS = 2

    coerce_to = TestEnum
    expected = [
        TestEnum.ONE,
        TestEnum.ONE,
        TestEnum.UNO,
        TestEnum.ONE,
        TestEnum.ONE,
    ]

    actual = [
        coerce_type("ONE", coerce_to),
        coerce_type("one", coerce_to),
        coerce_type("Uno", coerce_to),
        coerce_type("1", coerce_to),
        coerce_type(1, coerce_to),
    ]

    assert actual == expected
