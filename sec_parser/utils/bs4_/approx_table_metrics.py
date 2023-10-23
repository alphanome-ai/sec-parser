import re
from dataclasses import dataclass

import bs4


@dataclass
class ApproxTableMetrics:
    rows: int
    numbers: int


class NoTableFoundError(Exception):
    pass


class MultipleTablesFoundError(Exception):
    pass


def get_approx_table_metrics(bs4_tag: bs4.Tag) -> ApproxTableMetrics:
    if bs4_tag.name == "table":
        table = bs4_tag
    else:
        tables = bs4_tag.find_all("table")
        if not tables:
            msg = "No <table> tag found in the provided bs4 tag."
            raise NoTableFoundError(msg)
        if len(tables) > 1:
            msg = "Multiple <table> tags found in the provided bs4 tag."
            raise MultipleTablesFoundError(msg)
        table = tables[0]
    rows = sum(1 for row in table.find_all("tr") if row.find("td").text.strip())
    numbers = sum(
        bool(re.search(r"\d", cell.text))
        for cell in table.find_all("td")
        if cell.text.strip()
    )
    return ApproxTableMetrics(rows, numbers)
