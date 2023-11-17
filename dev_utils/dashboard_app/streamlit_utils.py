import streamlit as st
import streamlit_antd_components as sac


def st_divider(label, icon, *, align="center", bold=False):
    sac.divider(
        label=label,
        icon=icon,
        align=align,
        bold=bold,
        dashed=True,
    )


def st_multiselect_allow_long_titles():  # noqa: ANN201
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


def st_expander_allow_nested():  # noqa: ANN201
    # just import the module to enable the functionality
    import streamlit_nested_layout as _

    # use the imported module to prevent linters from removing the import
    __ = _


def st_change_decoration_color():
    st.markdown(
        """
        <style>
            div[data-testid="stDecoration"] {
                background: none; /* This removes any background images or gradients */
                background-color: #767FA6; /* This sets the background color to your primary color */
                background-image: linear-gradient(90deg, #767FA6, #0000FF); /* This sets the new gradient */
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def st_remove_top_page_margin():
    st.markdown(
        "<style> div[class^='block-container'] { padding-top: 0rem; } </style>",
        unsafe_allow_html=True,
    )


def st_keep(key):
    "https://stackoverflow.com/questions/74968179/session-state-is-reset-in-streamlit-multipage-app"
    # Copy from temporary widget key to permanent key
    st.session_state[key] = st.session_state["_" + key]


def st_unkeep(key):
    "https://stackoverflow.com/questions/74968179/session-state-is-reset-in-streamlit-multipage-app"
    # Copy from permanent key to temporary widget key
    st.session_state["_" + key] = st.session_state[key]
