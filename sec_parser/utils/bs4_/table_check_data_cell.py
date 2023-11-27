import bs4

from sec_parser.utils.bs4_.get_single_table import get_single_table


def check_table_contains_text_page(bs4_tag: bs4.Tag) -> bool:
    """
    check_table_contains_text_page determines whether the given bs4 tag
    is a table of contents.

    Checks whether one of the table's <td> tags (data cells) contains
    the text "page".

    Returns true if there exists at least one <td> tag
    with the text "page", otherwise the function returns false.
    """
    table=get_single_table(bs4_tag)

    return any(is_page_data_cell(t.text.strip()) for t in table.find_all("td"))

def is_page_data_cell(data_cell_text: str) -> bool:
    """
    is_page_data_cell determines whether the given text expresses the
    word "page".

    Returns true if the given text expresses the word "page", otherwise
    the function returns false.
    """
    return data_cell_text.lower() in {"page", "page no.", "page number"}
