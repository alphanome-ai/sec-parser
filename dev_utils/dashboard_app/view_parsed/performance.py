from typing import TYPE_CHECKING

import numpy as np
import streamlit as st
from rich.console import Console

from dev_utils.core.profiled_parser import ParsingOutput, ProfiledParser
from dev_utils.dashboard_app.streamlit_utils import st_divider

if TYPE_CHECKING:
    from pyinstrument import Profiler


def render_view_parsed_performance(previous_parsing_output: ParsingOutput, name):
    with st.sidebar:
        options = [
            f"{x:.{max(1, 1-int(np.floor(np.log10(x))))}f}".rstrip("0")
            for x in np.logspace(-4.1, -1, 100)
        ]
        interval = st.select_slider(
            "Set sampling interval (seconds)",
            options=options,
            value=next(x for x in options if float(x) >= 0.001),
        )
    assert isinstance(interval, str)
    interval = float(interval)

    st.markdown(
        f"""
        This is a statistical profiler that interrupts the program every {interval*1000:g} ms (modifiable via a sidebar slider) and records the entire stack at that point. Despite the seemingly few samples that make up a report, the accuracy is not compromised. The {interval*1000:g} ms interval is a lower bound for recording a stackframe. However, if a single function call takes a long time, it will be recorded at the end of that call, effectively 'bunching up' the samples. The advantage of statistical profilers like Pyinstrument is their lower overhead compared to tracing profilers. For more information, [continue reading](https://pyinstrument.readthedocs.io/en/latest/how-it-works.html).
        """,
    )

    parser = ProfiledParser(parser=previous_parsing_output.parser, interval=interval)
    profiled_result = parser.parse(previous_parsing_output.html)

    original_parse_time = previous_parsing_output.result.parse_time
    profiled_parse_time = profiled_result.parse_time
    overhead = ((profiled_parse_time - original_parse_time) / original_parse_time) * 100

    original_parse_time_str = (
        f"{original_parse_time:.2f} seconds"
        if original_parse_time >= 1
        else f"{original_parse_time * 1000:.0f} milliseconds"
    )
    profiled_parse_time_str = (
        f"{profiled_parse_time:.2f} seconds"
        if profiled_parse_time >= 1
        else f"{profiled_parse_time * 1000:.0f} milliseconds"
    )

    with st.sidebar:
        st.write(
            f"""
            The original parse time was **{original_parse_time_str}**. With profiling enabled, the parse time increased to **{profiled_parse_time_str}**. This indicates an overhead of **{overhead/100+1:.1f}x** due to the use of the profiler.
            """,
        )
        timeline = not st.checkbox(
            "Sort results by time taken",
            value=False,
        )

    assert profiled_result.profile
    html = profiled_result.profile.output_html(timeline=timeline)
    st.download_button(
        label="Download the Interactive Report",
        data=html,
        file_name=f"{name}.html",
        mime="text/html",
    )

    st_divider("Preview", "speedometer2")
    with st.sidebar:
        show_all = st.checkbox(
            "Verbose mode (for Preview only)",
            value=False,
        )

    output_text = profiled_result.profile.output_text(
        unicode=True, timeline=timeline, show_all=show_all
    )
    # st.code trims whitespace at the beginning, so we add a dot to prevent that to not lose indentation
    output_text = "_." + output_text[3:]
    st.code(output_text)
