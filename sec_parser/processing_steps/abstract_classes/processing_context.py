from dataclasses import dataclass


@dataclass
class ElementProcessingContext:
    """
    The ElementProcessingContext class is designed to provide context information
    for elementwise processing steps. This includes specifying whether an element is a
    root and tracking the current iteration in a series of repeated processing steps
    over all elements.

    Attributes
    ----------
        is_root_element (bool): Indicates if the given semantic element is a root
                                element in the HTML document.
        iteration (int): Represents the current iteration number during the repeated
                         processing of all semantic elements. This is related to the
                         `_NUM_ITERATIONS` constant in subclasses, which specifies
                         the total number of iterations that will be performed over
                         all elements.
    """

    is_root_element: bool
    iteration: int
