# NOTE:
# For more examples and advanced usage of `sec-parser`, refer to the following resources:
# - User Guide: 
#     https://sec-parser.readthedocs.io/en/latest/notebooks/user_guide.html
# - Developer Guide
#     https://sec-parser.readthedocs.io/en/latest/notebooks/developer_guide.html
# - Documentation:
#     https://sec-parser.readthedocs.io/en/latest/

from sec_downloader import Downloader

import sec_parser as sp

# Utility function to make the example code a bit more compact
def print_first_n_lines(text: str, *, n: int):
    print("\n".join(text.split("\n")[:n]), "...", sep="\n")


# Initialize the downloader with your company name and email
dl = Downloader("MyCompanyName", "email@example.com")

# Download the latest 10-Q filing for Apple
html = dl.get_filing_html(ticker="AAPL", form="10-Q")

# Now, we can parse the filing HTML into a list of semantic elements:
elements: list = sp.Edgar10QParser().parse(html)
demo_output: str = sp.render(elements)
print_first_n_lines(demo_output, n=7)

# We can also construct a semantic tree to allow for easy filtering by parent sections:
tree = sp.TreeBuilder().build(elements)
demo_output: str = sp.render(tree)
print_first_n_lines(demo_output, n=7)
