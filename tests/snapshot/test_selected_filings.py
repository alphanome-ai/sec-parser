from pathlib import Path

import yaml

from tests.utils import traverse_repository_for_filings

DEFAULT_YAML = Path(__file__).parent / "selected-filings.yaml"
