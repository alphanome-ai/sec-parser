import sec_downloader as sd

import sec_parser as sp

# Initialize the downloader with your company name and email
dl = sd.Downloader("MyCompanyName", "email@example.com")

# Download the latest 10-Q filing for Apple
html = dl.get_filing_html(ticker="AAPL", form="10-Q")

# Now, we can parse the filing HTML into a list of semantic elements:
elements: list = sp.Edgar10QParser().parse(html)

# Let's print the first 5 elements:
for element in elements[:5]:
    element_type = element.__class__.__name__
    element_text = element.text
    print(f"Element Type: {element_type}")
    print(f"Text Content: {element_text}")
    print("-" * 40)  # Separator for readability
