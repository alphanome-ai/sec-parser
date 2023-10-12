def get_direct_subclass_of_base_class(cls: type, base_class: type) -> type:
    """
    Given a class, find the class that is one step below
    the specified base_class in its inheritance hierarchy.
    """
    if not issubclass(cls, base_class):
        msg = f"Argument must be a subclass of {base_class.__name__}."
        raise TypeError(msg)

    root_child = None
    for ancestor in cls.mro():
        if ancestor is base_class:
            break
        root_child = ancestor

    if root_child is None:
        msg = (
            f"Could not find a root child class for "
            f"the given class below {base_class.__name__}."
        )
        raise ValueError(msg)

    return root_child
