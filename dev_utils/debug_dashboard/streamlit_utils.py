import streamlit as st

from dev_utils.debug_dashboard.sec_utils import generate_bool_list


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
    # just import the module to enable the functionality
    import streamlit_nested_layout as _

    # use the imported module to prevent linters from removing the import
    _  # noqa: B018
