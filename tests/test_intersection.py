import pytest

from kruiscijferraadsel import InterSection, NumberSection


@pytest.mark.parametrize(
    "h_indexes, v_indexes, expected",
    (
        (("FB", "FC", "FD", "FE", "FF"), ("AB", "BB", "CB", "DB", "EB", "FB"), "FB"),
        (("AJ", "AK", "AL", "AM", "AN", "AO"), ("AL", "BL", "CL"), "AL"),
    ),
)
def test_position(h_indexes, v_indexes, expected):
    intersection = InterSection(
        horizontal=NumberSection(indexes=h_indexes, options=set(), horizontal=True),
        vertical=NumberSection(indexes=v_indexes, options=set(), horizontal=False),
    )
    assert intersection.position == expected
