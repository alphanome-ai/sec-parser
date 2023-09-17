import hashlib
import multiprocessing
import sys
import time
from multiprocessing import Manager, Pool
from pathlib import Path
from statistics import mean, median, stdev
from rich import print

import numpy as np
import sec_parser as sp
from millify import millify
from rich.console import Console
from rich.table import Table

ALLOWED_MICROSECONDS_PER_CHAR = 3
TESTS_PER_CORE = 5


class Metric:
    def __init__(self, name, style, justify="right"):
        self.name = name
        self.style = style
        self.justify = justify

    def calculate(self, times, char_count):
        raise NotImplementedError

    def visualize(self, value):
        return f"{value:.3f}"


class MinTime(Metric):
    def calculate(self, times, char_count):
        return min(times)


class MaxTime(Metric):
    def calculate(self, times, char_count):
        return max(times)


class Average(Metric):
    def calculate(self, times, char_count):
        return mean(times)


class Median(Metric):
    def calculate(self, times, char_count):
        return median(times)


class P95(Metric):
    def calculate(self, times, char_count):
        return np.percentile(times, 95)


class StdDev(Metric):
    def calculate(self, times, char_count):
        return stdev(times)


class Threshold(Metric):
    def calculate(self, times, char_count):
        return char_count * ALLOWED_MICROSECONDS_PER_CHAR / 1_000_000


class P95Threshold(Metric):
    def calculate(self, times, char_count, p95_time, threshold):
        return (p95_time / threshold) * 100

    def visualize(self, value):
        return f"{value:.0f} %"


class Size(Metric):
    def calculate(self, times, char_count):
        return char_count

    def visualize(self, value):
        return millify(value)


METRICS = [
    MinTime("Min Time", "green"),
    MaxTime("Max Time", "green"),
    Average("Average", "green"),
    Median("Median", "green"),
    P95("P95", "green"),
    StdDev("Std Dev", "green"),
    Size("Size", "dim"),
    Threshold("Threshold", "blue"),
    P95Threshold("P95/Threshold", "green"),
]


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


if __name__ == "__main__":
    core_count = multiprocessing.cpu_count()

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

    tests_per_file = core_count * TESTS_PER_CORE
    total_tests_ran = tests_per_file * file_counter
    print(
        f"- Each document underwent [bold]{tests_per_file}[/bold] tests, totaling [bold]{total_tests_ran}[/bold] tests across [bold]{core_count}[/bold] cores.",
        f"- The 'Threshold' in the table signifies the maximum allowable parsing time (in seconds) per document.",
        f"- This threshold was determined based on a set rate of [bold]{ALLOWED_MICROSECONDS_PER_CHAR}[/bold] microseconds per HTML character.",
        f"- Performance metrics ('Average', 'Median', 'P95') are measured in seconds, while 'Size' is measured in HTML characters.",
        sep="\n",
    )
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

        example_doc = next(
            (
                doc
                for doc in example_htmls
                if hashlib.sha256(doc.encode()).hexdigest() == document_hash
            ),
            None,
        )
        char_count = len(example_doc)

        metrics[document_hash] = {}
        for metric in METRICS:
            if isinstance(metric, P95Threshold):
                p95_time = metrics[document_hash]["P95"]
                threshold = metrics[document_hash]["Threshold"]
                metrics[document_hash][metric.name] = metric.calculate(
                    times, char_count, p95_time, threshold
                )
            else:
                metrics[document_hash][metric.name] = metric.calculate(
                    times, char_count
                )

        if metrics[document_hash]["P95/Threshold"] > 100:
            failed_documents.append(document_hash)

    render_table(metrics, hash_to_filename)

    if failed_documents:
        print("\nDocuments that failed the threshold:")
        for doc in failed_documents:
            print(get_document_name(doc, hash_to_filename))
        sys.exit(1)
    else:
        print("\nAll documents passed the threshold.")
        sys.exit(0)
