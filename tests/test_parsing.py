import pytest

from kruiscijferraadsel import section_filter


@pytest.mark.parametrize(
    "given, expected",
    (
        ("111110010111111", "111110000111111"),
        ("100011110010101", "000011110000000"),
        ("110111111", "110111111"),
        ("010101010", "000000000"),
        ("111111011", "111111011"),
        ("111001111", "111001111"),
        ("101111101", "001111100"),
        ("011101110", "011101110"),
    ),
)
def test_section_filter(given, expected):
    assert section_filter(given) == expected
