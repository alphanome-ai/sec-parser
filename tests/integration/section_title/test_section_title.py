import json
from pathlib import Path
from typing import Callable

import pytest

from sec_parser.processing_engine.core import (
    AbstractSemanticElementParser,
    Edgar10QParser,
)

CURRENT_DIR = Path(__file__).resolve().parent


@pytest.mark.parametrize("html_path", list((CURRENT_DIR / "data").glob("*.html")))
def test_bold_titles(
    html_path: Path,
    check: Callable[[AbstractSemanticElementParser, Path, pytest.FixtureRequest], None],
    request: pytest.FixtureRequest,
):
    def get_steps():
        return [k for k in Edgar10QParser().get_default_steps() if True]

    parser = Edgar10QParser(get_steps)
    check(parser, html_path, request)
