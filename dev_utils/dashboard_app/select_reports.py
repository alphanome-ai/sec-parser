from urllib.parse import urlencode

import streamlit as st
import streamlit_antd_components as sac

import dev_utils.dashboard_app.streamlit_utils as st_utils
from dev_utils.core.sec_edgar_reports_getter import (
    SecEdgarReportsGetter,
    get_filing_metadatas,
)
from dev_utils.dashboard_app.constants import example_queries_items
from dev_utils.dashboard_app.python_utils import smart_join


def render_select_reports():
    st_utils.st_unkeep("select_reports__example_queries")
    selected_example_queries = sac.chip(
        items=[k[0] for k in example_queries_items],
        label="Get Started with Examples",
        size="xs",
        format_func="title",
        align="start",
        index=st.session_state.select_reports__example_queries,
        variant="outline",
        multiple=True,
        return_index=True,
        key="_select_reports__example_queries",
        on_change=lambda: st_utils.st_keep("select_reports__example_queries"),
    )

    avoidlist = [
        k[1]
        for i, k in enumerate(example_queries_items)
        if i not in selected_example_queries
    ]
    addlist = [example_queries_items[i][1] for i in selected_example_queries]

    current = [
        k
        for k in SecEdgarReportsGetter.raw_query_to_list(
            st.session_state.select_reports__queries,
        )
        if k not in avoidlist
    ]

    to_add = [k for k in addlist if k not in current]
    current.extend(to_add)
    st.session_state.select_reports__queries = smart_join(current)
    st_utils.st_unkeep("select_reports__queries")
    queries = st.text_area(
        "Enter your queries separated by commas and/or newlines:",
        key="_select_reports__queries",
        on_change=lambda: st_utils.st_keep("select_reports__queries"),
    )

    query_list = SecEdgarReportsGetter.raw_query_to_list(queries)

    reports = []
    table_container = st.empty()
    for query in query_list:
        new_reports = get_filing_metadatas(query)
        reports.extend(new_reports)
    if reports:
        reports_dict_list = SecEdgarReportsGetter.to_dict_list(reports)
        table_container.dataframe(reports_dict_list, use_container_width=False)

    st.session_state.select_reports__report_metadatas = reports

    queries = urlencode([("q", query) for query in query_list], doseq=True)

    if query_list:
        sac.buttons(
            [
                sac.ButtonsItem(label="share", icon="share-fill", href=f"/?{queries}"),
            ],
            format_func="title",
            align="center",
            index=-1,
            compact=True,
        )
