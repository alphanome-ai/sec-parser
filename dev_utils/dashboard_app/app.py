import contextlib
from enum import Enum, auto
from urllib.parse import urlencode

import rich.traceback
import streamlit as st
import streamlit_antd_components as sac

import dev_utils.dashboard_app.streamlit_utils as st_utils
from dev_utils.core.config import get_config
from dev_utils.core.sec_edgar_reports_getter import SecEdgarReportsGetter
from dev_utils.dashboard_app.constants import (
    URL_PARAM_KEY_FILTER_BY_TEXT,
    example_queries_items,
)
from dev_utils.dashboard_app.select_reports import render_select_reports
from dev_utils.dashboard_app.view_parsed.view_parsed import render_view_parsed

URL_PARAM_KEY = "p"

rich.traceback.install()
###################
### Page config ###
###################

st_utils.st_expander_allow_nested()
st.set_page_config(
    page_icon="🏦",
    page_title="sec-parser | Dashboard",
    initial_sidebar_state="expanded",
    layout="wide",
)

style, html = st_utils.get_html_replace_menu_with_placeholder_button()
styles = [
    st_utils.get_style_adjust_madewithstreamlit(),
    st_utils.get_style_change_top_page_margin(),
    st_utils.get_style_modify_decoration(),
    st_utils.get_style_multiselect_allow_long_titles(),
    st_utils.get_style_remove_sidebar_top_margin(),
    style,
]
styles = "\n".join(styles)
st.markdown(
    f"""<style>
{styles}
</style>
{html}""",
    unsafe_allow_html=True,
)


###################
### Persistence ###
###################

url_query_params = st.experimental_get_query_params()
url_params_queries = url_query_params.get("q", [])

if "select_reports__queries" not in st.session_state:
    default = ""
    if url_params_queries:
        default = ",".join(url_params_queries)
    st.session_state["select_reports__queries"] = default

if "select_reports__example_queries" not in st.session_state:
    default = [0, 2]
    if url_params_queries:
        default = [
            i for i, k in enumerate(example_queries_items) if k[1] in url_params_queries
        ]
    st.session_state["select_reports__example_queries"] = default

if "view_parsed__filter_by_text" not in st.session_state:
    default = None
    if url_filter_by_text := url_query_params.get(URL_PARAM_KEY_FILTER_BY_TEXT, []):
        default = url_filter_by_text[0]
    st.session_state["view_parsed__filter_by_text"] = default


############
### Menu ###
############


class NavbarItems(Enum):
    SELECT_REPORTS = auto()
    VIEW_PARSED = auto()

    @classmethod
    def get_items(cls):
        return [
            sac.SegmentedItem(icon="file-earmark-arrow-down", label="select reports"),
            sac.SegmentedItem(icon="search", label="view parsed"),
        ]

    def serialize(self):
        return self.name.lower()

    @classmethod
    def deserialize(cls, name: str):
        return NavbarItems[name.upper()]


default_nav_bar_selection = NavbarItems.SELECT_REPORTS.value
try:
    if URL_PARAM_KEY in url_query_params:
        default_nav_bar_selection = NavbarItems.deserialize(
            url_query_params[URL_PARAM_KEY][0]
        ).value
except Exception as e:
    st.toast(
        "An error occurred while parsing the URL for the navigation bar selection.",
        icon="❌",
    )
selected_navbar = NavbarItems(
    1
    + sac.segmented(
        items=NavbarItems.get_items(),  # type: ignore
        format_func="title",
        align="center",
        return_index=True,
        index=default_nav_bar_selection - 1,
    ),
)

##############
### Runner ###
##############

query_elements = None
if selected_navbar == NavbarItems.SELECT_REPORTS:
    query_elements = render_select_reports()
elif selected_navbar == NavbarItems.VIEW_PARSED:
    query_elements = render_view_parsed()

##############
### Footer ###
##############

# this is for metadata queries
metadata_queries = st.session_state.select_reports__queries
metadata_query_list = SecEdgarReportsGetter.raw_query_to_list(metadata_queries)

# this is for URL queries
query_elements = [
    (URL_PARAM_KEY, selected_navbar.serialize()),
    *(query_elements or []),
    *([("q", query) for query in metadata_query_list]),
]
queries = urlencode(query_elements, doseq=True)
st_utils.st_set_url_to_share_link_to_this_page_placeholder_button(f"/?{queries}")

footer = f"v{get_config().sec_parser_version}"
if not get_config().environment.is_prod:
    footer = f"[{get_config().environment.value}] {footer}"
st.markdown(
    f"""
    <div style="position: fixed;
        right: 18px;
        bottom: 8px;
        width: 100%;
        text-align: right;
        color: #eee;">
        {footer}
    </div>
    """,
    unsafe_allow_html=True,
)
