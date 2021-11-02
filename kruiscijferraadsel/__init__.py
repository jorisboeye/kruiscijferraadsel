__version__ = "0.1.0"

import string
from collections import defaultdict
from copy import deepcopy
from enum import Enum
from typing import Dict, FrozenSet, List, Set, Tuple

import attr
import numpy as np
from attr.validators import instance_of


def thirdpower(start, stop):
    i_start = int(np.ceil(start ** (1 / 3)))
    i_stop = int(np.floor(stop ** (1 / 3))) + 1
    for i in range(i_start, i_stop):
        yield str(i ** 3)


def generate_options(words):
    options = defaultdict(list)
    for word in words:
        options[len(word)].append(word)
    return {x: frozenset(options[x]) for x in options}


def intersect(horizontal, vertical, h_idx, v_idx):
    return horizontal[h_idx] == vertical[v_idx]


def match(char: str, options: Set[str], idx: int):
    return {x for x in options if x[idx] == char}


def matches(section, other, idx, other_idx):
    options = set()
    for option in section.options:
        options = options | match(option[idx], other.options, other_idx)
    return options


class Orientation(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


@attr.s(auto_attribs=True)
class NumberSection:
    origin: str
    options: Set[str] = attr.ib(validator=instance_of(set), converter=set)
    orientation: Orientation = attr.ib(
        validator=instance_of(Orientation), converter=lambda x: Orientation[x.upper()]
    )
    length: int = attr.ib(init=False)
    indexes: Tuple[str] = attr.ib(init=False)

    def __attrs_post_init__(self):
        self.length = len(next(iter(self.options)))
        self.indexes = self.get_indexes()

    def __len__(self):
        return self.length

    def get_indexes(self):
        if self.orientation == Orientation.HORIZONTAL:
            start = self.origin[0]
            cst = self.origin[-1]
        else:
            start = self.origin[-1]
            cst = self.origin[0]
        indexes = string.ascii_uppercase
        start_idx = indexes.find(start)
        end_idx = start_idx + self.length
        indexes = indexes[start_idx:end_idx]
        if self.orientation == Orientation.HORIZONTAL:
            return [f"{idx}{cst}" for idx in indexes]
        else:
            return [f"{cst}{idx}" for idx in indexes]


@attr.s(auto_attribs=True)
class NumberIntersection:
    horizontal: NumberSection = attr.ib(validator=instance_of(NumberSection))
    vertical: NumberSection = attr.ib(validator=instance_of(NumberSection))
    horizontal_idx: int = attr.ib(validator=instance_of(int))
    vertical_idx: int = attr.ib(validator=instance_of(int))

    def filter(self):
        vertical_options = matches(
            self.horizontal,
            self.vertical,
            self.horizontal_idx,
            self.vertical_idx,
        )
        horizontal_options = matches(
            self.vertical,
            self.horizontal,
            self.vertical_idx,
            self.horizontal_idx,
        )
        self.vertical.options = vertical_options
        self.horizontal.options = horizontal_options


@attr.s(repr=False)
class CrossNumber:
    sections: Dict[str, NumberSection] = attr.ib(factory=dict)
    intersections: List[NumberIntersection] = attr.ib(factory=list)
    words: FrozenSet[str] = attr.ib(default=frozenset(thirdpower(1000, 10_000_000)))
    options: Dict[int, FrozenSet[str]] = attr.ib(init=False)

    def __attrs_post_init__(self):
        self.options = generate_options(words=self.words)

    def add_section(self, identifier, length):
        origin, orientation = identifier.split("-")
        orientation = "horizontal" if orientation == "h" else "vertical"
        self.sections[identifier] = NumberSection(
            origin=origin, options=self.options[length], orientation=orientation
        )

    def connect(self, horizontal_key, vertical_key, horizontal_idx, vertical_idx):
        self.intersections.append(
            NumberIntersection(
                horizontal=self.sections[horizontal_key],
                vertical=self.sections[vertical_key],
                horizontal_idx=horizontal_idx,
                vertical_idx=vertical_idx,
            )
        )

    def filter(self):
        for intersection in self.intersections:
            intersection.filter()

    def generate_uniques(self):
        for section in self.sections.values():
            if len(section.options) == 1:
                yield section.options

    @property
    def uniques(self):
        uniques = set()
        for unique in self.generate_uniques():
            uniques = uniques | unique
        return uniques

    def parse_uniques(self):
        for section_key, section in self.sections.items():
            if len(section.options) > 1:
                self.sections[section_key].options = section.options.difference(
                    self.uniques
                )

    @property
    def option_lengths(self):
        return [len(section.options) for section in self.sections.values()]

    def assume(self, label):
        remove = set()
        for option in self.sections[label].options:
            assumed = deepcopy(self)
            assumed.sections[label].options = set([option])
            assumed.solve()
            if min(assumed.option_lengths) == 0:
                remove.add(option)
            elif max(assumed.option_lengths) == 1:
                print("SOLVED!")
        self.sections[label].options = self.sections[label].options.difference(remove)

    @property
    def score(self):
        return sum([len(section.options) - 1 for section in self.sections.values()])

    def solve(self, max_steps=25):
        ref_score = self.score + 1
        step = 0
        while ref_score != self.score and ref_score > 0 and step < max_steps:
            step += 1
            if step == max_steps:
                print("max steps hit.")
            ref_score = self.score
            self.parse_uniques()
            self.filter()

    def get_value(self, position):
        for section in self.sections.values():
            if position in section.indexes:
                if len(section.options) == 1:
                    value = list(section.options)[0][section.indexes.index(position)]
                    return f" {value} "
                else:
                    return "   "
        return "\u2588" * 3

    def __repr__(self):
        indexes = " ABCDEFGHIJKLMNO"
        output = ""
        for r_idx, row in enumerate(indexes):
            output += row + " |"
            for c_idx, column in enumerate(indexes):
                if c_idx:
                    if r_idx:
                        value = self.get_value(position=f"{column}{row}")
                        output += f"{value}|"
                    else:
                        output += f" {column} |"
            output += "\n" + 62 * "-" + "|\n"
        return output


def generate_graph(fixed=None):
    cs = CrossNumber()
    # sections
    cs.add_section("AA-h", 5)
    cs.add_section("AA-v", 6)
    cs.add_section("AC-h", 5)
    cs.add_section("AE-h", 7)
    cs.add_section("AH-h", 4)
    cs.add_section("AK-h", 7)
    cs.add_section("AK-v", 5)
    cs.add_section("AO-h", 6)
    cs.add_section("BH-v", 4)
    cs.add_section("CC-v", 6)
    cs.add_section("CM-h", 6)
    cs.add_section("CK-v", 5)
    cs.add_section("EA-v", 7)
    cs.add_section("EB-h", 4)
    cs.add_section("EG-h", 7)
    cs.add_section("EI-h", 7)
    cs.add_section("EI-v", 7)
    cs.add_section("GE-v", 7)
    cs.add_section("HA-v", 4)
    cs.add_section("HC-h", 6)
    cs.add_section("HL-v", 4)
    cs.add_section("HN-h", 4)
    cs.add_section("IE-h", 7)
    cs.add_section("IE-v", 7)
    cs.add_section("IK-h", 7)
    cs.add_section("JA-h", 6)
    cs.add_section("KM-h", 5)
    cs.add_section("KA-v", 7)
    cs.add_section("KI-v", 7)
    cs.add_section("KO-h", 5)
    cs.add_section("LH-h", 4)
    cs.add_section("MA-v", 5)
    cs.add_section("MH-v", 6)
    cs.add_section("NE-v", 4)
    cs.add_section("OA-v", 5)
    cs.add_section("OJ-v", 6)

    # intersections
    cs.connect("AA-h", "AA-v", 0, 0)
    cs.connect("AA-h", "EA-v", 4, 0)
    cs.connect("AC-h", "AA-v", 0, 2)
    cs.connect("AC-h", "CC-v", 2, 0)
    cs.connect("AC-h", "EA-v", 4, 2)
    cs.connect("AE-h", "AA-v", 0, 4)
    cs.connect("AE-h", "CC-v", 2, 2)
    cs.connect("AE-h", "EA-v", 4, 4)
    cs.connect("AE-h", "GE-v", -1, 0)
    cs.connect("AH-h", "BH-v", 1, 0)
    cs.connect("AH-h", "CC-v", 2, -1)
    cs.connect("AK-h", "BH-v", 1, 3)
    cs.connect("AK-h", "AK-v", 0, 0)
    cs.connect("AK-h", "CK-v", 2, 0)
    cs.connect("AK-h", "EI-v", 4, 2)
    cs.connect("AK-h", "GE-v", -1, -1)
    cs.connect("AO-h", "AK-v", 0, 4)
    cs.connect("AO-h", "CK-v", 2, 4)
    cs.connect("AO-h", "EI-v", 4, 6)
    cs.connect("CM-h", "CK-v", 0, 2)
    cs.connect("CM-h", "EI-v", 2, 4)
    cs.connect("CM-h", "HL-v", -1, 1)
    cs.connect("EB-h", "EA-v", 0, 1)
    cs.connect("EB-h", "HA-v", 3, 1)
    cs.connect("EG-h", "EA-v", 0, 6)
    cs.connect("EG-h", "GE-v", 2, 2)
    cs.connect("EG-h", "IE-v", 4, 2)
    cs.connect("EG-h", "KA-v", 6, 6)
    cs.connect("EI-h", "EI-v", 0, 0)
    cs.connect("EI-h", "GE-v", 2, 4)
    cs.connect("EI-h", "IE-v", 4, 4)
    cs.connect("EI-h", "KI-v", 6, 0)
    cs.connect("HC-h", "HA-v", 0, 3)
    cs.connect("HC-h", "KA-v", 3, 3)
    cs.connect("HC-h", "MA-v", 5, 3)
    cs.connect("HN-h", "HL-v", 1, 2)
    cs.connect("HN-h", "KI-v", 3, 5)
    cs.connect("IE-h", "IE-v", 0, 0)
    cs.connect("IE-h", "KA-v", 2, 4)
    cs.connect("IE-h", "MA-v", 4, 4)
    cs.connect("IE-h", "NE-v", 5, 0)
    cs.connect("IE-h", "OA-v", 6, 4)
    cs.connect("IK-h", "IE-v", 0, 6)
    cs.connect("IK-h", "KI-v", 2, 2)
    cs.connect("IK-h", "MH-v", 4, 3)
    cs.connect("IK-h", "OJ-v", 6, 1)
    cs.connect("JA-h", "KA-v", 1, 0)
    cs.connect("JA-h", "MA-v", 3, 0)
    cs.connect("JA-h", "OA-v", 5, 0)
    cs.connect("KM-h", "KI-v", 0, 4)
    cs.connect("KM-h", "MH-v", 2, 5)
    cs.connect("KM-h", "OJ-v", 4, 3)
    cs.connect("KO-h", "KI-v", 0, -1)
    cs.connect("KO-h", "OJ-v", -1, -1)
    cs.connect("LH-h", "MH-v", 1, 0)
    cs.connect("LH-h", "NE-v", 2, -1)

    if fixed is not None:
        for section_key, options in fixed.items():
            cs.sections[section_key].options = options
    return cs


if __name__ == "__main__":
    cs = generate_graph()
    print("=" * 80)
    initial = {}
    for origin, section in cs.sections.items():
        initial[origin] = len(section.options)
    ref_score = cs.score

    print(cs.score)
    cs.solve()
    print(cs.score)
    iterations = 0
    while cs.score > 0 and iterations <= 10:
        iterations += 1
        for section_key in cs.sections:
            cs.assume(section_key)
            cs.solve()
            print(section_key, cs.score)

    # print("=" * 80)
    # for origin, section in cs.sections.items():
    #     print(origin, section.options)
    print(cs)
    for idx, pos in zip("ABCDEFGH", ["KB", "OC", "CF", "EG", "KL", "CL", "GM", "JI"]):
        print(idx, cs.get_value(pos))
