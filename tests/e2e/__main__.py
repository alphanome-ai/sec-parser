from __future__ import annotations

from pathlib import Path

import click

from tests.e2e.manage_snapshots import VerificationFailedError, manage_snapshots

DEFAULT_E2E_DATA_DIR = (
    Path(__file__).resolve().parent.parent.parent.parent / "sec-parser-validation-data"
)


@click.group()
def cli() -> None:
    pass


@click.command()
@click.option(
    "--data_dir",
    default=DEFAULT_E2E_DATA_DIR,
    help="Directory containing cloned repository from alphanome-ai/sec-parser-validation-data.",
)
@click.option("--document_types", multiple=True, help="Filter by document types")
@click.option("--company_names", multiple=True, help="Filter by company names")
@click.option("--report_ids", multiple=True, help="Filter by report IDs")
@click.option("--yaml_path", help="Path to YAML filter file")
def generate(
    data_dir: str,
    document_types: list[str],
    company_names: list[str],
    report_ids: list[str],
    yaml_path: str,
) -> None:
    """
    Generate a new end-to-end dataset snapshot based on the latest parser results.

    This command will create a new snapshot in the directory specified by `data_dir`.
    The snapshot will contain data based on the current state of the sec-parser.
    """
    manage_snapshots(
        "generate",
        data_dir,
        document_types,
        company_names,
        report_ids,
        yaml_path,
    )


@click.command()
@click.option(
    "--data_dir",
    default=DEFAULT_E2E_DATA_DIR,
    help="Directory containing cloned repository from alphanome-ai/sec-parser-validation-data.",
)
@click.option("--document_types", multiple=True, help="Filter by document types")
@click.option("--company_names", multiple=True, help="Filter by company names")
@click.option("--report_ids", multiple=True, help="Filter by report IDs")
@click.option("--yaml_path", help="Path to YAML filter file")
def verify(
    data_dir: str,
    document_types: list[str],
    company_names: list[str],
    report_ids: list[str],
    yaml_path: str,
) -> None:
    """
    Verify the integrity and correctness of the end-to-end dataset snapshot.

    This command will check the snapshot stored in the directory specified
    by `data_dir`.
    It ensures that the snapshot is consistent and accurate based on the current
    sec-parser logic.
    """
    try:
        manage_snapshots(
            "verify",
            data_dir,
            document_types,
            company_names,
            report_ids,
            yaml_path,
        )
    except VerificationFailedError as e:
        print(e)
        exit(1)


cli.add_command(generate)
cli.add_command(verify)


if __name__ == "__main__":
    cli()
