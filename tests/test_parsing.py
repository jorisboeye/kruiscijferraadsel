import pytest

from kruiscijferraadsel import section_filter


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
