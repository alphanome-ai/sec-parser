from __future__ import annotations

import click
import rich.traceback

from tests._sec_parser_validation_data import DEFAULT_VALIDATION_DATA_DIR
from tests.e2e.manage_snapshots import VerificationFailedError, manage_snapshots

rich.traceback.install()


@click.group()
def cli() -> None:
    pass


@click.command()
@click.option(
    "--data_dir",
    default=DEFAULT_VALIDATION_DATA_DIR,
    help="Directory containing cloned repository from alphanome-ai/sec-parser-test-data.",
)
@click.option("--document_type", multiple=True, help="Filter by document types")
@click.option("--company_name", multiple=True, help="Filter by company names")
@click.option("--report_id", multiple=True, help="Filter by report IDs")
@click.option("--yaml_path", help="Path to YAML filter file")
def generate(
    data_dir: str,
    document_type: list[str],
    company_name: list[str],
    report_id: list[str],
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
        document_type,
        company_name,
        report_id,
        yaml_path,
    )


@click.command()
@click.option(
    "--data_dir",
    default=DEFAULT_VALIDATION_DATA_DIR,
    help="Directory containing cloned repository from alphanome-ai/sec-parser-test-data.",
)
@click.option("--document_type", multiple=True, help="Filter by document types")
@click.option("--company_name", multiple=True, help="Filter by company names")
@click.option("--report_id", multiple=True, help="Filter by report IDs")
@click.option("--yaml_path", help="Path to YAML filter file")
def verify(
    data_dir: str,
    document_type: list[str],
    company_name: list[str],
    report_id: list[str],
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
            document_type,
            company_name,
            report_id,
            yaml_path,
        )
    except VerificationFailedError as e:
        print(e)
        exit(1)


cli.add_command(generate)
cli.add_command(verify)


if __name__ == "__main__":
    cli()
