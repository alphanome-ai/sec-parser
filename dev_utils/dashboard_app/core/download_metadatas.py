import streamlit as st

from dev_utils.core.sec_edgar_reports_getter import (
    SecEdgarReportsGetter,
    get_filing_metadatas,
)


def global_get_report_metadatas():
    queries = st.session_state.select_reports__queries
    query_list = SecEdgarReportsGetter.raw_query_to_list(queries)
    report_metadatas = []
    for query in query_list:
        new_reports = get_filing_metadatas(query)
        report_metadatas.extend(new_reports)
    st.session_state.select_reports__report_metadatas = report_metadatas
    return query_list, report_metadatas
