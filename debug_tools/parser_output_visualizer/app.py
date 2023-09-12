from collections import Counter
import random
import streamlit as st
from _ui import (
    st_hide_streamlit_element,
    SecApiIoApiKeyGetter,
    st_radio,
    st_multiselect_allow_long_titles,
)
from _sec_parser import (
    download_html_from_ticker,
    download_html_from_url,
    get_semantic_elements,
    get_semantic_tree,
)
from _utils import remove_ix_tags, add_spaces
from dotenv import load_dotenv
import streamlit_antd_components as sac
import sec_parser as sp

load_dotenv()


st.set_page_config(
    page_icon="🏦",
    page_title="SEC Parser Output Visualizer",
    layout="centered",
    initial_sidebar_state="expanded",
)
st_hide_streamlit_element("class", "stDeployButton")
st_multiselect_allow_long_titles()

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
    index=1,
    format_func=None,
    placement="horizontal",
    size="default",
    direction="horizontal",
    type="default",  # default, navigation
    dot=False,
    return_index=True,
)


def get_pretty_class_name(element_cls):
    def get_emoji(cls):
        return {
            sp.UnclaimedElement: "🍃",
        }.get(
            cls, "✨"
        )  # star

    emoji = get_emoji(element_cls)
    class_name = f"**{add_spaces(element_cls.__name__)}**"
    pretty_name = f"{emoji} {class_name}"
    return pretty_name


if selected_step > 1:
    elements = get_semantic_elements(html)
    with st.sidebar:
        st.write("# Semantic Elements")
        do_element_render_html = st.checkbox("Render HTML", value=True)
        do_expand_all = st.checkbox("Expand All", value=False)

        counted_element_types = Counter(element.__class__ for element in elements)
        selected_types = st.multiselect(
            "Filter Element Types",
            counted_element_types.keys(),
            counted_element_types.keys(),
            format_func=lambda cls: f'{counted_element_types[cls]}x {get_pretty_class_name(cls).replace("*","")}',
        )
        elements = [e for e in elements if e.__class__ in selected_types]


if selected_step > 2:
    tree = get_semantic_tree(elements)


if selected_step == 1:
    st.markdown(remove_ix_tags(html), unsafe_allow_html=True)
if selected_step == 2:
    for element in elements:
        with st.expander(
            get_pretty_class_name(element.__class__), expanded=do_expand_all
        ):
            bs4_tag = element.html_tag.bs4
            if do_element_render_html:
                element_html = remove_ix_tags(str(bs4_tag))
                st.markdown(element_html, unsafe_allow_html=True)
            else:
                st.code(bs4_tag.prettify(), language="html")
