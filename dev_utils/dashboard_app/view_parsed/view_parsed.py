import re
from collections import Counter
from enum import Enum, auto
from typing import TYPE_CHECKING

import streamlit as st
import streamlit_antd_components as sac

import dev_utils.dashboard_app.streamlit_utils as st_utils
import sec_parser as sp
from dev_utils.core.profiled_parser import get_parsing_output
from dev_utils.dashboard_app.constants import URL_PARAM_KEY_FILTER_BY_TEXT
from dev_utils.dashboard_app.core.download_metadatas import global_get_report_metadatas
from dev_utils.dashboard_app.view_parsed._utils import aggregate_skipped_elements
from dev_utils.dashboard_app.view_parsed.export_as import render_view_parsed_export_as
from dev_utils.dashboard_app.view_parsed.overlay import render_view_parsed_overlay
from dev_utils.dashboard_app.view_parsed.performance import (
    render_view_parsed_performance,
)
from dev_utils.dashboard_app.view_parsed.semantic_elements import (
    render_view_parsed_semantic_elements,
)
from sec_parser.semantic_elements.composite_semantic_element import (
    CompositeSemanticElement,
)

URL_PARAM_KEY = "view_parsed"
URL_PARAM_KEY_ELEMENT_TYPE = "et"

URL_PARAM_KEY_SHOW_COMPOSITE = "show_composite"
URL_PARAM_KEY_DO_FILTER_BY_HTML = "do_filter_by_html"
if TYPE_CHECKING:
    from sec_downloader.types import FilingMetadata

    import sec_parser as sp


