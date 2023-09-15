import bs4


class HtmlTag:
    """
    HtmlTag class serves as a wrapper around native BeautifulSoup4 Tag objects. The
    primary motivation for introducing this wrapper is to decouple our application
    logic from the underlying library. This abstraction makes it easier to make
    modifications or even switch to a different HTML parsing library in the future
    without requiring extensive changes throughout the codebase.

    The HtmlTag class can also serve as a location to add any extension methods or
    additional properties that are not provided by the native BeautifulSoup4 Tag class,
    thereby further enhancing maintainability and extensibility.
    """

    def __init__(self, bs4: bs4.Tag) -> None:
        self.bs4 = bs4
