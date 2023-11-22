import streamlit_antd_components as sac

example_queries_items = [
    (sac.ChipItem(icon="apple", label="Latest apple 10-Q"), "AAPL"),
    (sac.ChipItem(icon="google", label="Two Latest alphabet 10-Q"), "2/GOOG"),
    (
        sac.ChipItem(icon="microsoft", label="Microsoft 10-Q April 2023"),
        "MSFT/0000950170-23-014423",
    ),
    (
        sac.ChipItem(icon="facebook", label="Meta 10-Q April 2019"),
        "https://www.sec.gov/Archives/edgar/data/1326801/000132680119000037/fb-03312019x10q.htm",
    ),
]

URL_PARAM_KEY_FILTER_BY_TEXT = "filter_by_text"
