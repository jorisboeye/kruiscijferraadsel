import pytest

import kruiscijferraadsel as kcr


def test_version():
    assert kcr.__version__ == "0.1.0"


@pytest.mark.parametrize(
    "horizontal, vertical, h_idx, v_idx, expected",
    (
        ("test", "test", 1, 1, True),
        ("test", "test", 1, 2, False),
        ("test", "test", 2, 1, False),
        ("test", "test", 0, 3, True),
    ),
)
def test_intersect(horizontal, vertical, h_idx, v_idx, expected):
    assert kcr.intersect(horizontal, vertical, h_idx, v_idx) == expected


@pytest.mark.parametrize(
    "start, stop, min_val, max_val",
    (
        (1000, 10000, "1000", "9261"),
        (10000, 100000, "10648", "97336"),
        (100000, 1000000, "103823", "970299"),
        (1000000, 10000000, "1000000", "9938375"),
    ),
)
def test_generator(start, stop, min_val, max_val):
    thirdpowers = list(kcr.thirdpower(start, stop))
    assert thirdpowers[0] == min_val
    assert thirdpowers[-1] == max_val
