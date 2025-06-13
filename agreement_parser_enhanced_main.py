#!/usr/bin/env python3
"""
Universal EDGAR Parser - Main Integration
Combines all components for robust agreement parsing
"""

import os
import sys
from pathlib import Path
import traceback
from typing import List, Dict, Optional
import json

# Add the sec_parser module to the path
sys.path.insert(0, str(Path(__file__).parent))

from agreement_parser_enhanced import *
from agreement_parser_enhanced_part2 import *
from agreement_parser_enhanced_part3 import *


class UniversalEDGARParser:
    """Universal parser for all EDGAR document formats"""
    
    def __init__(self):
        self.format_detector = FormatDetector()
        self.converter = FormatConverter()
        self.extractor = HTMLExtractor()
        self.analyzer = StructuralAnalyzer()
        self.title_detector = TitleDetector()
        self.classifier = ElementClassifier()
        self.validator = ParseValidator()
        self.special_handler = SpecialCaseHandler()
        
        # Statistics tracking
        self.stats = {
            'total_parsed': 0,
            'successful_parses': 0,
            'format_counts': {},
            'failures': [],
        }
        
    def parse(self, raw_content: str, filename: str = None) -> ParseResult:
        """Parse document with comprehensive error handling"""
        try:
            logger.info(f"Starting parse of {filename or 'unknown file'}")
            
            # Step 1: Detect format
            doc_format = self.format_detector.detect_format(raw_content)
            logger.info(f"Detected format: {doc_format}")
            
            # Step 2: Convert to normalized HTML
            if doc_format == DocumentFormat.DATA_FORMAT:
                # Special handling for data format
                elements = self.special_handler.handle_data_format(raw_content)
                return ParseResult(
                    success=True,
                    elements=elements,
                    format=doc_format,
                    title=self._extract_title_from_elements(elements),
                    quality_score=0.8
                )
            
            # Convert format
            html_content = self.converter.convert(raw_content, doc_format)
            
            # Step 3: Extract clean HTML
            extracted_html = self.extractor.extract_content(html_content)
            if not extracted_html:
                extracted_html = html_content
                
            # Step 4: Structural analysis
            try:
                structure = self.analyzer.analyze(extracted_html)
            except Exception as e:
                logger.warning(f"Structural analysis failed: {e}")
                # Fallback to basic parsing
                return self._fallback_parse(extracted_html, doc_format)
            
            # Step 5: Detect title
            title_element = self.title_detector.detect_title(
                structure['elements'], structure
            )
            
            # Step 6: Classify elements
            elements = self.classifier.classify_all(structure)
            
            # Step 7: Handle special cases
            if self._is_table_heavy(structure):
                soup = BeautifulSoup(extracted_html, 'html.parser')
                table_elements = self.special_handler.handle_table_based(soup)
                if table_elements:
                    elements.extend(table_elements)
            
            # Step 8: Validate and fix
            validated_elements = self.validator.validate_and_fix(elements)
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(validated_elements, structure)
            
            result = ParseResult(
                success=True,
                elements=validated_elements,
                format=doc_format,
                title=title_element['text'] if title_element else None,
                quality_score=quality_score,
                metadata={
                    'element_count': len(validated_elements),
                    'has_title': title_element is not None,
                    'structure_depth': max((elem.level for elem in validated_elements), default=0)
                }
            )
            
            self._update_stats(filename, result)
            return result
            
        except Exception as e:
            logger.error(f"Parse failed for {filename}: {str(e)}")
            logger.error(traceback.format_exc())
            
            result = ParseResult(
                success=False,
                elements=[],
                format=DocumentFormat.UNKNOWN,
                errors=[str(e)],
                quality_score=0.0
            )
            
            self._update_stats(filename, result)
            return result
    
    def _fallback_parse(self, html_content: str, doc_format: DocumentFormat) -> ParseResult:
        """Fallback parsing when main parsing fails"""
        logger.info("Using fallback parsing strategy")
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract all text elements
            elements = []
            for i, elem in enumerate(soup.find_all(text=True)):
                text = elem.strip()
                if text and len(text) > 3:
                    parsed_elem = ParsedElement(
                        type=ElementType.PARAGRAPH,
                        content=text,
                        level=5,
                        line_number=i,
                        confidence=0.5
                    )
                    elements.append(parsed_elem)
            
            # Try to identify title from first few elements
            title = None
            for elem in elements[:10]:
                if any(keyword in elem.content.lower() for keyword in ['agreement', 'contract', 'lease']):
                    title = elem.content
                    elem.type = ElementType.TITLE
                    elem.level = 0
                    break
            
            return ParseResult(
                success=True,
                elements=elements,
                format=doc_format,
                title=title,
                quality_score=0.3,
                warnings=["Used fallback parsing - structure may be incomplete"]
            )
            
        except Exception as e:
            return ParseResult(
                success=False,
                elements=[],
                format=doc_format,
                errors=[f"Fallback parsing failed: {str(e)}"],
                quality_score=0.0
            )
    
    def _is_table_heavy(self, structure: Dict) -> bool:
        """Check if document is table-heavy"""
        table_count = structure.get('nesting_patterns', {}).get('table_structure', {}).get('total_tables', 0)
        return table_count > 5
    
    def _extract_title_from_elements(self, elements: List[ParsedElement]) -> Optional[str]:
        """Extract title from elements list"""
        for elem in elements:
            if elem.type == ElementType.TITLE:
                return elem.content
        return None
    
    def _calculate_quality_score(self, elements: List[ParsedElement], structure: Dict) -> float:
        """Calculate quality score for parse result"""
        score = 0.0
        
        # Title bonus
        has_title = any(elem.type == ElementType.TITLE for elem in elements)
        if has_title:
            score += 0.3
        
        # Structure bonus
        has_structure = any(elem.type in [ElementType.ARTICLE, ElementType.SECTION] for elem in elements)
        if has_structure:
            score += 0.3
        
        # Element variety bonus
        element_types = set(elem.type for elem in elements)
        type_variety = len(element_types) / len(ElementType)
        score += type_variety * 0.2
        
        # Confidence bonus
        avg_confidence = sum(elem.confidence for elem in elements) / len(elements) if elements else 0
        score += avg_confidence * 0.2
        
        return min(1.0, score)
    
    def _update_stats(self, filename: str, result: ParseResult):
        """Update parsing statistics"""
        self.stats['total_parsed'] += 1
        
        if result.success:
            self.stats['successful_parses'] += 1
        else:
            self.stats['failures'].append({
                'filename': filename,
                'errors': result.errors,
                'format': result.format
            })
        
        # Track format counts
        format_key = result.format.value
        self.stats['format_counts'][format_key] = self.stats['format_counts'].get(format_key, 0) + 1
    
    def get_stats_report(self) -> str:
        """Generate statistics report"""
        success_rate = (self.stats['successful_parses'] / self.stats['total_parsed'] * 100) if self.stats['total_parsed'] > 0 else 0
        
        report = f"""
UNIVERSAL EDGAR PARSER STATISTICS
================================

Total files processed: {self.stats['total_parsed']}
Successful parses: {self.stats['successful_parses']}
Success rate: {success_rate:.1f}%

Format distribution:
"""
        
        for format_name, count in self.stats['format_counts'].items():
            percentage = (count / self.stats['total_parsed'] * 100) if self.stats['total_parsed'] > 0 else 0
            report += f"  {format_name}: {count} ({percentage:.1f}%)\n"
        
        if self.stats['failures']:
            report += f"\nFailures ({len(self.stats['failures'])}):\n"
            for failure in self.stats['failures']:
                report += f"  {failure['filename']}: {failure['errors']}\n"
        
        return report


