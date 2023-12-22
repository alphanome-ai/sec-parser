from sec_downloader import Downloader

import sec_parser as sp

# Initialize the downloader with your company name and email
dl = Downloader("MyCompanyName", "email@example.com")

# Download the latest 10-Q filing for Apple
html = dl.get_filing_html(ticker="AAPL", form="10-Q")


# Utility function to make the example code a bit more compact
def print_first_n_lines(text: str, *, n: int):
    print("\n".join(text.split("\n")[:n]), "...", sep="\n")


elements: list = sp.Edgar10QParser().parse(html)

demo_output: str = sp.render(elements)
print_first_n_lines(demo_output, n=7)
