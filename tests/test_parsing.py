import pytest

from kruiscijferraadsel import (
    get_section_starting_indexes,
    replace_section_indexes,
    section_filter,
)


@pytest.mark.parametrize(
    "given, expected",
    (
        ("111110010111111", "111110000111111"),
        ("100011110010101", "000011110000000"),
        ("110111111", "110111111"),
        ("0101010100101", "0000000000000"),
        ("111111011", "111111011"),
        ("1110101111", "1110001111"),
        ("10111110111101", "00111110111100"),
        ("010", "000"),
        ("011", "011"),
        ("011101110", "011101110"),
    ),
)
def test_section_filter(given, expected):
    assert section_filter(given) == expected


@pytest.mark.parametrize(
    "given, expected",
    (
        ("111110000111111", "ABCDE    JKLMNO"),
        ("000011110000000", "    EFGH       "),
        ("110111111", "AB DEFGHI"),
        ("0000000000000", "             "),
        ("111111011", "ABCDEF HI"),
        ("1110001111", "ABC   GHIJ"),
        ("00111110111100", "  CDEFG IJKL  "),
        ("000", "   "),
        ("011", " BC"),
        ("011101110", " BCD FGH "),
    ),
)
def test_replace_section_indexes(given, expected):
    assert replace_section_indexes(given) == expected


@pytest.mark.parametrize(
    "given, expected",
    (
        ("111110010111111", ["A", "J"]),
        ("100011110010101", ["E"]),
        ("110111111", ["A", "D"]),
        # ("0101010100101", "0000000000000"),
        # ("111111011", "111111011"),
        # ("1110101111", "1110001111"),
        # ("10111110111101", "00111110111100"),
        # ("010", "000"),
        # ("011", "011"),
        # ("011101110", "011101110"),
    ),
)
def test_get_section_starting_indexes(given, expected):
    assert replace_section_indexes(given) == expected
