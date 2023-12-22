import sec_downloader as sd

import sec_parser as sp

# Initialize the downloader with your company name and email
dl = sd.Downloader("MyCompanyName", "email@example.com")

# Download the latest 10-Q filing for Apple
html = dl.get_filing_html(ticker="AAPL", form="10-Q")

# Now, we can parse the filing HTML into a list of semantic elements:
elements: list = sp.Edgar10QParser().parse(html)

print(elements[0])
