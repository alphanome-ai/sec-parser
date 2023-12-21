import difflib
import json
from dataclasses import dataclass
from pathlib import Path

from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)


@dataclass
class OverwriteResult:
    removed_lines: int
    added_lines: int
    created_file: bool


def overwrite_with_change_track(
    json_file: Path,
    elements: list[AbstractSemanticElement],
) -> OverwriteResult:
    dict_items = [
        e.to_dict(include_previews=True, include_contents=True) for e in elements
    ]
    created_file = False
    removed_lines = 0
    added_lines = 0

    if json_file.exists():
        with json_file.open("r") as f:
            old_content = f.read()
        new_content = json.dumps(
            dict_items,
            indent=4,
            ensure_ascii=False,
            sort_keys=True,
        )
        diff = list(
            difflib.unified_diff(old_content.splitlines(), new_content.splitlines()),
        )
        for line in diff:
            if line.startswith("-"):
                removed_lines += 1
            elif line.startswith("+"):
                added_lines += 1
    else:
        added_lines += len(dict_items)
        created_file = True

    with json_file.open("w") as f:
        json.dump(
            dict_items,
            f,
            indent=4,
            ensure_ascii=False,
            sort_keys=True,
        )

    return OverwriteResult(removed_lines, added_lines, created_file)
