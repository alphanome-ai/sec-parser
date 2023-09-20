import hashlib
import multiprocessing
import sys
import time
from multiprocessing import Manager, Pool
from pathlib import Path

from rich import print
from rich.console import Console
from rich.table import Table

import sec_parser as sp
from tests.e2e.speed._metrics import (P99, Average, MaxTime, Median,
                                      RatioMetric, Size, Threshold)

# Specify the metric that determines the test outcome
# A test will pass or fail based on this metric
TEST_METRIC = "Average/Threshold"

ALLOWED_MICROSECONDS_PER_CHAR = 1

DEFAULT_TESTS_PER_CORE = 5

# Define metrics to be used
METRICS = [
    Average("Average", "blue"),
    Threshold(ALLOWED_MICROSECONDS_PER_CHAR, "Threshold", "blue"),
    RatioMetric(
        Average("Average"),
        Threshold(ALLOWED_MICROSECONDS_PER_CHAR, "Threshold"),
        "Average/Threshold",
        "blue",
    ),
    Median("Median", "dim"),
    P99("P99", "dim"),
    MaxTime("Max Time", "dim"),
    Size("Size", "dim"),
]


# Function to get document name from hash
def get_document_name(document_hash, hash_to_filename):
    return hash_to_filename.get(document_hash, document_hash)


# Function to execute a single test
def execute_test(html_input, execution_times):
    start_time = time.time()
    elements = sp.SecParser().parse(html_input)
    tree = sp.TreeBuilder().build(elements)
    assert len(tree.root_nodes)
    elapsed_time = time.time() - start_time

    html_hash = hashlib.sha256(html_input.encode()).hexdigest()
    execution_times[html_hash].append(elapsed_time)


# Function to execute multiple tests
def execute_multiple_tests(html_inputs, execution_times):
    for html_input in html_inputs:
        execute_test(html_input, execution_times)


# Function to render the results table
def render_table(metrics, hash_to_filename):
    console = Console()

    # Initialize table with headers
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Document", style="dim", justify="right")
    for metric in METRICS:
        table.add_column(metric.name, style=metric.style, justify=metric.justify)

    # Populate table with rows
    for document_hash, metric_values in metrics.items():
        document_name = get_document_name(document_hash, hash_to_filename)
        row_data = [document_name]
        for metric in METRICS:
            value = metric_values[metric.name]
            row_data.append(metric.visualize(value))
        table.add_row(*row_data)

    # Display the table in the terminal
    console.print(table)


# Main execution
if __name__ == "__main__":
    tests_per_core = DEFAULT_TESTS_PER_CORE
    core_count = None

    for arg in sys.argv[1:]:
        if arg.startswith("--tests-per-core="):
            tests_per_core = int(arg.partition("=")[2])
        elif arg.startswith("--cores="):
            core_count = int(arg.partition("=")[2])

    if core_count is None:
        core_count = multiprocessing.cpu_count()

    # Load test data
    test_data_htmls = {}
    test_data_path = Path(__file__).parent / "../test_data"
    hash_to_filename = {}
    file_counter = 0
    for html_file in test_data_path.glob("10q_*.html"):
        with open(html_file, "r") as file:
            file_content = file.read()
            test_data_htmls[html_file.name] = file_content
            hash_key = hashlib.sha256(file_content.encode()).hexdigest()
            hash_to_filename[hash_key] = html_file.name  # Populate the mapping
            file_counter += 1

    # Calculate number of tests
    tests_per_file = core_count * tests_per_core
    total_tests_ran = tests_per_file * file_counter

    # Print initial information
    print(
        f"- Each document underwent [bold]{tests_per_file}[/bold] tests, totaling [bold]{total_tests_ran}[/bold] tests across [bold]{core_count}[/bold] cores.",
        f"- The 'Threshold' in the table signifies the maximum allowable parsing time (in seconds) per document.",
        f"- This threshold was determined based on a set rate of [bold]{ALLOWED_MICROSECONDS_PER_CHAR}[/bold] microseconds per HTML character.",
        f"- Performance metrics (e.g. 'Average', 'Median', 'P99') are measured in seconds, while 'Size' is measured in HTML characters.",
        sep="\n",
    )

    # Prepare test data
    example_htmls = list(test_data_htmls.values()) * tests_per_file

    # Initialize shared data structures
    manager = Manager()
    execution_times = manager.dict(
        {
            hashlib.sha256(doc.encode()).hexdigest(): manager.list()
            for doc in example_htmls
        }
    )

    # Execute tests in parallel
    with Pool(processes=core_count) as pool:
        pool.starmap(
            execute_multiple_tests,
            [
                (example_htmls[i::core_count], execution_times)
                for i in range(core_count)
            ],
        )

    # Initialize metrics and failed documents list
    metrics = {}
    failed_documents = []

    # Calculate metrics for each document
    for document_hash, times in execution_times.items():
        times = list(times)
        if not times:
            continue  # Skip if no timing data collected

        # Find the document corresponding to the hash
        example_doc = next(
            (
                doc
                for doc in example_htmls
                if hashlib.sha256(doc.encode()).hexdigest() == document_hash
            ),
            None,
        )
        char_count = len(example_doc)

        # Calculate each metric for the document
        metrics[document_hash] = {}
        for metric in METRICS:
            if isinstance(metric, RatioMetric):
                metrics[document_hash][metric.name] = metric.calculate(
                    times, char_count, metrics[document_hash]
                )
            else:
                metrics[document_hash][metric.name] = metric.calculate(
                    times, char_count
                )

        # Check if the document failed the threshold
        if metrics[document_hash][TEST_METRIC] > 100:
            failed_documents.append(document_hash)

    # Render the results table
    render_table(metrics, hash_to_filename)

    # Print the documents that failed the threshold
    if failed_documents:
        print("\nDocuments that failed the threshold:")
        for doc in failed_documents:
            print(get_document_name(doc, hash_to_filename))
        sys.exit(1)
    else:
        print("\nAll documents passed the threshold.")
        sys.exit(0)
