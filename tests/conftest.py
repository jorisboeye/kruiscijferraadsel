import pytest

from kruiscijferraadsel import NumberIntersection, NumberSection, generate_options


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
        origin="A8", options=options[4], orientation="horizontal"
    )
    vertical = NumberSection(origin="B8", options=options[5], orientation="vertical")
    return NumberIntersection(
        horizontal=horizontal, vertical=vertical, horizontal_idx=0, vertical_idx=0
    )


# @pytest.fixture(scope="function")
# def crossnumber(options):
#     cs = CrossNumber(words=options)
