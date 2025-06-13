#!/usr/bin/env python3
"""
Enhanced EDGAR Agreement Parser
Handles multiple document formats and complex structures
"""

import re
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from bs4 import BeautifulSoup, Tag
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentFormat(Enum):
    """Document format types"""
    HTML = "html"
    SGML = "sgml"
    XML = "xml"
    WRAPPED = "wrapped"
    TEXT = "text"
    DATA_FORMAT = "data_format"
    UNKNOWN = "unknown"


class ElementType(Enum):
    """Element types in legal documents"""
    TITLE = "title"
    ARTICLE = "article"
    SECTION = "section"
    SUBSECTION = "subsection"
    CLAUSE = "clause"
    PARAGRAPH = "paragraph"
    TABLE = "table"
    METADATA = "metadata"
    SIGNATURE = "signature"
    EXHIBIT = "exhibit"
    SCHEDULE = "schedule"
    DEFINITION = "definition"
    RECITAL = "recital"
    PARTY = "party"


@dataclass
class ParsedElement:
    """Represents a parsed document element"""
    type: ElementType
    content: str
    level: int
    tag_name: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)
    children: List['ParsedElement'] = field(default_factory=list)
    line_number: int = 0
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParseResult:
    """Result of parsing operation"""
    success: bool
    elements: List[ParsedElement]
    format: DocumentFormat
    title: Optional[str] = None
    tree: Optional[ParsedElement] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0


class FormatDetector:
    """Detects document format"""
    
    def detect_format(self, content: str) -> DocumentFormat:
        """Detect the format of the document"""
        if not content or len(content.strip()) == 0:
            return DocumentFormat.UNKNOWN
            
        content_lower = content[:5000].lower()
        content_start = content[:1000]
        
        # Check for XML
        if content.strip().startswith('<?xml'):
            return self._classify_xml_format(content)
            
        # Check for DOCTYPE
        if '<!doctype' in content_lower:
            doctype_match = re.search(r'<!doctype\s+(\w+)', content_lower)
            if doctype_match:
                doctype = doctype_match.group(1)
                if doctype in ['html', 'html5']:
                    return DocumentFormat.HTML
                elif doctype == 'sgml':
                    return DocumentFormat.SGML
                    
        # Check for HTML tags
        if '<html' in content_lower or '</html>' in content_lower:
            # Check if it's wrapped EDGAR format
            if '<document>' in content_lower or '<type>' in content_lower:
                return DocumentFormat.WRAPPED
            return DocumentFormat.HTML
            
        # Check for data format (like Agreement 6 with ZEQ patterns)
        if any(pattern in content_start for pattern in ['ZEQ=', 'CIK=', 'ACCESSION=']):
            return DocumentFormat.DATA_FORMAT
            
        # Check for structured text with tables
        if self._is_structured_text(content):
            return DocumentFormat.TEXT
            
        return DocumentFormat.UNKNOWN
    
    def _classify_xml_format(self, content: str) -> DocumentFormat:
        """Classify XML format"""
        if '<xbrl' in content.lower()[:1000]:
            return DocumentFormat.XML
        elif '<document>' in content.lower()[:1000]:
            return DocumentFormat.WRAPPED
        return DocumentFormat.XML
    
    def _is_structured_text(self, content: str) -> bool:
        """Check if content is structured text"""
        lines = content.split('\n')[:50]
        
        # Check for table patterns
        table_patterns = [
            r'\|.*\|.*\|',  # Pipe-separated
            r'\t.*\t.*\t',  # Tab-separated
            r'^[-=]+$',     # Horizontal lines
        ]
        
        table_line_count = 0
        for line in lines:
            if any(re.search(pattern, line) for pattern in table_patterns):
                table_line_count += 1
                
        return table_line_count > 5


