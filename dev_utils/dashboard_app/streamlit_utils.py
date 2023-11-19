import contextlib

import streamlit as st
import streamlit_antd_components as sac


def st_adjust_madewithstreamlit():
    st.markdown(
        """
        <style>
            footer {
                padding-left: 15px !important;
                color: rgb(238, 238, 238) !important;
                z-index: 1;
            }
            footer a {
                color: rgb(210, 210, 210) !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def st_replace_menu_with_share_link_to_this_page_placeholder_button():
    # Shared styles for the buttons
    style = """
    <style>
        #MainMenu {
            margin-right: 50px;
            visibility: hidden;
        }
        .shareLinkToThisPageButton {
            position: fixed;
            top: 7px;
            right: 7px;
            background-color: #f0f2f6;
            color: #31333e !important;
            border: none;
            padding: 5px 10px;
            border-radius: 0.5rem;
            cursor: pointer;
            z-index: 9999999999;
            text-decoration: none;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
            font-weight: 500;
            font-size: 1rem;
            transition: background-color 0.3s ease, color 0.3s ease;
        }
        .shareLinkToThisPageButton:hover {
            background-color: #777ea4;
            color: #fff !important;
            text-decoration: none;  // Added this line to remove underline on hover
            transition: color 0.3s ease;  // Added this line to add transition to color change on hover
        }
        .shareLinkToThisPageButton:active {
            background-color: #31333e;
            color: #f0f2f6;
        }
        @media (max-width: 768px) {
            #MainMenu {
                margin-right: 5px;
            }
            .shareLinkToThisPageButtonText {
                font-size: 0;
            }
            .shareLinkToThisPageButtonIcon {
                display: inline;
            }
        }
        @media (min-width: 769px) {
            .shareLinkToThisPageButtonIcon {
                display: none;
            }
        }
        .shareLinkToThisPageButtonPlaceholder {
            cursor: not-allowed;
        }
    </style>
    """
    # Placeholder button
    st.markdown(
        style
        + '<a class="shareLinkToThisPageButtonPlaceholder shareLinkToThisPageButton" href="'
        + "#"
        + """"><span class="shareLinkToThisPageButtonIcon">🔗</span><span class="shareLinkToThisPageButtonText">🔗 Share</span></a>""",
        unsafe_allow_html=True,
    )


def st_set_url_to_share_link_to_this_page_placeholder_button(url: str):
    style = """
        <style>
        .shareLinkToThisPageButtonPlaceholder {
            display: none;
        }
        </style>
    """
    st.markdown(
        style
        + '<a class="shareLinkToThisPageButton" href="'
        + url
        + """"><span class="shareLinkToThisPageButtonIcon">🔗</span><span class="shareLinkToThisPageButtonText">🔗 Share</span></a>""",
        unsafe_allow_html=True,
    )


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


def st_modify_decoration(hide=False):
    if hide:
        st.markdown(
            """
            <style>
                div[data-testid="stDecoration"] {
                    display: none;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <style>
                div[data-testid="stDecoration"] {
                    background: none; /* This removes any background images or gradients */
                    background-color: #f0f2f6; /* This sets the background color to your primary color */
                    background-image: linear-gradient(90deg, #f0f2f6, #777ea4); /* This sets the new gradient */
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
    st.session_state["_" + key] = st.session_state[key]
    st.session_state["_" + key] = st.session_state[key]
