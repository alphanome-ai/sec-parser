import streamlit as st
from _ui import (
    st_hide_streamlit_element,
    SecApiIoApiKeyGetter,
    st_radio,
)
from _sec_parser import (
    download_html_from_ticker,
    download_html_from_url,
)
from _utils import remove_ix_tags
from dotenv import load_dotenv
import streamlit_antd_components as sac

load_dotenv()


st.set_page_config(
    page_icon="🏦",
    page_title="SEC Parser Output Visualizer",
    layout="centered",
    initial_sidebar_state="expanded",
)
st_hide_streamlit_element("class", "stDeployButton")

with st.sidebar:
    st.write("# Download Report")
    sec_api_io_key_getter = SecApiIoApiKeyGetter(st.container())

    data_source_options = [
        "Select Ticker to Find Latest",
        "Enter Ticker to Find Latest",
        "Enter SEC EDGAR URL",
    ]
    select_ticker, find_ticker, url = st_radio(
        "Select 10-Q Report Data Source", data_source_options
    )
    ticker, url = None, None
    if select_ticker:
        ticker = st.selectbox(
            label="Select Ticker",
            options=["AAPL", "GOOG"],
        )
    elif find_ticker:
        ticker = st.text_input(
            label="Enter Ticker",
            value="AAPL",
        )
    else:
        url = st.text_input(
            label="Enter URL",
            value="https://www.sec.gov/Archives/edgar/data/320193/000032019323000077/aapl-20230701.htm",
        )

    section_1_2, all_sections = st_radio(
        "Select 10-Q Sections", ["Only MD&A", "All Sections"], horizontal=True
    )
    if section_1_2:
        sections = ["part1item2"]
    else:
        sections = None


if ticker:
    html = download_html_from_ticker(
        sec_api_io_key_getter, doc="10-Q", ticker=ticker, sections=sections
    )
else:
    html = download_html_from_url(
        sec_api_io_key_getter, doc="10-Q", url=url, sections=sections
    )

view_step_options = [
    "Original From SEC EDGAR",
    "Parsed Semantic Elements",
    "Nested Semantic Tree",
]
selected_step = 1 + sac.steps(
    [
        sac.StepsItem(
            title=k.partition(" ")[0],
            description=k.partition(" ")[2],
        )
        for k in view_step_options
    ],
    index=0,
    format_func=None,
    placement="horizontal",
    size="default",
    direction="horizontal",
    type="default",  # default, navigation
    dot=False,
    return_index=True,
)
if selected_step == 1:
    st.markdown(remove_ix_tags(html), unsafe_allow_html=True)
