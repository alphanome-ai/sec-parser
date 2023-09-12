import os
import streamlit as st
from _utils import generate_bool_list


def st_hide_streamlit_element(key: str, value: str):
    st.markdown(
        f"""
            <style>
                div[{key}="{value}"] {{
                    visibility: hidden;
                    height: 0%;
                    position: fixed;
                }}
            </style>
        """,
        unsafe_allow_html=True,
    )


class SecApiIoApiKeyGetter:
    def __init__(self, st_container) -> None:
        self.st_container = st_container
        self.api_key: str = None

    def get(self):
        if "SEC_API_IO_API_KEY" in os.environ:
            return os.environ["SEC_API_IO_API_KEY"]
        if self.api_key:
            return self.api_key
        with self.st_container:
            self.api_key = st.text_input(
                type="password", label="Enter your https://sec-api.io API key here:"
            )
            if not self.api_key:
                st.info(
                    "Alternatively, you can set the `SEC_API_IO_API_KEY` environment variable, e.g. by creating an `.env` file."
                )
                st.stop()
            return self.api_key


def escape_markdown(text: str) -> str:
    return text.replace("$", "\$")


def st_display_html(html: str) -> None:
    st.markdown(escape_markdown(html), unsafe_allow_html=True)


def st_radio(label: str, options: list[str], *args, **kwargs) -> str:
    selected_value = st.radio(label=label, options=options, *args, **kwargs)
    return generate_bool_list(options.index(selected_value), len(options))
