# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
from dataclasses import dataclass
import os
import glob
import pprint
import re
from itertools import groupby
from typing import NamedTuple, Sequence, Union

FEATURE_FILES = [
    "Brewfile",
    "run.sh",
]

FEATURE_FILES_RE = re.compile(f".*({'|'.join(FEATURE_FILES)})$")
FEATURE_NAME_REGEX = re.compile(f"(.?..-)?(.*)$")


def main() -> None:
    targets = glob.glob("*", root_dir="targets")
    components = FeatureTree.build(discover("components"))

    pprint.pprint(components)


def discover(root_dir: str) -> list["FeatureFolder"]:
    return [
        FeatureFolder.parse(feature_folder)
        for feature_folder, g in groupby(
            [
                os.path.dirname(setupfile)
                for setupfile in sorted(
                    glob.glob(
                        "**", recursive=True, root_dir=root_dir, include_hidden=True
                    )
                )
                if FEATURE_FILES_RE.match(setupfile)
            ]
        )
    ]


@dataclass
class FeatureFolder:
    folder: str
    name: str
    categories: tuple[str, ...]
    selected: bool

    @classmethod
    def parse(cls, feature_folder: str) -> "FeatureFolder":
        categories, name = os.path.split(feature_folder)
        return cls(
            folder=feature_folder,
            name=denumbered_name(name),
            categories=tuple(
                [
                    denumbered_name(category)
                    for category in categories.split(os.path.sep)
                ]
            ),
            selected=False,
        )

    def is_part_of_categories(self, categories: tuple[str, ...]) -> bool:
        if len(categories) >= len(self.categories):
            return False
        return self.categories[: len(categories)] == categories

    def is_in_category(self, categories: tuple[str, ...]) -> bool:
        return categories == self.categories


@dataclass(frozen=True)
class FeatureTree:
    name: str
    contents: tuple[Union["FeatureTree", "FeatureFolder"], ...]

    @classmethod
    def build(
        cls,
        feature_folders: list["FeatureFolder"],
        categories: tuple[str, ...] = tuple(),
    ) -> "FeatureTree":
        contents: list[FeatureFolder] = []
        children: list[FeatureFolder] = []

        for feature_folder in feature_folders:
            if feature_folder.is_in_category(categories):
                contents.append(feature_folder)
            elif feature_folder.is_part_of_categories(categories):
                children.append(feature_folder)

        sub_tree = []
        for category, _ in groupby(
            children, key=lambda ff: ff.categories[: len(categories) + 1]
        ):
            sub_tree.append(cls.build(children, categories=category))

        return cls(
            name="root" if not len(categories) else categories[-1],
            contents=tuple(sub_tree + contents),
        )


def denumbered_name(name: str):
    matches = FEATURE_NAME_REGEX.match(name)
    if not matches:
        return name
    return matches.group(2)


if __name__ == "__main__":
    main()
