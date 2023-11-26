from dataclasses import dataclass


@dataclass
class ElementProcessingContext:
    """
    The ElementProcessingContext class is designed to provide context information
    for elementwise processing steps.
    """

    iteration: int
