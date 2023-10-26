import pytest

from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.processing_engine.html_tag_parser import HtmlTagParser
from sec_parser.semantic_elements.semantic_elements import NotYetClassifiedElement

from tests._sec_parser_validation_data import (
    DEFAULT_VALIDATION_DATA_DIR,
    Report,
    traverse_repository_for_reports,
)


@pytest.fixture(scope="package")
def parsed_reports() -> dict[Report, list[HtmlTag]]:
    bs4_root_tags: dict[Report, list[HtmlTag]] = {}
    for report in traverse_repository_for_reports():
        html_text = report.primary_doc_html_path.read_text()
        bs4_root_tags[report] = HtmlTagParser().parse(html_text)
    return bs4_root_tags


def html_tags_per_report() -> dict[Report, list[NotYetClassifiedElement]]:
    bs4_root_tags: dict[Report, list[HtmlTag]] = {}
    for report in traverse_repository_for_reports():
        html_text = report.primary_doc_html_path.read_text()
        bs4_root_tags[report] = HtmlTagParser().parse(html_text)
    return {
        report: [NotYetClassifiedElement(tag) for tag in tags]
        for report, tags in bs4_root_tags.items()
    }


@pytest.fixture(scope="package")
def elements_per_report() -> dict[Report, list[NotYetClassifiedElement]]:
    return html_tags_per_report()


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "report_and_html_tags" in metafunc.fixturenames:
        elements_per_report = html_tags_per_report()
        items = list(elements_per_report.items())
        ids = [report.identifier for report, _ in items]
        metafunc.parametrize("report_and_html_tags", items, ids=ids)
