import pytest

from kruiscijferraadsel import NumberSection, Orientation, intersect


@pytest.mark.parametrize(
    "indexes, expected",
    (
        (("AB", "BB", "CB", "DB", "EB", "FB"), "AB"),
        (("FB", "FC", "FD", "FE", "FF"), "FB"),
    ),
)
def test_origin(indexes, expected):
    ns = NumberSection(indexes, options=set(), horizontal=True)
    assert ns.origin == expected


@pytest.mark.parametrize(
    "horizontal, vertical, expected",
    (
        (("AB", "BB", "CB", "DB", "EB", "FB"), ("FB", "FC", "FD", "FE", "FF"), True),
        (("AB", "BB", "CB", "DB", "EB", "FB"), ("FD", "FE", "FF"), False),
    ),
)
def test_intersect(horizontal, vertical, expected):
    ns_h = NumberSection(indexes=horizontal, options=set(), horizontal=True)
    ns_v = NumberSection(indexes=vertical, options=set(), horizontal=False)
    assert ns_h.intersects(ns_v) == expected
    assert ns_v.intersects(ns_h) == expected


def test_filter(intersection):
    intersection.filter()
    assert len(intersection.horizontal.options) == 4
    assert len(intersection.vertical.options) == 2
