from enum import Enum

import rich.traceback
import streamlit as st
import streamlit_antd_components as sac

import dev_utils.dashboard_app.streamlit_utils as st_utils
from dev_utils.core.config import get_config
from dev_utils.dashboard_app.constants import example_queries_items
from dev_utils.dashboard_app.select_reports import render_select_reports
from dev_utils.dashboard_app.view_parsed.view_parsed import render_view_parsed

rich.traceback.install()

###################
### Page config ###
###################

st_utils.st_expander_allow_nested()
st.set_page_config(
    page_icon="🏦",
    page_title="Dasboard App",
    initial_sidebar_state="expanded",
    layout="wide",
)
st_utils.st_multiselect_allow_long_titles()
st_utils.st_change_decoration_color()
st_utils.st_remove_top_page_margin()

###################
### Persistence ###
###################

url_params_queries = st.experimental_get_query_params().get("q", [])

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

############
### Menu ###
############


class NavbarItems(Enum):
    SELECT_REPORTS = 0
    VIEW_PARSED = 1

    @classmethod
    def get_items(cls):
        return [
            sac.SegmentedItem(icon="file-earmark-arrow-down", label="select reports"),
            sac.SegmentedItem(icon="search", label="view parsed"),
        ]


selected_navbar = NavbarItems(
    sac.segmented(
        items=NavbarItems.get_items(),  # type: ignore
        format_func="title",
        align="center",
        return_index=True,
    ),
)

##############
### Runner ###
##############

if selected_navbar == NavbarItems.SELECT_REPORTS:
    render_select_reports()
elif selected_navbar == NavbarItems.VIEW_PARSED:
    render_view_parsed()

##############
### Footer ###
##############

footer = f"v{get_config().sec_parser_version}"
if not get_config().environment.is_prod:
    footer = f"[{get_config().environment.value}] {footer}"
st.markdown(
    f"""
    <div style="position: fixed; right: 20px; bottom: 10px; width: 100%; text-align: right; color: #aaa;">
        {footer}
    </div>
    """,
    unsafe_allow_html=True,
)
