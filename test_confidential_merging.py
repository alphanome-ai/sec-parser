#!/usr/bin/env python3
"""
Test confidential metadata merging functionality
"""

from complete_parser import UniversalEDGARParser

# Test HTML with confidential metadata pattern
test_html = """
<html>
<body>
<p>Some regular content</p>
<p>Confidential Treatment Requested Under</p>
<p>17 C.F.R. Sections 200.80(b)(4) and 240.24b-2</p>
<p>More content after</p>
<p>Another Confidential treatment under</p>
<p>Section 123.45</p>
<p>Regular paragraph</p>
</body>
</html>
"""

print("Testing confidential metadata merging...")
print("=" * 60)

parser = UniversalEDGARParser()
result = parser.parse(test_html, "test_confidential.html")

if result.success:
    print("Parser results:")
    print(f"Total elements: {len(result.elements)}")
    print()
    
    for i, element in enumerate(result.elements):
        element_info = f"[{element.type.value.upper()}]"
        if hasattr(element, 'metadata') and element.metadata.get('merged_count'):
            element_info += f" (merged {element.metadata['merged_count']} elements)"
        print(f"{i+1:2d}. {element_info} '{element.content}'")
        
    # Check for merged elements
    merged_elements = [elem for elem in result.elements if 
                      hasattr(elem, 'metadata') and elem.metadata.get('merged_count')]
    
    print(f"\nFound {len(merged_elements)} merged confidential metadata elements")
    for elem in merged_elements:
        print(f"  Merged: '{elem.content}'")
        print(f"  Count: {elem.metadata['merged_count']} elements merged")
        
else:
    print("Parser failed:", result.errors)