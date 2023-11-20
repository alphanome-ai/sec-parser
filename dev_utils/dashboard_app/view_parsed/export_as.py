import re
from io import StringIO

import bs4
import nbformat
import pandas as pd
import streamlit as st
import tiktoken
from millify import millify
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

import sec_parser as sp
from dev_utils.core.config import get_config
from dev_utils.dashboard_app.streamlit_utils import st_divider

GPT4_ENCODING = "cl100k_base"


def render_view_parsed_export_as(elements, html: bytes, filename: str):
    filename_with_version = f"{filename}_{get_config().sec_parser_version}"

    st.markdown("Here you can download the original HTML document.")
    st.download_button(
        label=f"Download Original HTML",
        data=html,
        file_name=f"{filename}.html",
        mime="text/html",
    )

    title_level_to_markdown = _get_map_title_levels_to_markdown_headings(elements)
    output = []
    for element in elements:
        if isinstance(element, sp.TopLevelSectionTitle):
            output.append(f"# {element.text}")
        elif isinstance(element, sp.TextElement):
            output.append(f"{element.text}")
        elif isinstance(element, sp.TitleElement):
            output.append(f"{title_level_to_markdown[element.level]} {element.text}")
        elif isinstance(element, sp.TableElement):
            unmerged_html: str = _unmerge_cells(element.get_source_code())
            output.append(_html_to_pandas(unmerged_html))

    nb = new_notebook()
    nb.cells.append(new_code_cell("import pandas as pd\nfrom numpy import nan\n"))
    for k in output:
        if isinstance(k, pd.DataFrame):
            nb.cells.append(
                new_code_cell(f"pd.DataFrame({k.to_dict()})"),
            )
        else:
            nb.cells.append(new_markdown_cell(k))

    markdown_output = []
    for k in output:
        if isinstance(k, pd.DataFrame):
            markdown_output.append(_pandas_to_markdown(k))
        else:
            markdown_output.append(k)
    markdown_text = "\n\n".join(markdown_output)

    html_tokens = num_tokens_from_string(html.decode("utf-8"))
    markdown_tokens = num_tokens_from_string(markdown_text)
    saved_tokens = html_tokens - markdown_tokens
    saved_percentage = (saved_tokens / html_tokens) * 100

    st.markdown(
        f"The original HTML document contains approximately {millify(html_tokens)} GPT-4 tokens. The converted Markdown version contains {millify(markdown_tokens)} GPT-4 tokens, reducing the token count by approximately {millify(saved_tokens)} ({saved_percentage:.2f}%)."
    )

    st.markdown(
        "For accurate interpretation when using Language Learning Models (LLMs) like ChatGPT with tables, please ensure to include the following text at the beginning of your LLM prompt."
    )
    st.code(
        "Header Rule for All Tables: If a column header is empty, assume it is part of the same data group as the last non-empty header cell to its right. Apply this rule to all following tables.",
        language="text",
    )

    st.download_button(
        label="Download Markdown",
        data=markdown_text.encode("utf-8"),
        file_name=f"{filename_with_version}.txt",
        mime="text/markdown",
    )

    st.markdown(
        "In the Jupyter notebook, tables are encoded in pandas DataFrame format for better manipulation."
    )
    st.download_button(
        label="Download Jupyter Notebook",
        data=nbformat.writes(nb).encode("utf-8"),
        file_name=f"{filename_with_version}.ipynb",
        mime="application/x-ipynb+json",
    )

    st_divider("Markdown Preview", "file-earmark-check")
    st.code(markdown_text, language="text")


def _get_map_title_levels_to_markdown_headings(elements, base_heading_level=2):
    levels = sorted(
        {k.level for k in elements if isinstance(k, sp.TitleElement)},
    )
    adjusted_levels = [level - min(levels) + base_heading_level for level in levels]
    return {
        level: "#" * adjusted_level
        for level, adjusted_level in zip(levels, adjusted_levels)
    }


def num_tokens_from_string(string: str, encoding_name: str = GPT4_ENCODING) -> int:
    return len(tiktoken.get_encoding(encoding_name).encode(string))


def _unmerge_cells(html: str) -> str:
    soup = bs4.BeautifulSoup(html, "lxml")
    assert soup is not None, "No table found."
    assert isinstance(soup, bs4.Tag), "Expected a bs4.Tag."
    for td in soup.find_all("td"):
        if td.has_attr("colspan"):
            for _ in range(int(td["colspan"]) - 1):
                new_td = soup.new_tag("td")
                new_td.string = "NaN"
                td.insert_before(new_td)
            td["colspan"] = 1
    return str(soup)


def _pandas_to_markdown(df):
    df = df.fillna("")
    markdown_table = "\n".join(df.to_markdown(index=False).split("\n")[2:])
    markdown_table = re.sub(r" +", " ", markdown_table)
    return markdown_table


def _html_to_pandas(html):
    df = pd.read_html(StringIO(html), flavor="lxml")[0]
    df = df.dropna(how="all")
    df = df.dropna(how="all", axis="columns")
    return df
