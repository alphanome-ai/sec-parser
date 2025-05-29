#!/usr/bin/env python3
"""
Test script to verify space preservation in text extraction
"""

from bs4 import BeautifulSoup
from complete_parser import UniversalEDGARParser

# Test HTML with potential space issues
test_html = """
<html>
<body>
<p>(a)The term of<b>this</b> Agreement shall be from January 15, 2016 through January<em>14</em>,2046.</p>
<p>This is a <strong>test</strong> of space preservation between <i>inline</i> elements.</p>
<div>Another <span>test</span> with <u>multiple</u> inline tags in<b>one</b>sentence.</div>
</body>
</html>
"""

print("Testing space preservation in text extraction...")
print("=" * 60)

# Test original BeautifulSoup behavior
soup = BeautifulSoup(test_html, 'html.parser')

print("Original get_text() without separator:")
for elem in soup.find_all(['p', 'div']):
    text = elem.get_text(strip=True)
    print(f"  '{text}'")

print("\nFixed get_text() with separator=' ':")
for elem in soup.find_all(['p', 'div']):
    text = elem.get_text(separator=" ", strip=True)
    print(f"  '{text}'")

print("\nTesting with our enhanced parser:")
parser = UniversalEDGARParser()
result = parser.parse(test_html, "test.html")

if result.success:
    print("Parser results:")
    for i, element in enumerate(result.elements[:5]):  # Show first 5 elements
        print(f"  {i+1}. [{element.type.value.upper()}] '{element.content}'")
else:
    print("Parser failed:", result.errors)