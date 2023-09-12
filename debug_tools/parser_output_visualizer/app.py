import streamlit as st
from _ui import (
    st_hide_streamlit_element,
    SecApiIoApiKeyGetter,
    st_display_html,
    st_radio,
)
from _sec_parser import (
    download_html_from_ticker,
    download_html_from_url,
)
from dotenv import load_dotenv

load_dotenv()


st.set_page_config(
    page_icon="🏦",
    page_title="SEC Parser Output Visualizer",
    layout="wide",
    initial_sidebar_state="expanded",
)
st_hide_streamlit_element("class", "stDeployButton")

with st.sidebar:
    st.write("# Download Report")
    sec_api_io_key_getter = SecApiIoApiKeyGetter(st.container())

    data_source_options = [
        "Find Latest by Ticker",
        "Enter SEC EDGAR URL",
    ]
    ticker, url = st_radio("Select 10-Q Report Data Source", data_source_options)
    if ticker:
        ticker = st.text_input(
            label="Find Latest by Ticker",
            value="AAPL",
        )
    else:
        url = st.text_input(
            label="Enter SEC EDGAR URL",
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


with st.expander("Hello World", expanded=True):
    st.write("Hello world!")

st_display_html(html)
