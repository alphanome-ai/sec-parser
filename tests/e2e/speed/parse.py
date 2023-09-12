import hashlib
import multiprocessing
import sys
import time
from multiprocessing import Manager, Pool
from pathlib import Path
from statistics import mean, median
import sec_parser as sp
import numpy as np
from rich.console import Console
from rich.table import Table

ALLOWED_MICROSECONDS_PER_CHAR = 3
TESTS_PER_CORE = 5


def get_document_name(document_hash, hash_to_filename):
    return hash_to_filename.get(document_hash, document_hash)


def execute_test(html_input, execution_times):
    start_time = time.time()
    elements = sp.SecParser().parse(html_input)
    tree = sp.TreeBuilder().build(elements)
    assert len(tree.root_nodes)
    elapsed_time = time.time() - start_time

    html_hash = hashlib.sha256(html_input.encode()).hexdigest()
    execution_times[html_hash].append(elapsed_time)


def execute_multiple_tests(html_inputs, execution_times):
    for html_input in html_inputs:
        execute_test(html_input, execution_times)


def render_table(metrics, hash_to_filename):
    console = Console()

    # Initialize table with headers
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Document", style="dim", width=64)
    table.add_column("Avg Time, s", style="green", justify="right", width=15)
    table.add_column("Median Time, s", style="green", justify="right", width=15)
    table.add_column("P95 Time, s", style="green", justify="right", width=15)
    table.add_column("Threshold, s", style="green", justify="right", width=15)
    table.add_column("P95 % of Threshold", style="green", justify="right", width=20)

    # Populate table with rows
    for document_hash, metric in metrics.items():
        avg_time, median_time, p95_time, threshold, p95_percentage = metric
        document_name = get_document_name(document_hash, hash_to_filename)
        table.add_row(
            document_name,
            f"{avg_time:.2f}",
            f"{median_time:.2f}",
            f"{p95_time:.2f}",
            f"{threshold:.2f}",
            f"{p95_percentage:.0f} %",
        )

    # Display the table in the terminal
    console.print(table)


if __name__ == "__main__":
    core_count = multiprocessing.cpu_count()

    test_data_htmls = {}
    test_data_path = Path(__file__).parent / "../test_data"
    hash_to_filename = {}
    for html_file in test_data_path.glob("10q_*.html"):
        with open(html_file, "r") as file:
            file_content = file.read()
            test_data_htmls[html_file.name] = file_content
            hash_key = hashlib.sha256(file_content.encode()).hexdigest()
            hash_to_filename[hash_key] = html_file.name  # Populate the mapping

    tests_per_file = core_count * TESTS_PER_CORE
    print(f"Running {tests_per_file} tests per file on {core_count} cores")
    print(f"Allowing {ALLOWED_MICROSECONDS_PER_CHAR} microseconds per HTML character")
    example_htmls = list(test_data_htmls.values()) * tests_per_file

    manager = Manager()
    execution_times = manager.dict(
        {
            hashlib.sha256(doc.encode()).hexdigest(): manager.list()
            for doc in example_htmls
        }
    )

    with Pool(processes=core_count) as pool:
        pool.starmap(
            execute_multiple_tests,
            [
                (example_htmls[i::core_count], execution_times)
                for i in range(core_count)
            ],
        )

    metrics = {}
    failed_documents = []
    for document_hash, times in execution_times.items():
        times = list(times)
        if not times:
            continue  # Skip if no timing data collected
        avg_time = mean(times)
        median_time = median(times)
        p95_time = np.percentile(times, 95)

        example_doc = next(
            (
                doc
                for doc in example_htmls
                if hashlib.sha256(doc.encode()).hexdigest() == document_hash
            ),
            None,
        )
        char_count = len(example_doc)
        threshold = char_count * ALLOWED_MICROSECONDS_PER_CHAR / 1_000_000

        p95_percentage = (p95_time / threshold) * 100

        if p95_time > threshold:
            failed_documents.append(document_hash)

        metrics[document_hash] = (
            avg_time,
            median_time,
            p95_time,
            threshold,
            p95_percentage,
        )

    render_table(metrics, hash_to_filename)

    if failed_documents:
        print("\nDocuments that failed the threshold:")
        for doc in failed_documents:
            print(get_document_name(doc, hash_to_filename))
        sys.exit(1)
    else:
        print("\nAll documents passed the threshold.")
        sys.exit(0)
