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
    "power, start, stop, min_val, max_val",
    (
        (2, 10, 1000, "16", "961"),
        (2, 100, 10_000, "100", "10000"),
        (3, 1000, 10_000, "1000", "9261"),
        (3, 10_000, 100_000, "10648", "97336"),
        (3, 100_000, 1_000_000, "103823", "970299"),
        (3, 1_000_000, 10_000_000, "1000000", "9938375"),
    ),
)
def test_generator(start, stop, power, min_val, max_val):
    powers = list(kcr.powers_in_range(power, start, stop))
    assert powers[0] == min_val
    assert powers[-1] == max_val
