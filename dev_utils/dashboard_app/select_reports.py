from __future__ import annotations

from urllib.parse import urlencode

import streamlit as st
import streamlit_antd_components as sac

import dev_utils.dashboard_app.streamlit_utils as st_utils
from dev_utils.core.sec_edgar_reports_getter import SecEdgarReportsGetter
from dev_utils.dashboard_app.constants import example_queries_items
from dev_utils.dashboard_app.core.download_metadatas import global_get_report_metadatas
from dev_utils.dashboard_app.python_utils import smart_join


def render_select_reports():
    st.markdown(
        """
        <div style="text-align: right;">
            <a href="https://discord.gg/2MC3uJhBxs"><img alt="Discord" src="https://img.shields.io/discord/1164249739836018698?logo=discord&logoColor=white&style=flat&color=white&labelColor=767FA6"></a>
            <a href="https://github.com/alphanome-ai/sec-parser"><img src="https://img.shields.io/github/stars/alphanome-ai/sec-parser.svg?style=social&label=Star us on GitHub!" alt="GitHub stars"></a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    class OnChangeHandler:
        def __init__(self, key):
            self.key = key

        def __call__(self, value):
            if isinstance(value, list):
                if len(value) >= 2 and 0 in value and value[0] != 0:
                    return [0]  # [v for v in value if v != 0]
                if len(value) >= 2 and value[0] == 0:
                    return [v for v in value if v != 0]
                elif len(value) == 0:
                    return [0]
            return value

    handler = OnChangeHandler("actual")
    st_utils.st_unkeep("select_reports__example_queries")
    selected_example_queries = handler(
        sac.chip(
            items=[k[0] for k in example_queries_items],
            label="Get started with examples:",
            size="xs",
            format_func="title",
            align="start",
            index=st.session_state.select_reports__example_queries,
            variant="outline",
            multiple=True,
            return_index=True,
            key="_select_reports__example_queries",
            on_change=lambda: st_utils.st_keep(
                "select_reports__example_queries",
                handler,
            ),
        ),
    )
    avoidlist = [
        k[1]
        for i, k in enumerate(example_queries_items)
        if i not in selected_example_queries
    ]
    addlist = [
        example_queries_items[i][1]
        for i in selected_example_queries
        if example_queries_items[i][1]
    ]

    current = [
        k
        for k in SecEdgarReportsGetter.raw_query_to_list(
            st.session_state.select_reports__queries,
        )
        if k not in avoidlist
    ]

    to_add = [k for k in addlist if k not in current]
    current.extend(to_add)
    queries = smart_join(current, max_length=50)

    st.session_state.select_reports__queries = queries
    st_utils.st_unkeep("select_reports__queries")
    queries = st.text_area(
        "Enter your [queries](https://github.com/Elijas/sec-downloader) separated by commas and/or newlines:",
        key="_select_reports__queries",
        on_change=lambda: st_utils.st_keep("select_reports__queries"),
    )

    query_list, report_metadatas = global_get_report_metadatas()

    if any(m.form_type != "10-Q" for m in report_metadatas):
        st.warning(
            "**Warning:** Only 10-Q form types are supported at this time. Parsing other form types may lead to unexpected results.",
        )
    table_container = st.empty()
    if report_metadatas:
        reports_dict_list = SecEdgarReportsGetter.to_dict_list(report_metadatas)
        table_container.dataframe(reports_dict_list, use_container_width=False)

    st.session_state.select_reports__report_metadatas = report_metadatas

    query_elements = [("q", query) for query in query_list]
    queries = urlencode(query_elements, doseq=True)

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