def render_view_parsed():
    global_get_report_metadatas()
    if (
        "select_reports__report_metadatas" not in st.session_state
        or not st.session_state.select_reports__report_metadatas
    ):
        st.error("Please select some reports first.")
        return
    metadatas: list[FilingMetadata] = st.session_state.select_reports__report_metadatas

    url_params = st.experimental_get_query_params()
    new_url_params = []

    #################
    ### Sidebar
    #################
    # Get elements
    metadata_options = [_format_name(metadata) for metadata in metadatas]
    with st.sidebar:
        columns = st.columns([11, 2])
        with columns[0]:
            filter_by_report = st.selectbox(
                ".",
                metadata_options,
                label_visibility="collapsed",
            )

    if not filter_by_report:
        st.info("Please select a report.")
        st.stop()
    assert filter_by_report

    metadata = metadatas[metadata_options.index(filter_by_report)]
    parsing_output = get_parsing_output(metadata.primary_doc_url)
    elements: list[sp.AbstractSemanticElement] = parsing_output.result.elements

    with columns[1]:
        st.link_button("📄", metadata.primary_doc_url)

    #################
    ### Subnavbar
    #################

    class ViewParsedItems(Enum):
        SEMANTIC_ELEMENTS = auto()
        SEMANTIC_TREE = auto()
        PERFORMANCE = auto()
        OVERLAY = auto()
        EXPORT_AS = auto()

        @classmethod
        def get_items(cls):
            return [
                sac.SegmentedItem(icon="view-stacked", label="semantic elements"),
                sac.SegmentedItem(icon="diagram-3", label="semantic tree"),
                sac.SegmentedItem(icon="speedometer2", label="performance"),
                sac.SegmentedItem(icon="layers", label="overlay"),
                sac.SegmentedItem(icon="download", label="export as"),
            ]

        def serialize(self):
            return self.name.lower()

        @classmethod
        def deserialize(cls, name: str):
            return ViewParsedItems[name.upper()]

    url_query_params = st.experimental_get_query_params()
    default_nav_bar_selection = ViewParsedItems.SEMANTIC_ELEMENTS.value
    try:
        if URL_PARAM_KEY in url_query_params:
            default_nav_bar_selection = ViewParsedItems.deserialize(
                url_query_params[URL_PARAM_KEY][0]
            ).value
    except Exception:
        st.toast(
            "Error: Unable to parse the URL for the navigation bar selection.",
            icon="❌",
        )

    selected_subnavbar = ViewParsedItems(
        1
        + sac.segmented(
            items=ViewParsedItems.get_items(),  # type: ignore
            format_func="title",
            align="center",
            return_index=True,
            size="sm",
            index=default_nav_bar_selection - 1,
        ),
    )

    if selected_subnavbar == ViewParsedItems.OVERLAY:
        # Make a copy of the elements to avoid modifying the original
        elements = parsing_output.parser.parse(parsing_output.html)

    #################
    ### Sidebar (continued)
    #################
    are_any_elements_filtered = False
    do_show_nested_composite_elements = False
    filtered_elements = elements
    filter_by_element_type_selection_default = None
    filtered_element_types = None
    is_filtering_enabled = selected_subnavbar != ViewParsedItems.PERFORMANCE
    is_filtering_by_type_enabled = False
    if is_filtering_enabled:
        sidebar_top = st.sidebar.container()
        if selected_subnavbar == ViewParsedItems.SEMANTIC_ELEMENTS:
            default = False
            value = default
            value_from_url = url_params.get(URL_PARAM_KEY_SHOW_COMPOSITE, [])
            if value_from_url:
                value_from_url = value_from_url[0] == "1"
                value = value_from_url

            do_show_nested_composite_elements = st.sidebar.checkbox(
                "Show Composite Elements",
                help="Check this box to display Composite Elements. "
                "Composite Elements act as containers for other semantic elements, "
                "especially useful when a single HTML root tag wraps multiple elements. "
                "This ensures structural integrity and enables features like semantic segmentation visualization, "
                "and debugging by comparison with the original document.",
                value=value,
            )

            if do_show_nested_composite_elements != default:
                new_url_params.append(
                    (
                        URL_PARAM_KEY_SHOW_COMPOSITE,
                        int(do_show_nested_composite_elements),
                    )
                )
        if not do_show_nested_composite_elements:
            is_filtering_by_type_enabled = True
            unwrapped_elements = CompositeSemanticElement.unwrap_elements(elements)
            st_utils.st_unkeep("view_parsed__filter_by_text")
            filter_by_element_text = sidebar_top.text_input(
                label=f"{len(unwrapped_elements)} elements parsed in "
                + (
                    f"{round(int(parsing_output.result.parse_time * 1000), -1)} ms"
                    if parsing_output.result.parse_time < 1
                    else f"{parsing_output.result.parse_time:.2f} s"
                )
                + ". Filter by text:",
                placeholder="Text filter not applied.",
                key="_view_parsed__filter_by_text",
                on_change=lambda: st_utils.st_keep("view_parsed__filter_by_text"),
            )
            if filter_by_element_text:
                new_url_params.append(
                    (URL_PARAM_KEY_FILTER_BY_TEXT, filter_by_element_text)
                )
            element_type_counts = Counter(
                type(element) for element in unwrapped_elements
            )
            element_type_options = sorted(
                [
                    (
                        element_type,
                        count,
                        f"{count}x {element_type.__name__.replace('SemanticElement','').replace('Element','')}",
                    )
                    for element_type, count in element_type_counts.items()
                ],
                key=lambda x: x[1],
                reverse=True,
            )

            url_element_types = url_params.get(URL_PARAM_KEY_ELEMENT_TYPE, [])
            url_element_types = {k.lower() for k in url_element_types}
            filter_by_element_type_selection_default = [
                k
                for k in element_type_options
                if (
                    not issubclass(k[0], sp.IrrelevantElement)
                    or selected_subnavbar == ViewParsedItems.OVERLAY
                )
            ]
            filter_by_element_type_selection_default_str = [
                k[2] for k in filter_by_element_type_selection_default
            ]
            if not url_element_types:
                filter_by_element_type_selection_initial = (
                    filter_by_element_type_selection_default_str
                )
            else:
                filter_by_element_type_selection_initial = [
                    k[2]
                    for k in element_type_options
                    if k[0].__name__.lower() in url_element_types
                ]
            options = [k[2] for k in element_type_options]
            filter_by_element_type_selection = sidebar_top.multiselect(
                label="Filter by type:",
                options=options,
                default=filter_by_element_type_selection_initial,
                placeholder="Select at least one type.",
                help=(
                    "**Semantic Elements** correspond to the semantic elements in SEC EDGAR documents."
                    " A semantic element refers to a meaningful unit within the document that serves a"
                    " specific purpose, such as a paragraph or a table. Unlike syntactic elements,"
                    " which structure the HTML, semantic elements carry vital information for"
                    " understanding the document's content."
                ),
            )
            filtered_element_types = [
                next(k[0] for k in element_type_options if k[2] == selected_type)
                for selected_type in filter_by_element_type_selection
            ]

            ### checkbox start
            default = False
            value = default
            value_from_url = url_params.get(URL_PARAM_KEY_DO_FILTER_BY_HTML, [])
            if value_from_url:
                value_from_url = value_from_url[0] == "1"
                value = value_from_url

            include_html_in_text_search = st.sidebar.checkbox(
                "Include HTML in text search",
                help="Check this box to include HTML source code in the text search.",
                value=value,
            )

            if include_html_in_text_search != default:
                new_url_params.append(
                    (
                        URL_PARAM_KEY_DO_FILTER_BY_HTML,
                        int(include_html_in_text_search),
                    )
                )
            ### checkbox end

            if not filter_by_element_type_selection:
                st.info("Please select at least one element type.")
                st.stop()

            def predicate(element: sp.AbstractSemanticElement):
                return (
                    not filtered_element_types
                    or isinstance(element, tuple(filtered_element_types))
                ) and (
                    not filter_by_element_text
                    or filter_by_element_text
                    in (
                        element.text
                        if not include_html_in_text_search
                        else element.get_source_code()
                    )
                )

            filtered_elements = aggregate_skipped_elements(
                unwrapped_elements,
                predicate,
            )

            if selected_subnavbar == ViewParsedItems.SEMANTIC_ELEMENTS:
                are_any_elements_filtered = len(filtered_elements) != len(
                    unwrapped_elements
                )
            else:
                filtered_elements = [
                    k
                    for k in filtered_elements
                    if not isinstance(k, list)  # skipped elements are put in lists
                ]
                are_any_elements_filtered = False

    #################
    ### Runner
    #################
    query_elements = None
    if selected_subnavbar == ViewParsedItems.OVERLAY:
        query_elements = render_view_parsed_overlay(
            filtered_elements,
            metadata.primary_doc_url,
        )
    elif selected_subnavbar == ViewParsedItems.PERFORMANCE:
        query_elements = render_view_parsed_performance(
            parsing_output,
            _format_name(metadata, filename=True),
        )
    elif selected_subnavbar in (
        ViewParsedItems.SEMANTIC_ELEMENTS,
        ViewParsedItems.SEMANTIC_TREE,
    ):
        if selected_subnavbar in (
            ViewParsedItems.SEMANTIC_TREE,
            ViewParsedItems.SEMANTIC_TREE,
        ):
            tree = sp.TreeBuilder().build(filtered_elements)
            query_elements = render_view_parsed_semantic_elements(
                tree, do_show_nested_composite_elements, are_any_elements_filtered
            )
        else:
            query_elements = render_view_parsed_semantic_elements(
                filtered_elements,
                do_show_nested_composite_elements,
                are_any_elements_filtered,
            )
    elif selected_subnavbar == ViewParsedItems.EXPORT_AS:
        query_elements = render_view_parsed_export_as(
            filtered_elements,
            parsing_output.html,
            _format_name(metadata, filename=True),
        )

    if is_filtering_by_type_enabled:
        assert filter_by_element_type_selection_default and filtered_element_types
        if set(filtered_element_types) != {
            k[0] for k in filter_by_element_type_selection_default
        }:
            new_url_params.extend(
                [
                    (
                        URL_PARAM_KEY_ELEMENT_TYPE,
                        [k.__name__.lower() for k in filtered_element_types],
                    ),
                ]
            )
    return [
        (URL_PARAM_KEY, selected_subnavbar.serialize()),
        *new_url_params,
        *(query_elements or []),
    ]


def _format_name(metadata, *, filename=False):
    name = f"{metadata.form_type} | {metadata.company_name.title()} | {metadata.report_date} | CIK={metadata.cik} | {metadata.accession_number}{' | ' + metadata.items.title() if metadata.items else ''}"
    if filename:
        name = re.sub("[^0-9a-zA-Z-_]", "-", name.replace(" | ", "_"))
    return name
