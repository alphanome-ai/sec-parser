from pathlib import Path
from typing import Callable

import bs4
import requests
import streamlit as st

import sec_parser as sp
from dev_utils.semantic_visualization.const import *
from dev_utils.semantic_visualization.sp_utils import *


def simple_coloring(
    element: sp.AbstractSemanticElement,
) -> str:
    bg_color = get_bg_color_with_element(element)

    if bg_color is None:
        return element.get_source_code()

    if not is_table_element(element):
        bs4_tag = get_bs4_tag(element)
        assign_extra_style(
            bs4_tag,
            {
                'background-color': bg_color,
            },
        )
        return bs4_tag.prettify()

    src_code = COLORING_COVER_TEMPLATE.format(real_tag=element.get_source_code(), bg_color=bg_color)
    return src_code


def coloring_by_keeping_structure(
    root: bs4.BeautifulSoup,
    element: sp.AbstractSemanticElement,
) -> sp.AbstractSemanticElement:
    ignore_types = [
        sp.EmptyElement,
        sp.NotYetClassifiedElement,
    ]

    for ignore_type in ignore_types:
        if isinstance(element, ignore_type):
            return element

    bs4_tag = get_bs4_tag(element)
    bg_color = get_bg_color_with_element(element)

    if not is_table_element(element):
        if bs4_tag.parent is None:
            return element
        else:
            assign_extra_style(
                bs4_tag,
                {
                    "background-color": bg_color,
                    "type": str(element)
                }
            )
        return element

    transparent_extra_style = {
        **TRANSPARENT_EXTRA_STYLE,
        'background-color': bg_color,
    }

    parent_div = root.new_tag("div")
    transparent_div = root.new_tag("div")

    assign_extra_style(parent_div, PARENT_EXTRA_STYLE)
    assign_extra_style(transparent_div, transparent_extra_style)

    bs4_tag.replace_with(parent_div)

    parent_div.append(bs4_tag)
    parent_div.append(transparent_div)

    return element


def visualize_html(html: Path | str, keep_structure: bool = False) -> str:
    root, elements, _ = extract_root_and_tree(html)
    if keep_structure:
        for element in elements:
            coloring_by_keeping_structure(root, element)
        return root.prettify()

    colored_code = '\n'.join(map(simple_coloring, elements))
    return colored_code


@st.cache
def get_html(url):
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    return res.text


def fetch_html():
    def wrapper(url, callback: Callable[[object | None, str | None], None] | None):
        try:
            html = get_html(url)
            if callback:
                callback(None, html)
            return html
        except (
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
        ) as e:
            if callback is None:
                raise
            callback(e, None)
    return wrapper


def process_html(html: str) -> str:

    return visualize_html(html)


def main():
    st.set_page_config(layout="wide")

    url = st.text_input('Enter the target URL')

    btn_load = st.button('Load & Visualize')

    st.markdown("<style>.stTextInput>div>div>input { align-items: flex-end; }</style>", unsafe_allow_html=True)

    html_component = st.empty()

    if btn_load:
        html_content = fetch_html()(url, None)
        visualized_html = visualize_html(html_content)
        html_component.markdown(visualized_html, unsafe_allow_html=True)


if __name__ == '__main__':
    main()
