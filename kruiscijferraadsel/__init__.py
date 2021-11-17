__version__ = "0.1.0"

import re
import string
from collections import defaultdict
from copy import deepcopy
from enum import Enum
from typing import Dict, FrozenSet, List, Set, Tuple

import attr
import numpy as np
from attr.validators import instance_of


def powers_in_range(power: int, start: int, stop: int):
    i_start = int(np.ceil(start ** (1 / power)))
    i_stop = int(np.floor(stop ** (1 / power))) + 1
    for i in range(i_start, i_stop):
        yield str(i ** power)


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


def section_filter(line: str) -> str:
    """Filter out non sections in a line (row or column)

    A section in a certain line (a row or a column) consists of at least
    two `1` characters. If a single `1` character occurs, this needs not
    be evaluated. This function filters out these single `1`s.

    Parameters
    ----------
    line : str
        [description]

    Returns
    -------
    str
        [description]
    """

    return re.sub(r"(?:^|[^1])1(?=[^1]|$)", lambda x: "0" * len(x.group()), line)


def replace_section_indexes(line: str) -> str:
    """Replace each section component with its alphabetical index."""
    return "".join(
        [idx if int(s) else " " for idx, s in zip(string.ascii_uppercase, line)]
    )


def section_indexes(line: str, line_index: str, horizontal: bool) -> List[Tuple[str]]:
    sections = replace_section_indexes(line=section_filter(line=line)).strip().split()
    if horizontal:
        return [tuple(line_index + idx for idx in section) for section in sections]
    else:
        return [tuple(idx + line_index for idx in section) for section in sections]


def section_generator(lines: List[str], horizontal: bool):
    for line_index, line in zip(string.ascii_uppercase, lines):
        sections = section_indexes(
            line=line, line_index=line_index, horizontal=horizontal
        )
        for section in sections:
            yield section


def transpose_lines(lines: List[str]):
    return list(map("".join, zip(*lines)))


def parse_lines(lines: List[str], horizontal: bool):
    if not horizontal:
        lines = transpose_lines(lines=lines)
    return list(section_generator(lines=lines, horizontal=horizontal))


