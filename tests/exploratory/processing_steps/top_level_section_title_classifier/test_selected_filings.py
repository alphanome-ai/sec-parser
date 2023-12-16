from pathlib import Path

import yaml

from tests.utils import traverse_repository_for_filings

DEFAULT_YAML = Path(__file__).parent / "selected-filings.yaml"


def test_filings_exist():
    with DEFAULT_YAML.open("r") as file:
        selected_filings = yaml.safe_load(file)
    accession_numbers = list(selected_filings["accession_numbers"])
    assert accession_numbers, "No accession numbers found in YAML file."

    existing_numbers = {
        report.accession_number for report in traverse_repository_for_filings()
    }

    for accession_number in accession_numbers:
        assert accession_number in existing_numbers, f"Missing {accession_number}"
