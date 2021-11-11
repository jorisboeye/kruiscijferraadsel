import pytest

import kruiscijferraadsel as kcr


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
    assert kcr.section_filter(given) == expected


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
    assert kcr.replace_section_indexes(given) == expected


@pytest.mark.parametrize(
    "line, line_index, horizontal, expected",
    (
        (
            "111110000111111",
            "A",
            True,
            [("AA", "AB", "AC", "AD", "AE"), ("AJ", "AK", "AL", "AM", "AN", "AO")],
        ),
        ("000011110000000", "B", False, [("EB", "FB", "GB", "HB")]),
        ("110111111", "A", False, [("AA", "BA"), ("DA", "EA", "FA", "GA", "HA", "IA")]),
        ("0000000000000", "A", False, []),
        ("111111011", "C", False, [("AC", "BC", "CC", "DC", "EC", "FC"), ("HC", "IC")]),
        ("1110001111", "C", True, [("CA", "CB", "CC"), ("CG", "CH", "CI", "CJ")]),
        (
            "00111110111100",
            "C",
            True,
            [("CC", "CD", "CE", "CF", "CG"), ("CI", "CJ", "CK", "CL")],
        ),
        ("000", "C", True, []),
        ("000", "C", False, []),
    ),
)
def test_section_indexes(line, line_index, horizontal, expected):
    assert kcr.section_indexes(line, line_index, horizontal) == expected


def test_transpose_lines():
    lines = ["011011", "110001", "010100", "011100", "010001", "011111"]
    expected = ["010000", "111111", "100101", "001101", "100001", "110011"]
    assert kcr.transpose_lines(lines=lines) == expected


@pytest.mark.parametrize(
    "horizontal, expected",
    (
        (
            True,
            [
                ("AB", "AC"),
                ("AE", "AF"),
                ("BA", "BB"),
                ("DB", "DC", "DD"),
                ("FB", "FC", "FD", "FE", "FF"),
            ],
        ),
        (
            False,
            [
                ("AB", "BB", "CB", "DB", "EB", "FB"),
                ("CD", "DD"),
                ("AF", "BF"),
                ("EF", "FF"),
            ],
        ),
    ),
)
def test_parse_lines(horizontal, expected):
    lines = ["011011", "110001", "010100", "011100", "010001", "011111"]
    assert kcr.parse_lines(lines=lines, horizontal=horizontal) == expected
