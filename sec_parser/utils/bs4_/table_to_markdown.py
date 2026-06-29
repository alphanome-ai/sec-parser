import re
from io import StringIO

import bs4
import pandas as pd

from sec_parser.utils.bs4_.get_single_table import get_single_table


class TableToMarkdown:
    def __init__(self, tag: bs4.Tag) -> None:
        self._tag = tag
        self._soup = bs4.BeautifulSoup("", features="lxml")

    def convert(self) -> str:
        tag = get_single_table(self._tag)
        unmerged = self._unmerge_cells(tag)
        pandas_table = pd.read_html(StringIO(str(unmerged)), flavor="lxml")[0]
        return self._to_markdown_table(pandas_table)

    def _unmerge_cells(self, bs4_tag: bs4.Tag) -> bs4.Tag:
        for td in bs4_tag.find_all("td"):
            if td.has_attr("colspan"):
                for _ in range(int(td["colspan"]) - 1):
                    new_td = self._soup.new_tag("td")
                    new_td.string = "NaN"
                    td.insert_before(new_td)
                td["colspan"] = 1
        return bs4_tag

    @staticmethod
    def _to_markdown_table(pandas_table: pd.DataFrame) -> str:
        pandas_table = pandas_table.dropna(how="all").fillna(
            "",
        )  # remove empty rows and fill NaN values
        all_headers_are_digits = all(
            isinstance(header, int) or header.isdigit()
            for header in pandas_table.columns
        )
        markdown_lines = pandas_table.to_markdown(index=False).split("\n")
        if all_headers_are_digits:
            # Strip the auto-generated integer column header row and its separator.
            # When a table has no semantic headers, pandas assigns integer column
            # names (0, 1, 2, ...).  The first data row is the real visual header
            # of the SEC filing table, so promote it and add a divider beneath it
            # to produce a valid Markdown table.
            data_lines = markdown_lines[2:]
            if data_lines:
                first_row = data_lines[0]
                parts = first_row.split("|")
                divider = "|" + "|".join(
                    "-" * max(1, len(p)) for p in parts[1:-1]
                ) + "|"
                markdown_lines = [first_row, divider] + data_lines[1:]
            else:
                markdown_lines = data_lines
        elif "---" in markdown_lines[1]:
            markdown_lines[1] = re.sub(r":?---+:?", "---", markdown_lines[1])
        return re.sub(
            r" +",
            " ",
            "\n".join(markdown_lines),
        )
