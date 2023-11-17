import re
from collections import Counter
from enum import Enum, auto
from typing import TYPE_CHECKING

import streamlit as st
import streamlit_antd_components as sac

import sec_parser as sp
from dev_utils.core.profiled_parser import get_parsing_output
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

if TYPE_CHECKING:
    from sec_downloader.types import FilingMetadata

    import sec_parser as sp



def render_view_parsed():
    if (
        "select_reports__report_metadatas" not in st.session_state
        or not st.session_state.select_reports__report_metadatas
    ):
        st.error("Please select some reports first.")
        return
    metadatas: list[FilingMetadata] = st.session_state.select_reports__report_metadatas

    # Get elements
    metadata_options = [_format_name(metadata) for metadata in metadatas]
    with st.sidebar:
        st.write("Type text to quickly search and select reports:")
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

    selected_subnavbar = ViewParsedItems(
        1
        + sac.segmented(
            items=ViewParsedItems.get_items(),  # type: ignore
            format_func="title",
            align="center",
            return_index=True,
            size="sm",
        ),
    )

    #################
    ### Sidebar
    #################

    do_show_nested_composite_elements = False
    filtered_elements = elements
    if selected_subnavbar != ViewParsedItems.PERFORMANCE:
        if selected_subnavbar == ViewParsedItems.SEMANTIC_ELEMENTS:
            with st.sidebar:
                do_show_nested_composite_elements = st.checkbox(
                    "Show Composite Elements",
                    help="Check this box to display Composite Elements. "
                    "Composite Elements act as containers for other semantic elements, "
                    "especially useful when a single HTML root tag wraps multiple elements. "
                    "This ensures structural integrity and enables features like semantic segmentation visualization, "
                    "and debugging by comparison with the original document.",
                )
        if not do_show_nested_composite_elements:
            unwrapped_elements = CompositeSemanticElement.unwrap_elements(elements)
            with st.sidebar:
                element_type_counts = Counter(
                    type(element) for element in unwrapped_elements
                )
                element_type_options = sorted(
                    [
                        (element_type, count, f"{count}x {element_type.__name__}")
                        for element_type, count in element_type_counts.items()
                    ],
                    key=lambda x: x[1],
                    reverse=True,
                )
                default = [
                    k[2]
                    for k in element_type_options
                    if (
                        not issubclass(k[0], sp.IrrelevantElement)
                        or selected_subnavbar == ViewParsedItems.OVERLAY
                    )
                ]
                options = [k[2] for k in element_type_options]
                filter_by_element_type_selection = st.multiselect(
                    label=f"Filter parsed ({round(int(parsing_output.result.parse_time * 1000), -1)} ms) Semantic Element types"
                    if parsing_output.result.parse_time < 1
                    else f"Filter parsed ({parsing_output.result.parse_time:.2f} s) Semantic Element types",
                    options=options,
                    default=default,
                    placeholder="Hiding all elements.",
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
                filter_by_element_text = st.text_input(
                    label=f"Search {len(unwrapped_elements)} elements containing:",
                    placeholder="Showing all elements.",
                )
                include_html_in_text_search = st.checkbox(
                    "Include HTML in text search",
                    help="Check this box to include HTML source code in the text search.",
                )
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
                if selected_subnavbar != ViewParsedItems.SEMANTIC_TREE:
                    filtered_elements = [
                        k
                        for k in filtered_elements
                        if not isinstance(k, list)  # skipped elements are put in lists
                    ]

    #################
    ### Runner
    #################
    if selected_subnavbar == ViewParsedItems.OVERLAY:
        render_view_parsed_overlay(filtered_elements, metadata.primary_doc_url)
    elif selected_subnavbar == ViewParsedItems.PERFORMANCE:
        render_view_parsed_performance(
            parsing_output,
            _format_name(metadata, filename=True),
        )
    elif selected_subnavbar in (
        ViewParsedItems.SEMANTIC_ELEMENTS,
        ViewParsedItems.SEMANTIC_TREE,
    ):
        if selected_subnavbar == ViewParsedItems.SEMANTIC_TREE:
            tree = sp.TreeBuilder().build(filtered_elements)
            render_view_parsed_semantic_elements(
                tree,
                do_show_nested_composite_elements,
            )
        else:
            render_view_parsed_semantic_elements(
                filtered_elements,
                do_show_nested_composite_elements,
            )
    elif selected_subnavbar == ViewParsedItems.EXPORT_AS:
        render_view_parsed_export_as(
            filtered_elements,
            parsing_output.html,
            _format_name(metadata, filename=True),
        )


def _format_name(metadata, *, filename=False):
    name = f"{metadata.form_type} | {metadata.company_name.title()} | {metadata.report_date} | CIK={metadata.cik} | {metadata.accession_number}{' | ' + metadata.items.title() if metadata.items else ''}"
    if filename:
        name = re.sub("[^0-9a-zA-Z-_]", "-", name.replace(" | ", "_"))
    return name

