import streamlit as st
from _utils.misc import generate_bool_list

from typing import TypeVar

T = TypeVar("T")


class NotHashed(T):
    """This is a generic wrapper for any type. It prevents the value
    from being hashed when it's passed to functions like st.cache_resource()."""

    def __init__(self, value: T, /) -> None:
        self.value = value


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


def st_radio(label: str, options: list[str], *args, **kwargs) -> str:
    selected_value = st.radio(label=label, options=options, *args, **kwargs)
    return generate_bool_list(options.index(selected_value), len(options))


def st_multiselect_allow_long_titles():
    st.markdown(  # Make the multiselect fit long text options
        """
        <style>
            .stMultiSelect [data-baseweb=select] span{
                max-width: 500px;
                font-size: 1rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def st_expander_allow_nested():
    import streamlit_nested_layout
