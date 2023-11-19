from typing import TYPE_CHECKING

import bs4
import streamlit as st
import streamlit_antd_components as sac
from streamlit_extras import add_vertical_space as avs

import sec_parser as sp
from dev_utils.dashboard_app.streamlit_utils import st_divider

########################
### Constants
########################

PARENT_EXTRA_STYLE = {
    "position": "relative",
    "width": "100%",
}
TRANSPARENT_EXTRA_STYLE = {
    "position": "absolute",
    "top": 0,
    "left": 0,
    "width": "100%",
    "height": "100%",
    "z-index": 10,
}
COLOR_PAIR = [
    (sp.TopLevelSectionTitle, "rgba(247, 217, 196, 0.7)"),
    (sp.TitleElement, "rgba(250, 237, 203, 0.7)"),
    (sp.TextElement, "rgba(201, 228, 222, 0.7)"),
    (sp.ImageElement, "rgba(198, 222, 241, 0.7)"),
    (sp.IrrelevantElement, "rgba(219, 205, 240, 0.7)"),
    (sp.TableElement, "rgba(242, 198, 222, 0.7)"),
    (sp.SupplementaryText, "rgba(255, 192, 203, 0.7)"),
]
COLORING_COVER_TEMPLATE = """
<div style="position: relative;width: 100%">
    {real_tag}
    <div style="position: absolute;top: 0;left: 0;width: 100%;height: 100%;z-index: 10;background-color: {bg_color}">
    </div>
</div>
"""

########################
### Utils
########################


def _get_bg_color_with_element(element: sp.AbstractSemanticElement):
    for element_type, color in COLOR_PAIR:
        if isinstance(element, element_type):
            return color
    return None


def _get_bs4_tag(element: sp.AbstractSemanticElement | sp.TreeNode) -> bs4.Tag:
    if isinstance(element, sp.TreeNode):
        return _get_bs4_tag(element.semantic_element)

    return getattr(element.html_tag, "_bs4", None)


def _get_root_soup(
    element: bs4.BeautifulSoup
    | bs4.Tag
    | sp.HtmlTag
    | sp.AbstractSemanticElement
    | sp.TreeNode,
):
    if isinstance(element, sp.TreeNode):
        return _get_root_soup(element.semantic_element)

    if isinstance(element, sp.AbstractSemanticElement):
        root = _get_root_soup(element.html_tag)
        return root

    if isinstance(element, sp.HtmlTag):
        return _get_root_soup(getattr(element, "_bs4"))

    if element.parent is not None:
        return _get_root_soup(element.parent)

    if not isinstance(element, bs4.BeautifulSoup):
        return None

    return element


def _assign_extra_style(tag: bs4.Tag, extra_style: dict):
    extra_style_string = "; ".join(
        f"{key}: {value}" for key, value in extra_style.items()
    )
    org_style = tag.get("style", "")
    new_style = f"{org_style}; {extra_style_string}"
    tag["style"] = new_style


def _is_table_element(element: sp.AbstractSemanticElement):
    if isinstance(element, sp.TableElement):
        return True
    return False


########################
### Main
########################


def _simple_coloring(
    element: sp.AbstractSemanticElement,
) -> str:
    bg_color = _get_bg_color_with_element(element)

    if bg_color is None:
        return element.get_source_code()

    if not _is_table_element(element):
        bs4_tag = _get_bs4_tag(element)
        _assign_extra_style(
            bs4_tag,
            {
                "background-color": bg_color,
            },
        )
        return bs4_tag.prettify()

    src_code = COLORING_COVER_TEMPLATE.format(
        real_tag=element.get_source_code(), bg_color=bg_color
    )
    return src_code


def _coloring_by_keeping_structure(
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

    bs4_tag = _get_bs4_tag(element)
    bg_color = _get_bg_color_with_element(element)

    if not _is_table_element(element):
        if bs4_tag.parent is None:
            return element
        _assign_extra_style(
            bs4_tag, {"background-color": bg_color, "type": str(element)}
        )
        return element

    transparent_extra_style = {
        **TRANSPARENT_EXTRA_STYLE,
        "background-color": bg_color,
    }

    parent_div = root.new_tag("div")
    transparent_div = root.new_tag("div")

    _assign_extra_style(parent_div, PARENT_EXTRA_STYLE)
    _assign_extra_style(transparent_div, transparent_extra_style)

    bs4_tag.replace_with(parent_div)

    parent_div.append(bs4_tag)
    parent_div.append(transparent_div)

    return element


def _get_root_soup(
    element: bs4.BeautifulSoup
    | bs4.Tag
    | sp.HtmlTag
    | sp.AbstractSemanticElement
    | sp.TreeNode,
):
    if isinstance(element, sp.TreeNode):
        return _get_root_soup(element.semantic_element)

    if isinstance(element, sp.AbstractSemanticElement):
        root = _get_root_soup(element.html_tag)
        return root

    if isinstance(element, sp.HtmlTag):
        return _get_root_soup(getattr(element, "_bs4"))

    if hasattr(element, "parent") and element.parent is not None:
        return _get_root_soup(element.parent)

    if not isinstance(element, bs4.BeautifulSoup):
        return None

    return element


def _extract_root_and_tree(elements):
    root_soup = None
    for element in elements:
        root = _get_root_soup(element)
        if root is None:
            continue
        root_soup = root
    return root_soup, elements


def _visualize_html(elements, keep_structure: bool = False) -> str:
    root, elements = _extract_root_and_tree(elements)
    if keep_structure:
        for element in elements:
            _coloring_by_keeping_structure(root, element)
        return root.prettify()

    colored_code = "\n".join(map(_simple_coloring, elements))
    return colored_code


def render_view_parsed_overlay(elements, original_document_url):
    visualized_html = _visualize_html(elements)

    st_divider("Report with Overlay", "file-earmark-check")
    st.markdown(visualized_html, unsafe_allow_html=True)

    with st.sidebar:
        # avs.add_vertical_space(1)
        html_content = []
        html_content.append(
            "<div style='font-weight: bold; text-align: center; padding: 2px;'>Color Legend</div>"
        )
        for element_type, color in COLOR_PAIR:
            html_content.append(
                f"<div style='background-color: {color};text-align: center; padding: 2px;'>{element_type.__name__}</div>"
            )
        st.markdown("\n".join(html_content), unsafe_allow_html=True)