class Orientation(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


@attr.s(auto_attribs=True)
class NumberSection:
    indexes: FrozenSet[str] = attr.ib(
        validator=instance_of(frozenset), converter=frozenset
    )
    options: Set[str] = attr.ib(validator=instance_of(set), converter=set)
    horizontal: bool = attr.ib(validator=instance_of(bool))

    def __len__(self):
        return len(self.indexes)

    @property
    def origin(self):
        return min(self.indexes)

    @property
    def label(self):
        suffix = "-h" if self.horizontal else "-v"
        return self.origin + suffix

    def intersects(self, other: "NumberSection") -> bool:
        if self.horizontal == other.horizontal:
            raise ValueError("Sections with identical orientation can't intersect.")
        return bool(self.indexes.intersection(other.indexes))


@attr.s(auto_attribs=True, repr=False)
class InterSection:
    horizontal: NumberSection = attr.ib(validator=instance_of(NumberSection))
    vertical: NumberSection = attr.ib(validator=instance_of(NumberSection))

    @property
    def position(self):
        (position,) = self.horizontal.indexes.intersection(self.vertical.indexes)
        return position

    @property
    def horizontal_idx(self):
        return string.ascii_uppercase.find(
            self.position[0]
        ) - string.ascii_uppercase.find(self.horizontal.origin[0])

    @property
    def vertical_idx(self):
        return string.ascii_uppercase.find(
            self.position[-1]
        ) - string.ascii_uppercase.find(self.vertical.origin[-1])

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

    def __repr__(self):
        return f"{self.vertical.origin}-{self.horizontal.origin}-{self.position}"


@attr.s(repr=False)
class CrossNumber:
    sections: Dict[str, NumberSection] = attr.ib(factory=dict)
    intersections: List[InterSection] = attr.ib(factory=list)
    words: FrozenSet[str] = attr.ib(default=frozenset(), converter=frozenset)
    options: Dict[int, FrozenSet[str]] = attr.ib(init=False)

    def __attrs_post_init__(self):
        self.options = generate_options(words=self.words)

    def add_section(self, indexes: Tuple[str], horizontal: bool):
        section = NumberSection(
            indexes=indexes, options=self.options[len(indexes)], horizontal=horizontal
        )
        self.sections[section.label] = section

    @property
    def horizontal_sections(self):
        return [s for s in self.sections.values() if s.horizontal]

    @property
    def vertical_sections(self):
        return [s for s in self.sections.values() if not s.horizontal]

    def connect(self):
        for horizontal in self.horizontal_sections:
            for vertical in self.vertical_sections:
                if horizontal.intersects(vertical):
                    intersection = InterSection(
                        horizontal=horizontal, vertical=vertical
                    )
                    if intersection not in self.intersections:
                        self.intersections.append(intersection)

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

    @property
    def is_invalid(self):
        """Check if the current state is invalid."""
        return min(self.option_lengths) == 0

    @property
    def is_solved(self):
        """Check if the current state is a solution."""
        return max(self.option_lengths) == 1

    def assume(self, label):
        remove = set()
        for option in self.sections[label].options:
            assumed = deepcopy(self)
            assumed.sections[label].options = set([option])
            assumed.solve()
            if assumed.is_invalid:
                remove.add(option)
            elif assumed.is_solved:
                print("SOLVED!")
                return assumed
        self.sections[label].options = self.sections[label].options.difference(remove)
        return self

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

    @property
    def intersection_positions(self):
        return [intersection.position for intersection in self.intersections]

    def is_intersection(self, position):
        for intersection in self.intersections:
            if intersection.position == position:
                return True
        return False

    def get_intersection_value(self, position):
        if self.is_intersection(position=position):
            return " X "
        for section in self.sections.values():
            if position in section.indexes:
                return "   "
        return "\u2588" * 3

    def print_intersections(self):
        indexes = " ABCDEFGHIJKLMNO"
        output = ""
        for r_idx, row in enumerate(indexes):
            output += row + " |"
            for c_idx, column in enumerate(indexes):
                if c_idx:
                    if r_idx:
                        value = self.get_intersection_value(position=f"{column}{row}")
                        output += f"{value}|"
                    else:
                        output += f" {column} |"
            output += "\n" + 62 * "-" + "|\n"
        return output


def get_block_coord_dict(c: np.array, transpose: bool):
    horizontal_block_coords = []
    if transpose:
        c = c.T
    for y_i, row in enumerate(c):
        for x_i, cell in enumerate(row):
            if x_i == 0 and cell and row[x_i + 1]:
                horizontal_block_coords.append((y_i, x_i))
            elif x_i < (len(row) - 2) and cell and not row[x_i - 1] and row[x_i + 1]:
                horizontal_block_coords.append((y_i, x_i))

    horizontal_block_coords_dict = {}
    for y, x in horizontal_block_coords:
        row = c[y, x:]
        first_false = np.argmin(row)
        if first_false:
            if transpose:
                horizontal_block_coords_dict[x, y] = first_false
            else:
                horizontal_block_coords_dict[y, x] = first_false
        else:
            if transpose:
                horizontal_block_coords_dict[x, y] = len(row)
            else:
                horizontal_block_coords_dict[y, x] = len(row)
    return horizontal_block_coords_dict


def generate_graph(input_file, fixed=None, **kwargs):
    cs = CrossNumber(**kwargs)
    crossnumber_array = np.loadtxt(input_file)
    letters = string.ascii_uppercase[: len(crossnumber_array)]
    # sections
    h_block_coords = get_block_coord_dict(crossnumber_array, transpose=False)
    for coord, digits in h_block_coords.items():
        cs.add_section(f"{letters[coord[1]]}{letters[coord[0]]}-h", digits)

    v_block_coords = get_block_coord_dict(crossnumber_array, transpose=True)
    for coord, digits in v_block_coords.items():
        cs.add_section(f"{letters[coord[1]]}{letters[coord[0]]}-v", digits)

    # intersections
    for h_coord, h_digits in h_block_coords.items():
        for v_coord, v_digits in v_block_coords.items():
            # check if intersects
            if (h_coord[1] <= v_coord[1] <= h_coord[1] + h_digits - 1) and (
                v_coord[0] <= h_coord[0] <= v_coord[0] + v_digits - 1
            ):
                cs.connect(
                    f"{letters[h_coord[1]]}{letters[h_coord[0]]}-h",
                    f"{letters[v_coord[1]]}{letters[v_coord[0]]}-v",
                    v_coord[1] - h_coord[1],
                    h_coord[0] - v_coord[0],
                )

    if fixed is not None:
        for section_key, options in fixed.items():
            cs.sections[section_key].options = options
    return cs


CONFIG = {
    "kwadraten": {
        "solution": ["IG", "DB", "BI", "GD", "EB", "BE", "AC", "BA"],
        "input_file": "kwadraten_input.txt",
        "word_generator": powers_in_range(2, 10, 1_000_000),
    },
    "derdemachten": {
        "solution": ["KB", "OC", "CF", "EG", "KL", "CL", "GM", "JI"],
        "input_file": "derdemachten_input.txt",
        "word_generator": powers_in_range(3, 1000, 10_000_000),
    },
}


if __name__ == "__main__":
    challenge = CONFIG["derdemachten"]
    cs = generate_graph(
        input_file=challenge["input_file"], words=challenge["word_generator"]
    )
    cs.solve()
    iterations = 0
    while not cs.is_solved and iterations <= 10:
        iterations += 1
        for section_key in cs.sections:
            cs = cs.assume(section_key)
            cs.solve()
            print(section_key, cs.score)
            if cs.is_solved:
                break
    print(cs)
    for idx, pos in zip(string.ascii_uppercase, challenge["solution"]):
        print(idx, cs.get_value(pos))
    array = np.loadtxt(challenge["input_file"])
    print(array)
    print(np.diff(array, axis=1))
