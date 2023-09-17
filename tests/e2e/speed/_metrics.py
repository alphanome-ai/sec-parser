from statistics import mean, median, stdev

import numpy as np
from millify import millify


class Metric:
    def __init__(self, name="Undefined", style='dim', justify="right"):
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

    def visualize(self, value):
        return f"[bold]{value:.3f}[/bold]"


class Median(Metric):
    def calculate(self, times, char_count):
        return median(times)


class P99(Metric):
    def calculate(self, times, char_count):
        return np.percentile(times, 99)


class StdDev(Metric):
    def calculate(self, times, char_count):
        return stdev(times)


class Threshold(Metric):
    def __init__(self, microsecond_threshold, name="Undefined", style="dim", justify="right"):
        super().__init__(name, style, justify)
        self.microsecond_threshold = microsecond_threshold

    def calculate(self, times, char_count):
        return char_count * self.microsecond_threshold / 1_000_000


class RatioMetric(Metric):
    def __init__(self, metric1, metric2, name, style="dim", justify="right"):
        super().__init__(name, style, justify)
        self.metric1 = metric1
        self.metric2 = metric2

    def calculate(self, times, char_count, metrics):
        value1 = metrics[self.metric1.name]
        value2 = metrics[self.metric2.name]
        return (value1 / value2) * 100

    def visualize(self, value):
        return f"{value:.0f} %"


class Size(Metric):
    def calculate(self, times, char_count):
        return char_count

    def visualize(self, value):
        return millify(value)
