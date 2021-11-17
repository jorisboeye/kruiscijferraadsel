import pytest

from kruiscijferraadsel import InterSection, NumberSection, generate_options


@pytest.fixture(scope="session")
def words():
    return frozenset(
        [
            "ABCD",
            "ABDC",
            "CDAB",
            "CDBA",
            "ABCDE",
            "BCDEA",
            "CDEAB",
            "DEABC",
            "EABCD",
            "ABCDEF",
            "BCDEFA",
            "CDEFAB",
            "DEFABC",
            "EFABCD",
            "FABCDE",
        ]
    )


@pytest.fixture(scope="session")
def options(words):
    return generate_options(words=words)


@pytest.fixture(scope="function")
def intersection(options):
    horizontal = NumberSection(
        indexes=("HA", "HB", "HC", "HD"), options=options[4], horizontal=True
    )
    vertical = NumberSection(
        indexes=("HB", "IB", "JB", "KB"), options=options[5], horizontal=False
    )
    return InterSection(horizontal=horizontal, vertical=vertical)


# @pytest.fixture(scope="function")
# def crossnumber(options):
#     cs = CrossNumber(words=options)
