def interleave_lists(lists):
    """
    Interleave elements from a list of lists.

    Parameters
    ----------
        lists (list): A list of lists to interleave.

    Returns
    -------
        list: A list containing interleaved elements from the input lists.

    Examples
    --------
        >>> interleave_lists([['a', 'b', 'c'], [1, 2], ['q']])
        ['a', 1, 'q', 'b', 2, 'c']

        >>> interleave_lists([[1, 2, 3], ['a', 'b']])
        [1, 'a', 2, 'b', 3]

        >>> interleave_lists([[]])
        []

        >>> interleave_lists([])
        []

        >>> interleave_lists([['a'], ['b'], ['c']])
        ['a', 'b', 'c']
    """
    max_length = max(len(lst) for lst in lists) if lists else 0
    return [lst[i] for i in range(max_length) for lst in lists if i < len(lst)]


if __name__ == "__main__":
    import doctest

    doctest.testmod()
    print("Finished running doctests!")
