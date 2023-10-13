from pathlib import Path

import click

from tests.e2e.manage_snapshots import VerificationFailedError, manage_snapshots

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
def generate(data_dir: str) -> None:
    """
    Generate a new end-to-end dataset snapshot based on the latest parser results.

    This command will create a new snapshot in the directory specified by `data_dir`.
    The snapshot will contain data based on the current state of the sec-parser.

    :param data_dir: Directory where the generated snapshot will be saved.
    """
    manage_snapshots("generate", data_dir)


@click.command()
@click.option("--data_dir", default=DEFAULT_E2E_DATA_DIR, help=UPDATE_HELP)
def verify(data_dir: str) -> None:
    """
    Verify the integrity and correctness of the end-to-end dataset snapshot.

    This command will check the snapshot stored in the directory specified
    by `data_dir`.
    It ensures that the snapshot is consistent and accurate based on the current
    sec-parser logic.

    :param data_dir: Directory where the snapshot to be verified is located.
    """
    try:
        manage_snapshots("verify", data_dir)
    except VerificationFailedError as e:
        print(e)
        exit(1)


cli.add_command(generate)
cli.add_command(verify)


if __name__ == "__main__":
    cli()
