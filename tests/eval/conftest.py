import logging

import pytest

from sec_parser.processing_engine.core import Edgar10QParser
from sec_parser.processing_engine.html_tag_parser import HtmlTagParser
from tests.eval.types import ParsedDocumentComponents


@pytest.fixture(scope="session")
def parse():
    results = {}

    def _get_result(report):
        if report not in results:
            html_text = report.primary_doc_html_path.read_text()
            root_tags = HtmlTagParser().parse(html_text)
            elements = Edgar10QParser().parse_from_tags(root_tags)
            results[report] = ParsedDocumentComponents(report, root_tags, elements)
        return results[report]

    return _get_result