class FormatConverter:
    """Converts various formats to normalized HTML"""
    
    def convert(self, content: str, format: DocumentFormat) -> str:
        """Convert content to normalized HTML"""
        if format == DocumentFormat.HTML:
            return content
        elif format == DocumentFormat.SGML:
            return self._convert_sgml_to_html(content)
        elif format == DocumentFormat.WRAPPED:
            return self._unwrap_edgar_document(content)
        elif format == DocumentFormat.DATA_FORMAT:
            return self._convert_data_format(content)
        elif format == DocumentFormat.TEXT:
            return self._convert_text_to_html(content)
        elif format == DocumentFormat.XML:
            return self._extract_html_from_xml(content)
        else:
            return content
    
    def _convert_sgml_to_html(self, content: str) -> str:
        """Convert SGML to HTML"""
        # Replace SGML entities
        replacements = {
            '&nbsp;': ' ',
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&apos;': "'",
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
            
        # Convert deprecated tags
        tag_replacements = {
            '<center>': '<div style="text-align: center;">',
            '</center>': '</div>',
            '<font': '<span',
            '</font>': '</span>',
        }
        
        for old, new in tag_replacements.items():
            content = content.replace(old, new)
            
        return content
    
    def _unwrap_edgar_document(self, content: str) -> str:
        """Extract HTML from EDGAR wrapped document"""
        # Try to find HTML content between tags
        patterns = [
            (r'<HTML>(.*?)</HTML>', re.DOTALL | re.IGNORECASE),
            (r'<DOCUMENT>(.*?)</DOCUMENT>', re.DOTALL | re.IGNORECASE),
            (r'<TEXT>(.*?)</TEXT>', re.DOTALL | re.IGNORECASE),
        ]
        
        for pattern, flags in patterns:
            match = re.search(pattern, content, flags)
            if match:
                return match.group(1)
                
        # If no wrapper found, return original
        return content
    
    def _convert_data_format(self, content: str) -> str:
        """Convert data format to HTML"""
        lines = content.split('\n')
        html_parts = ['<html><body>']
        
        current_section = []
        for line in lines:
            # Look for section markers
            if re.match(r'^[A-Z][A-Z\s]+$', line.strip()) and len(line.strip()) > 3:
                if current_section:
                    html_parts.append('<div>' + '<br>'.join(current_section) + '</div>')
                    current_section = []
                html_parts.append(f'<h2>{line.strip()}</h2>')
            else:
                current_section.append(line)
                
        if current_section:
            html_parts.append('<div>' + '<br>'.join(current_section) + '</div>')
            
        html_parts.append('</body></html>')
        return '\n'.join(html_parts)
    
    def _convert_text_to_html(self, content: str) -> str:
        """Convert structured text to HTML"""
        lines = content.split('\n')
        html_parts = ['<html><body>']
        
        in_table = False
        table_lines = []
        
        for line in lines:
            # Check for table patterns
            if '|' in line or '\t' in line:
                if not in_table:
                    in_table = True
                    table_lines = []
                table_lines.append(line)
            else:
                if in_table:
                    # Convert table to HTML
                    html_parts.append(self._convert_table_to_html(table_lines))
                    in_table = False
                    table_lines = []
                    
                # Regular line
                if line.strip():
                    html_parts.append(f'<p>{line}</p>')
                    
        if in_table and table_lines:
            html_parts.append(self._convert_table_to_html(table_lines))
            
        html_parts.append('</body></html>')
        return '\n'.join(html_parts)
    
    def _convert_table_to_html(self, lines: List[str]) -> str:
        """Convert text table to HTML table"""
        html = ['<table border="1">']
        
        for i, line in enumerate(lines):
            # Determine separator
            if '|' in line:
                cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            else:
                cells = [cell.strip() for cell in line.split('\t') if cell.strip()]
                
            if cells:
                row_tag = 'th' if i == 0 else 'td'
                html.append('<tr>')
                for cell in cells:
                    html.append(f'<{row_tag}>{cell}</{row_tag}>')
                html.append('</tr>')
                
        html.append('</table>')
        return '\n'.join(html)
    
    def _extract_html_from_xml(self, content: str) -> str:
        """Extract HTML content from XML"""
        # Try to parse as XML and extract HTML content
        try:
            soup = BeautifulSoup(content, 'xml')
            # Look for HTML content in various locations
            html_content = soup.find('html')
            if html_content:
                return str(html_content)
            
            # Look for text content
            text_content = soup.find('text')
            if text_content:
                return str(text_content)
                
        except Exception:
            pass
            
        return content


class HTMLExtractor:
    """Robust HTML content extraction"""
    
    def extract_content(self, raw_content: str) -> Optional[str]:
        """Extract HTML content with multiple strategies"""
        strategies = [
            self._extract_direct_html,
            self._extract_between_tags,
            self._extract_after_headers,
            self._extract_by_content_detection,
            self._extract_last_resort,
        ]
        
        for strategy in strategies:
            try:
                result = strategy(raw_content)
                if result and self._validate_extraction(result):
                    logger.info(f"Extraction succeeded with strategy: {strategy.__name__}")
                    return result
            except Exception as e:
                logger.warning(f"Strategy {strategy.__name__} failed: {e}")
                
        return None
    
    def _extract_direct_html(self, content: str) -> Optional[str]:
        """Try direct HTML extraction"""
        # Look for standard HTML document
        if '<html' in content.lower() and '</html>' in content.lower():
            return content
        return None
    
    def _extract_between_tags(self, content: str) -> Optional[str]:
        """Extract content between specific tags"""
        tag_pairs = [
            ('<HTML>', '</HTML>'),
            ('<html>', '</html>'),
            ('<DOCUMENT>', '</DOCUMENT>'),
            ('<TEXT>', '</TEXT>'),
        ]
        
        for start_tag, end_tag in tag_pairs:
            start_idx = content.find(start_tag)
            if start_idx != -1:
                end_idx = content.find(end_tag, start_idx)
                if end_idx != -1:
                    return content[start_idx:end_idx + len(end_tag)]
                    
        return None
    
    def _extract_after_headers(self, content: str) -> Optional[str]:
        """Extract content after EDGAR headers"""
        # Look for common EDGAR header end markers
        markers = [
            '<HTML>',
            '<html>',
            '- ---------------',
            '</IMS-HEADER>',
            '</SEC-HEADER>',
        ]
        
        for marker in markers:
            idx = content.find(marker)
            if idx != -1:
                return content[idx:]
                
        return None
    
    def _extract_by_content_detection(self, content: str) -> Optional[str]:
        """Detect HTML content by patterns"""
        # Look for HTML-like patterns
        html_pattern = re.search(r'<[^>]+>.*?</[^>]+>', content, re.DOTALL)
        if html_pattern:
            # Find the start of HTML content
            start = html_pattern.start()
            # Go back to find document start
            while start > 0 and content[start-1] != '\n':
                start -= 1
            return content[start:]
            
        return None
    
    def _extract_last_resort(self, content: str) -> Optional[str]:
        """Last resort extraction"""
        # Remove obvious non-HTML headers
        lines = content.split('\n')
        html_started = False
        cleaned_lines = []
        
        for line in lines:
            if not html_started:
                if any(tag in line.lower() for tag in ['<html', '<body', '<div', '<p', '<table']):
                    html_started = True
                    cleaned_lines.append(line)
            else:
                cleaned_lines.append(line)
                
        if cleaned_lines:
            return '\n'.join(cleaned_lines)
            
        return content
    
    def _validate_extraction(self, content: str) -> bool:
        """Validate extracted content"""
        if not content or len(content.strip()) < 100:
            return False
            
        # Check for minimal HTML structure
        content_lower = content.lower()
        has_tags = any(tag in content_lower for tag in ['<p', '<div', '<table', '<h', '<span'])
        
        # Check for agreement keywords
        has_keywords = any(keyword in content_lower for keyword in [
            'agreement', 'contract', 'party', 'parties', 'whereas', 
            'section', 'article', 'exhibit', 'schedule'
        ])
        
        return has_tags or has_keywords


