from pathlib import Path

import yaml

from tests.utils import traverse_repository_for_filings

DEFAULT_YAML = Path(__file__).parent / "selected-filings.yaml"

SUPPORTED_DOCUMENT_TYPES = {"10-K", "10-Q"}

def test_filings_exist():
    with DEFAULT_YAML.open("r") as file:
        selected_filings = yaml.safe_load(file)
    accession_numbers = list(selected_filings["accession_numbers"])
    assert accession_numbers, "No accession numbers found in YAML file."

    existing_filings = {
        (report.accession_number, report.document_type) 
        for report in traverse_repository_for_filings()
    }

    for accession_number in accession_numbers:
        # Find all matches for this accession number
        matches = [(acc, doc_type) for (acc, doc_type) in existing_filings 
                  if acc == accession_number]
        
        # Check if filing exists
        assert matches, f"Missing {accession_number}"
        
        # Check document type is supported
        for _, doc_type in matches:
            if doc_type not in SUPPORTED_DOCUMENT_TYPES:
                msg = f"Unsupported document type: {doc_type} for {accession_number}. Only {SUPPORTED_DOCUMENT_TYPES} are currently supported."
                raise ValueError(msg)