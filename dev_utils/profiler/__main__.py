from __future__ import annotations

import click
from pyinstrument import Profiler
from sec_downloader import Downloader

import sec_parser as sp


@click.command()
@click.option(
    "--ticker",
    required=True,
    help="Get latest 10-Q by ticker. Example: AAPL",
)
@click.option(
    "--print_to_console",
    is_flag=True,
    help="Print the results to the console. If not set, results will be opened in a browser.",
)
def run(ticker: str, print_to_console: bool) -> None:  # noqa: FBT001
    dl = Downloader("Alphanome.AI", "info@alphanome.ai")
    html = dl.get_latest_html("10-Q", ticker)

    with Profiler(interval=0.01) as profiler:
        sp.Edgar10QParser().parse(html)

    if print_to_console:
        profiler.print()
    else:
        profiler.open_in_browser()


if __name__ == "__main__":
    run()