def test_all_agreements():
    """Test parser on all HTML agreement files"""
    parser = UniversalEDGARParser()
    html_files_dir = Path(__file__).parent / "html_files"
    
    results = {}
    
    print("Testing Universal EDGAR Parser on all agreement files...")
    print("=" * 60)
    
    # Get all HTML files
    html_files = sorted(html_files_dir.glob("*.html"))
    
    for html_file in html_files:
        print(f"\nProcessing: {html_file.name}")
        print("-" * 40)
        
        try:
            # Read file content
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Parse document
            result = parser.parse(content, html_file.name)
            
            # Store result
            results[html_file.name] = result
            
            # Print summary
            if result.success:
                print(f"✅ SUCCESS - Quality: {result.quality_score:.2f}")
                print(f"   Format: {result.format.value}")
                print(f"   Elements: {len(result.elements)}")
                if result.title:
                    print(f"   Title: {result.title[:60]}...")
                
                # Show element type distribution
                type_counts = {}
                for elem in result.elements:
                    type_counts[elem.type.value] = type_counts.get(elem.type.value, 0) + 1
                
                print(f"   Element types: {dict(sorted(type_counts.items()))}")
                
                if result.warnings:
                    print(f"   Warnings: {len(result.warnings)}")
                    
            else:
                print(f"❌ FAILED")
                for error in result.errors:
                    print(f"   Error: {error}")
                    
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
            results[html_file.name] = None
    
    # Print final statistics
    print("\n" + "=" * 60)
    print(parser.get_stats_report())
    
    return results, parser


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Parse single file
        filename = sys.argv[1]
        parser = UniversalEDGARParser()
        
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        result = parser.parse(content, filename)
        
        if result.success:
            print(f"Successfully parsed {filename}")
            print(f"Quality score: {result.quality_score:.2f}")
            print(f"Elements found: {len(result.elements)}")
            if result.title:
                print(f"Title: {result.title}")
        else:
            print(f"Failed to parse {filename}")
            for error in result.errors:
                print(f"Error: {error}")
    else:
        # Test all files
        test_all_agreements()


if __name__ == "__main__":
    main()