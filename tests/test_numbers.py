import pytest

from kruiscijferraadsel import NumberSection, Orientation, intersect


@pytest.mark.parametrize(
    "orientation, expected",
    (("horizontal", Orientation.HORIZONTAL), ("vertical", Orientation.VERTICAL)),
)
def test_orientation(options, orientation, expected):
    ns = NumberSection(origin="A8", options=options[4], orientation=orientation)
    assert ns.orientation == expected


@pytest.mark.parametrize(
    "horizontal, vertical, h_idx, v_idx, expected",
    (
        ("test", "test", 1, 0, False),
        ("test", "test", 1, 1, True),
        ("untest", "test", 3, 1, True),
        ("untest", "test", 3, 2, False),
    ),
)
def test_intersect(horizontal, vertical, h_idx, v_idx, expected):
    assert intersect(horizontal, vertical, h_idx, v_idx) == expected


def test_filter(intersection):
    intersection.filter()
    assert len(intersection.horizontal.options) == 4
    assert len(intersection.vertical.options) == 2
