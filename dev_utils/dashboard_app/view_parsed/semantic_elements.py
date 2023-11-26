from __future__ import annotations

import json
from enum import Enum, auto

import streamlit as st
import streamlit_antd_components as sac

import sec_parser as sp

PAGINATION_OFF = "off"
LARGE_TABLE_ROWS_THRESHOLD = 7
PAGINATION_DISABLE_THRESHOLD = 10
URL_PARAM_KEY_OPEN_ALL_EXPANDERS = "open_all_expanders"
URL_PARAM_KEY_SHOW_FILTERED_OUT = "show_filtered_out"


class ShowSkippedElements(Enum):
    HIDE = auto()
    MINIMAL = auto()
    SHOW = auto()

    @classmethod
    def get_items(cls):
        return ["hide", "minimal", "show"]

    @classmethod
    def from_value(cls, value):
        return ShowSkippedElements(1 + cls.get_items().index(value))


def render_view_parsed_semantic_elements(
    elements: list[sp.AbstractSemanticElement | sp.TreeNode] | sp.SemanticTree,
    do_show_nested_composite_elements: bool,
    are_any_elements_filtered: bool,
):
    url_params = st.experimental_get_query_params()
    new_url_params = []
    pagination_size = None
    do_use_pagination = len(elements) >= PAGINATION_DISABLE_THRESHOLD
    pagination_options = []
    if do_use_pagination:
        pagination_options = [
            n for n in [10, 20, 30, 50, 100, 200, 300, 500] if n <= len(elements)
        ]
        if not pagination_options:
            do_use_pagination = False

    ### checkbox start
    default = False
    value = default
    value_from_url = url_params.get(URL_PARAM_KEY_OPEN_ALL_EXPANDERS, [])
    if value_from_url:
        value_from_url = value_from_url[0] == "1"
        value = value_from_url

    do_open_all_expanders = st.sidebar.checkbox(
        "Open All Expanders",
        value=value,
    )

    if do_open_all_expanders != default:
        new_url_params.append(
            (
                URL_PARAM_KEY_OPEN_ALL_EXPANDERS,
                int(do_open_all_expanders),
            ),
        )
    ### checkbox end
    do_set_visibility_of_filtered_elements = (
        not do_show_nested_composite_elements and are_any_elements_filtered
    )

    column_count = int(do_use_pagination) + int(do_set_visibility_of_filtered_elements)

    i = -1
    columns = []
    if column_count:
        with st.sidebar:
            columns = st.columns(column_count)

    if do_set_visibility_of_filtered_elements:
        i += 1
        with columns[i]:
            default = ShowSkippedElements.get_items()[1]
            value = default
            value_from_url = url_params.get(URL_PARAM_KEY_SHOW_FILTERED_OUT, [])
            if value_from_url:
                value_from_url = value_from_url[0].lower()
                if value_from_url in ShowSkippedElements.get_items():
                    value = value_from_url

            show_skipped_elements_option = st.select_slider(
                "Filtered out elements:",
                ShowSkippedElements.get_items(),
                value=value,
                help="This option determines the visibility of elements that have been filtered out.",
            )
            if show_skipped_elements_option != default:
                new_url_params.append(
                    (
                        URL_PARAM_KEY_SHOW_FILTERED_OUT,
                        show_skipped_elements_option,
                    )
                )
            show_skipped_elements_option = ShowSkippedElements.from_value(
                show_skipped_elements_option,
            )
    else:
        show_skipped_elements_option = ShowSkippedElements.SHOW

    if show_skipped_elements_option == ShowSkippedElements.HIDE:
        elements = [k for k in elements if not isinstance(k, list)]

    if do_use_pagination:
        pagination_options = [
            n for n in [10, 20, 30, 50, 100, 200, 300, 500] if n <= len(elements)
        ]
        if not pagination_options:
            do_use_pagination = False
    if do_use_pagination:
        i += 1
        with columns[i]:
            pagination_size = st.select_slider(
                "Page Size:",
                options=[*pagination_options, PAGINATION_OFF],
                value=pagination_options[0],
                help=(
                    "Set the number of elements displayed per page. "
                    "Use this to improve UI responsiveness. "
                ),
                format_func=lambda x: len(elements) if x == PAGINATION_OFF else x,
            )
            if pagination_size == PAGINATION_OFF:
                do_use_pagination = False

    # assert i == len(columns) - 1, "columns should be exhausted"

    #### PAGINATION START
    if do_use_pagination:
        elements_list = list(elements)
        pagination_size = int(pagination_size)
        total_items = len(elements_list)
        max_value = ((total_items // pagination_size) + 1) if pagination_size else 1
        selected_page = 1
        if max_value == 1:
            st.markdown(
                f"<p style='text-align: center; color: lightgrey;'>Top level elements: {total_items}</p>",
                unsafe_allow_html=True,
            )
        elif max_value > 1:
            # cols = st.columns(3)
            # with cols[1]:
            #     label = f"Choose a page (out of {max_value} total pages)"
            #     selected_page = st.number_input(
            #         label,
            #         min_value=1,
            #         max_value=max_value,
            #         value=1,
            #         step=1,
            #         format="%d",
            #     )

            #     start_item = (selected_page - 1) * pagination_size + 1
            #     end_item = min(selected_page * pagination_size, total_items)
            #     st.markdown(
            #         f"<p style='text-align: center;'>{start_item}-{end_item} / {total_items} items</p>",
            #         unsafe_allow_html=True,
            #     )

            selected_page = sac.pagination(
                total=total_items,
                align="center",
                jump=True,
                show_total=True,
                page_size=pagination_size,
            )
        pagination_start_idx = (selected_page - 1) * pagination_size
        pagination_end_idx = selected_page * pagination_size
        if max_value > 1:
            elements = elements_list[pagination_start_idx:pagination_end_idx]
    #### PAGINATION END

    for element in elements:
        render_element(
            element,
            show_skipped_elements_option,
            do_open_all_expanders,
        )

    return new_url_params


def render_element(
    element: sp.AbstractSemanticElement | sp.TreeNode,
    show_skipped_elements_option,
    do_open_all_expanders,
):
    tree_node = None
    if isinstance(element, sp.TreeNode):
        tree_node = element
        element = element.semantic_element

    is_semantic_tree_node = tree_node is not None and tree_node.children
    is_composite_element = isinstance(element, sp.CompositeSemanticElement)
    is_large_table = (
        isinstance(element, sp.TableElement)
        and element.html_tag.get_approx_table_metrics().rows
        >= LARGE_TABLE_ROWS_THRESHOLD
    )

    if isinstance(element, list):  # skipped elements are put in lists
        skipped_elements_list = element
        if show_skipped_elements_option == ShowSkippedElements.MINIMAL:
            element_count = len(element)
            element_text = "element" if element_count == 1 else "elements"
            st.markdown(
                f'<div align="center" style="color: lightgrey; margin-bottom: 10px;"><span style="font-style: italic;">(filtered out {element_count} {element_text})</span></div>',
                unsafe_allow_html=True,
            )
        if show_skipped_elements_option == ShowSkippedElements.SHOW:
            with st.expander(
                f"*------------- {len(element)} skipped -------------*",
                expanded=do_open_all_expanders,
            ):
                for skipped_element in skipped_elements_list:
                    render_element(
                        skipped_element,
                        show_skipped_elements_option,
                        do_open_all_expanders,
                    )
        return

    box_name = element.__class__.__name__
    if hasattr(element, "level"):
        box_name += f" (Level {element.level})"

    with st.expander(box_name, expanded=do_open_all_expanders):
        tab_names = []
        if is_composite_element:
            tab_names.append("Inner Elements")
        if not is_semantic_tree_node and not is_large_table:
            tab_names.append("Rendered")
        if is_large_table:
            tab_names.extend(("Summary", "Rendered"))
        if is_semantic_tree_node:
            tab_names.append("Children Elements")

        tab_names.extend(("Source code", "Text", "Processing Log"))

        if not is_large_table and is_semantic_tree_node:
            st.markdown(
                element.get_source_code(enable_compatibility=True),
                unsafe_allow_html=True,
            )

        i = -1
        tabs = st.tabs(tab_names)

        if is_composite_element:
            i += 1
            with tabs[i]:
                for inner_element in element.inner_elements:
                    render_element(
                        inner_element,
                        show_skipped_elements_option,
                        do_open_all_expanders,
                    )

        if not is_semantic_tree_node and not is_large_table:
            i += 1
            with tabs[i]:
                st.markdown(
                    element.get_source_code(enable_compatibility=True),
                    unsafe_allow_html=True,
                )

        if is_large_table:
            i += 1
            with tabs[i]:
                st.write(element.get_summary())
            i += 1
            with tabs[i]:
                st.markdown(
                    element.get_source_code(enable_compatibility=True),
                    unsafe_allow_html=True,
                )

        if is_semantic_tree_node:
            i += 1
            with tabs[i]:
                for c in tree_node.children:
                    render_element(
                        c,
                        show_skipped_elements_option,
                        do_open_all_expanders,
                    )

        i += 1
        with tabs[i]:
            st.code(element.get_source_code(pretty=True), language="text")

        i += 1
        with tabs[i]:
            st.code(element.text, language="text")

        i += 1
        with tabs[i]:
            output = ""
            processing_log = element.processing_log.get_items()
            for item in processing_log:
                payload: str = ""
                if isinstance(item.payload, dict):
                    obj_json = json.dumps(
                        item.payload,
                        indent=4,
                    )
                    payload = f"Created element {obj_json}"
                else:
                    payload = str(item.payload)
                output += f"{item.origin}: {payload}\n"
            st.code(output, language="text")

        assert i == len(tabs) - 1, "tabs should be exhausted"
