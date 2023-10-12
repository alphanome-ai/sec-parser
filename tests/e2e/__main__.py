from pathlib import Path

import click

from tests.e2e import snapshot as snapshot_module

DEFAULT_E2E_DATA_DIR = (
    Path(__file__).resolve().parent.parent.parent.parent / "sec-parser-e2e-data"
)


@click.group()
def cli() -> None:
    pass


UPDATE_HELP = (
    "Directory containing cloned repository from alphanome-ai/sec-parser-e2e-data."
)


@click.command()
@click.option("--data_dir", default=DEFAULT_E2E_DATA_DIR, help=UPDATE_HELP)
def snapshot(data_dir: str) -> None:
    print(f"Updating {data_dir}")
    """Update or create semantic-elements-list.json for each primary-document.html."""
    snapshot_module.write_snapshot(data_dir)


cli.add_command(snapshot)

if __name__ == "__main__":
    cli()
