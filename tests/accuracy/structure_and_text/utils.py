from sec_parser.semantic_elements.semantic_elements import IrrelevantElement

IGNORED_SEMANTIC_ELEMENT_TYPES = (IrrelevantElement,)


def elements_to_dicts(elements):
    return [
        e.to_dict(
            include_previews=False,
            include_contents=True,
        )
        for e in elements
        if not isinstance(e, IGNORED_SEMANTIC_ELEMENT_TYPES)
    ]
