#!/usr/bin/env python3
"""
Generate semantic trees for all agreement files using the enhanced parser
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List
from complete_parser import UniversalEDGARParser, ParsedElement, ElementType


def element_to_dict(element: ParsedElement) -> Dict[str, Any]:
    """Convert ParsedElement to dictionary for JSON serialization"""
    return {
        "type": element.type.value,
        "content": element.content[:500] + "..." if len(element.content) > 500 else element.content,
        "level": element.level,
        "tag_name": element.tag_name,
        "line_number": element.line_number,
        "confidence": element.confidence,
        "attributes": element.attributes,
        "metadata": element.metadata,
        "children": [element_to_dict(child) for child in element.children]
    }


def build_hierarchical_tree(elements: List[ParsedElement]) -> Dict[str, Any]:
    """Build a hierarchical tree structure from flat elements list"""
    # Create tree structure
    tree = {
        "type": "document",
        "title": None,
        "elements": [],
        "statistics": {
            "total_elements": len(elements),
            "element_types": {},
            "structure_depth": 0
        }
    }
    
    # Count element types and find max depth
    for element in elements:
        elem_type = element.type.value
        tree["statistics"]["element_types"][elem_type] = tree["statistics"]["element_types"].get(elem_type, 0) + 1
        tree["statistics"]["structure_depth"] = max(tree["statistics"]["structure_depth"], element.level)
        
        # Extract title
        if element.type == ElementType.TITLE and tree["title"] is None:
            tree["title"] = element.content
    
    # Group elements by hierarchy
    current_section = None
    current_subsection = None
    
    for element in elements:
        element_dict = element_to_dict(element)
        
        if element.type == ElementType.TITLE:
            tree["elements"].append(element_dict)
            
        elif element.type in [ElementType.SECTION, ElementType.ARTICLE]:
            # Start new section
            current_section = {
                **element_dict,
                "subsections": [],
                "content_elements": []
            }
            tree["elements"].append(current_section)
            current_subsection = None
            
        elif element.type == ElementType.SUBSECTION:
            # Start new subsection
            if current_section is not None:
                current_subsection = {
                    **element_dict,
                    "content_elements": []
                }
                current_section["subsections"].append(current_subsection)
            else:
                tree["elements"].append(element_dict)
                
        else:
            # Regular content element
            if current_subsection is not None:
                current_subsection["content_elements"].append(element_dict)
            elif current_section is not None:
                current_section["content_elements"].append(element_dict)
            else:
                tree["elements"].append(element_dict)
    
    return tree


def generate_semantic_tree_for_file(html_file: Path, parser: UniversalEDGARParser) -> Dict[str, Any]:
    """Generate semantic tree for a single HTML file"""
    print(f"Processing {html_file.name}...")
    
    try:
        # Read and parse file
        with open(html_file, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        result = parser.parse(content, html_file.name)
        
        if not result.success:
            return {
                "filename": html_file.name,
                "success": False,
                "errors": result.errors,
                "tree": None
            }
        
        # Build hierarchical tree
        tree = build_hierarchical_tree(result.elements)
        
        # Add metadata
        semantic_tree = {
            "filename": html_file.name,
            "success": True,
            "quality_score": result.quality_score,
            "format": result.format.value,
            "parsing_metadata": {
                "total_elements": len(result.elements),
                "has_title": result.title is not None,
                "detected_title": result.title,
                "element_count_by_type": {}
            },
            "tree": tree
        }
        
        # Count elements by type
        for element in result.elements:
            elem_type = element.type.value
            semantic_tree["parsing_metadata"]["element_count_by_type"][elem_type] = \
                semantic_tree["parsing_metadata"]["element_count_by_type"].get(elem_type, 0) + 1
        
        return semantic_tree
        
    except Exception as e:
        return {
            "filename": html_file.name,
            "success": False,
            "errors": [str(e)],
            "tree": None
        }


def generate_text_summary(tree_data: Dict[str, Any]) -> str:
    """Generate a human-readable text summary of the semantic tree"""
    if not tree_data["success"]:
        return f"FAILED TO PARSE: {tree_data['errors']}"
    
    lines = []
    lines.append(f"SEMANTIC TREE: {tree_data['filename']}")
    lines.append("=" * 80)
    lines.append(f"Quality Score: {tree_data['quality_score']:.2f}")
    lines.append(f"Format: {tree_data['format']}")
    lines.append(f"Total Elements: {tree_data['parsing_metadata']['total_elements']}")
    
    if tree_data['tree']['title']:
        lines.append(f"Title: {tree_data['tree']['title']}")
    
    lines.append(f"\nElement Distribution:")
    for elem_type, count in sorted(tree_data['parsing_metadata']['element_count_by_type'].items()):
        lines.append(f"  {elem_type}: {count}")
    
    lines.append(f"\nStructure Depth: {tree_data['tree']['statistics']['structure_depth']}")
    lines.append(f"\nDOCUMENT STRUCTURE:")
    lines.append("-" * 40)
    
    def print_element(element, indent=0):
        prefix = "  " * indent
        elem_type = element.get("type", "unknown")
        content = element.get("content", "")
        
        # Truncate long content
        if len(content) > 100:
            content = content[:100] + "..."
        
        # Clean up content for display
        content = content.replace("\n", " ").replace("\r", " ").strip()
        
        lines.append(f"{prefix}[{elem_type.upper()}] {content}")
        
        # Handle nested structure
        if "subsections" in element:
            for subsection in element["subsections"]:
                print_element(subsection, indent + 1)
                for content_elem in subsection.get("content_elements", []):
                    print_element(content_elem, indent + 2)
        
        if "content_elements" in element:
            for content_elem in element["content_elements"]:
                print_element(content_elem, indent + 1)
    
    # Print document structure
    for element in tree_data['tree']['elements']:
        print_element(element)
    
    return "\n".join(lines)


def main():
    """Generate semantic trees for all agreement files"""
    parser = UniversalEDGARParser()
    html_files_dir = Path(__file__).parent / "html_files"
    output_dir = Path(__file__).parent / "semantic_tree"
    
    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)
    
    print("Generating semantic trees for all agreement files...")
    print("=" * 80)
    
    # Get all HTML files
    html_files = sorted(html_files_dir.glob("*.html"))
    all_results = []
    
    for html_file in html_files:
        # Generate semantic tree
        tree_data = generate_semantic_tree_for_file(html_file, parser)
        all_results.append(tree_data)
        
        # Save individual JSON file
        json_file = output_dir / f"{html_file.stem}_semantic_tree.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(tree_data, f, indent=2, ensure_ascii=False)
        
        # Save individual text summary
        txt_file = output_dir / f"{html_file.stem}_summary.txt"
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write(generate_text_summary(tree_data))
        
        # Print status
        if tree_data["success"]:
            print(f"✅ {html_file.name} -> Quality: {tree_data['quality_score']:.2f}")
        else:
            print(f"❌ {html_file.name} -> FAILED")
    
    # Save combined results
    combined_file = output_dir / "all_semantic_trees.json"
    with open(combined_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    # Generate master summary
    master_summary_lines = []
    master_summary_lines.append("SEMANTIC TREES - MASTER SUMMARY")
    master_summary_lines.append("=" * 80)
    master_summary_lines.append(f"Total files processed: {len(all_results)}")
    
    successful = [r for r in all_results if r["success"]]
    master_summary_lines.append(f"Successfully parsed: {len(successful)}")
    master_summary_lines.append(f"Success rate: {len(successful)/len(all_results)*100:.1f}%")
    
    if successful:
        avg_quality = sum(r["quality_score"] for r in successful) / len(successful)
        master_summary_lines.append(f"Average quality score: {avg_quality:.2f}")
    
    master_summary_lines.append(f"\nPER-FILE RESULTS:")
    master_summary_lines.append("-" * 40)
    
    for result in all_results:
        if result["success"]:
            title = result["tree"]["title"] or "No title"
            master_summary_lines.append(f"{result['filename']}: Quality {result['quality_score']:.2f} - {title[:50]}...")
        else:
            master_summary_lines.append(f"{result['filename']}: FAILED - {result['errors']}")
    
    # Add parser statistics
    master_summary_lines.append(f"\nPARSER STATISTICS:")
    master_summary_lines.append("-" * 40)
    master_summary_lines.append(parser.get_stats_report())
    
    # Save master summary
    summary_file = output_dir / "master_summary.txt"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("\n".join(master_summary_lines))
    
    print(f"\n✅ Generated semantic trees for {len(all_results)} files")
    print(f"📁 Output saved to: {output_dir}")
    print(f"📊 Files generated:")
    print(f"   - {len(all_results)} individual JSON files")
    print(f"   - {len(all_results)} individual text summaries")
    print(f"   - 1 combined JSON file (all_semantic_trees.json)")
    print(f"   - 1 master summary (master_summary.txt)")


if __name__ == "__main__":
    main()