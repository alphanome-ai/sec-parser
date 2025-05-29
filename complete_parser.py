#!/usr/bin/env python3
"""
Complete Enhanced EDGAR Agreement Parser
Handles multiple document formats and complex structures
"""

import logging
import re
import sys
import traceback
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup, Tag

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
    children: List["ParsedElement"] = field(default_factory=list)
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
        if content.strip().startswith("<?xml"):
            return self._classify_xml_format(content)

        # Check for DOCTYPE
        if "<!doctype" in content_lower:
            doctype_match = re.search(r"<!doctype\s+(\w+)", content_lower)
            if doctype_match:
                doctype = doctype_match.group(1)
                if doctype in ["html", "html5"]:
                    return DocumentFormat.HTML
                if doctype == "sgml":
                    return DocumentFormat.SGML

        # Check for HTML tags
        if "<html" in content_lower or "</html>" in content_lower:
            # Check if it's wrapped EDGAR format
            if "<document>" in content_lower or "<type>" in content_lower:
                return DocumentFormat.WRAPPED
            return DocumentFormat.HTML

        # Check for data format (like Agreement 6 with ZEQ patterns)
        if any(pattern in content_start for pattern in ["ZEQ=", "CIK=", "ACCESSION="]):
            return DocumentFormat.DATA_FORMAT

        # Check for structured text with tables
        if self._is_structured_text(content):
            return DocumentFormat.TEXT

        return DocumentFormat.HTML  # Default to HTML for processing

    def _classify_xml_format(self, content: str) -> DocumentFormat:
        """Classify XML format"""
        if "<xbrl" in content.lower()[:1000]:
            return DocumentFormat.XML
        if "<document>" in content.lower()[:1000]:
            return DocumentFormat.WRAPPED
        return DocumentFormat.XML

    def _is_structured_text(self, content: str) -> bool:
        """Check if content is structured text"""
        lines = content.split("\n")[:50]

        # Check for table patterns
        table_patterns = [
            r"\|.*\|.*\|",  # Pipe-separated
            r"\t.*\t.*\t",  # Tab-separated
            r"^[-=]+$",     # Horizontal lines
        ]

        table_line_count = 0
        for line in lines:
            if any(re.search(pattern, line) for pattern in table_patterns):
                table_line_count += 1

        return table_line_count > 5


class TitleDetector:
    """Intelligent title detection using multiple strategies"""

    def detect_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Detect document title using multiple strategies"""
        strategies = [
            self._detect_by_style_and_position,
            self._detect_by_content_patterns,
            self._detect_by_html_structure,
        ]

        candidates = []
        for strategy in strategies:
            try:
                result = strategy(soup)
                if result:
                    candidates.extend(result if isinstance(result, list) else [result])
            except Exception as e:
                logger.warning(f"Title detection strategy failed: {e}")

        if not candidates:
            return None

        # Score and return best candidate
        best_candidate = max(candidates, key=lambda x: self._score_title_candidate(x, soup))
        return best_candidate.get_text(separator=" ", strip=True) if best_candidate else None

    def _detect_by_style_and_position(self, soup: BeautifulSoup) -> List[Tag]:
        """Detect title by style and position"""
        candidates = []

        # Look for centered, bold text early in document
        for elem in soup.find_all(["p", "div", "h1", "h2", "h3"], limit=20):
            text = elem.get_text(separator=" ", strip=True)
            if not text or len(text) < 5:
                continue

            # Check for styling that indicates title
            is_centered = (elem.get("align") == "center" or
                          "text-align:center" in str(elem.get("style", "")).lower() or
                          "text-align: center" in str(elem.get("style", "")).lower())

            is_bold = (elem.find(["b", "strong"]) is not None or
                      "font-weight:bold" in str(elem.get("style", "")).lower() or
                      "font-weight: bold" in str(elem.get("style", "")).lower())

            # Check for large font sizes that indicate titles
            style_str = str(elem.get("style", "")).lower()
            has_large_font = any(size in style_str for size in ["font-size:14", "font-size:16", "font-size:18", "font-size: 14", "font-size: 16", "font-size: 18"])

            # Check for agreement keywords
            has_keywords = any(keyword in text.lower() for keyword in [
                "agreement", "contract", "lease", "plan", "amendment", "indenture",
            ])

            if (is_centered or is_bold or has_large_font) and has_keywords and len(text) < 200:
                candidates.append(elem)

        return candidates

    def _detect_by_content_patterns(self, soup: BeautifulSoup) -> List[Tag]:
        """Detect title by content patterns"""
        candidates = []

        # Common agreement title patterns
        title_patterns = [
            r".*\bAGREEMENT\b.*",
            r".*\bCONTRACT\b.*",
            r".*\bLEASE\b.*",
            r".*\bPLAN\b.*",
            r"FORM\s+OF\s+.*",
            r".*\bAMENDMENT\b.*",
        ]

        for elem in soup.find_all(["p", "div", "h1", "h2", "h3"], limit=30):
            text = elem.get_text(separator=" ", strip=True)

            for pattern in title_patterns:
                if re.search(pattern, text, re.IGNORECASE) and len(text) < 300:
                    candidates.append(elem)
                    break

        return candidates

    def _detect_by_html_structure(self, soup: BeautifulSoup) -> List[Tag]:
        """Detect title by HTML structure"""
        candidates = []

        # Check for title in HEAD
        title_tag = soup.find("title")
        if title_tag and title_tag.get_text(separator=" ", strip=True):
            candidates.append(title_tag)

        # Check for first heading tags
        for tag in ["h1", "h2", "h3"]:
            heading = soup.find(tag)
            if heading:
                candidates.append(heading)

        return candidates

    def _score_title_candidate(self, element: Tag, soup: BeautifulSoup) -> float:
        """Score a title candidate"""
        score = 0.0
        text = element.get_text(separator=" ", strip=True)

        # Content scoring
        if "agreement" in text.lower(): score += 5
        if "contract" in text.lower(): score += 4
        if "lease" in text.lower(): score += 4
        if "plan" in text.lower(): score += 3
        if "form of" in text.lower(): score += 3

        # Style scoring
        if element.get("align") == "center": score += 3
        if "center" in str(element.get("style", "")).lower(): score += 3
        if element.find(["b", "strong"]): score += 2
        if "bold" in str(element.get("style", "")).lower(): score += 2

        # Position scoring (earlier is better)
        all_elements = soup.find_all(["p", "div", "h1", "h2", "h3"])
        try:
            position = all_elements.index(element)
            if position < 5: score += 3
            elif position < 10: score += 2
            elif position < 20: score += 1
        except ValueError:
            pass

        # Length scoring (titles should be reasonable length)
        text_len = len(text)
        if 10 <= text_len <= 100: score += 2
        elif text_len > 200: score -= 2

        return score


class UniversalEDGARParser:
    """Universal parser for all EDGAR document formats"""

    def __init__(self):
        self.format_detector = FormatDetector()
        self.title_detector = TitleDetector()

        # Statistics tracking
        self.stats = {
            "total_parsed": 0,
            "successful_parses": 0,
            "format_counts": {},
            "failures": [],
        }

    def parse(self, raw_content: str, filename: str = None) -> ParseResult:
        """Parse document with comprehensive error handling"""
        try:
            logger.info(f"Starting parse of {filename or 'unknown file'}")

            # Step 1: Detect format
            doc_format = self.format_detector.detect_format(raw_content)
            logger.info(f"Detected format: {doc_format}")

            # Step 2: Parse with BeautifulSoup
            soup = BeautifulSoup(raw_content, "html.parser")

            # Step 3: Extract title
            title = self.title_detector.detect_title(soup)

            # Step 4: Extract all elements
            elements = self._extract_elements(soup)

            # Step 5: Classify elements
            classified_elements = self._classify_elements(elements, title)

            # Step 5.5: Merge confidential metadata with following elements
            classified_elements = self._merge_confidential_metadata(classified_elements)
            
            # Step 5.6: Fix signature block grouping and intentional blanks
            classified_elements = self._fix_signature_blocks(classified_elements)

            # Step 6: Calculate quality score
            quality_score = self._calculate_quality_score(classified_elements, title)

            result = ParseResult(
                success=True,
                elements=classified_elements,
                format=doc_format,
                title=title,
                quality_score=quality_score,
                metadata={
                    "element_count": len(classified_elements),
                    "has_title": title is not None,
                    "filename": filename,
                },
            )

            self._update_stats(filename, result)
            return result

        except Exception as e:
            logger.error(f"Parse failed for {filename}: {e!s}")
            logger.error(traceback.format_exc())

            result = ParseResult(
                success=False,
                elements=[],
                format=DocumentFormat.UNKNOWN,
                errors=[str(e)],
                quality_score=0.0,
            )

            self._update_stats(filename, result)
            return result

    def _extract_elements(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract all text elements from document"""
        elements = []

        # Get all elements that contain text
        for elem in soup.find_all(["p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "td", "th", "span"]):
            # Use separator to preserve spaces between inline elements
            text = elem.get_text(separator=" ", strip=True)
            if not text or len(text) < 3:
                continue

            # Skip script and style elements
            if elem.name in ["script", "style"]:
                continue

            element_info = {
                "element": elem,
                "text": text,
                "tag": elem.name,
                "position": len(elements),
                "attributes": dict(elem.attrs) if elem.attrs else {},
            }
            elements.append(element_info)

        return elements

    def _classify_elements(self, elements: List[Dict], title: str) -> List[ParsedElement]:
        """Classify elements into semantic types"""
        classified = []

        for elem_data in elements:
            text = elem_data["text"]
            tag = elem_data["tag"]

            # Determine element type
            element_type = self._determine_element_type(text, tag, title)
            level = self._determine_level(element_type, text)

            parsed_element = ParsedElement(
                type=element_type,
                content=text,
                level=level,
                tag_name=tag,
                attributes=elem_data["attributes"],
                line_number=elem_data["position"],
                confidence=0.8,
            )

            classified.append(parsed_element)

        return classified

    def _determine_element_type(self, text: str, tag: str, title: str) -> ElementType:
        """Determine the semantic type of an element"""
        text_lower = text.lower()

        # Check if this is the title
        if title and text.strip() == title.strip():
            return ElementType.TITLE

        # Check for metadata patterns
        if self._is_metadata(text):
            return ElementType.METADATA

        # Check for section patterns
        if re.match(r"^\s*(article|section)\s+[ivx\d]+", text_lower):
            return ElementType.SECTION

        # Check for numbered sections (various formats)
        if re.match(r"^\s*\d+\.", text):
            return ElementType.SECTION

        # Check for lettered sections
        if re.match(r"^\s*[A-Z]\.", text) and len(text) < 100:
            return ElementType.SECTION

        # Check for schedule/exhibit patterns
        if re.match(r"^\s*(schedule|exhibit)\s+[a-z0-9]+", text_lower):
            return ElementType.SECTION

        # Check for subsections
        if re.match(r"^\s*\([a-z]\)", text):
            return ElementType.SUBSECTION

        # Check for definitions
        if '"' in text and ("means" in text_lower or "defined as" in text_lower):
            return ElementType.DEFINITION

        # Check for signature blocks
        if any(sig in text_lower for sig in ["signature", "executed", "witness whereof"]):
            return ElementType.SIGNATURE

        # Check for party information
        if any(party in text_lower for party in ["parties:", "between", "party of the first part"]):
            return ElementType.PARTY

        # Check for table elements
        if tag in ["td", "th"]:
            return ElementType.TABLE

        # Default to paragraph
        return ElementType.PARAGRAPH

    def _determine_level(self, element_type: ElementType, text: str) -> int:
        """Determine hierarchical level"""
        if element_type == ElementType.TITLE:
            return 0
        if element_type in [ElementType.ARTICLE, ElementType.SECTION]:
            return 1
        if element_type == ElementType.SUBSECTION:
            return 2
        if element_type == ElementType.CLAUSE:
            return 3
        return 4

    def _is_metadata(self, text: str) -> bool:
        """Check if text is metadata"""
        metadata_patterns = [
            r"page\s+\d+",
            r"exhibit\s+\d+",
            r"execution\s+copy",
            r"confidential",
            r"filed\s+with.*commission",
            r"\*+\s*\*+",
            r"^\d+\s*\|\s*\d+$",  # Page numbers like "3 | 11"
            r"^\d+\s*/\s*\d+$",  # Page numbers like "3 / 11"
            r"^\d+\s*of\s*\d+$", # Page numbers like "3 of 11"
            r"^page\s+\d+\s+of\s+\d+$", # Full page indicators
        ]

        text_lower = text.lower()
        text_clean = text.strip()
        return any(re.search(pattern, text_lower) for pattern in metadata_patterns)

    def _merge_confidential_metadata(self, elements: List[ParsedElement]) -> List[ParsedElement]:
        """Merge confidential metadata with following code sections"""
        if not elements:
            return elements
            
        merged_elements = []
        i = 0
        
        while i < len(elements):
            current = elements[i]
            
            # Check if current element is confidential metadata
            if (current.type == ElementType.METADATA and 
                self._is_confidential_metadata(current.content)):
                
                # Look ahead for code sections to merge (up to 2 elements)
                merge_content = [current.content]
                elements_to_merge = [current]
                j = i + 1
                
                # Merge up to 2 following elements if they contain code references
                while j < len(elements) and len(elements_to_merge) < 3:  # Original + up to 2 more
                    next_elem = elements[j]
                    if self._is_code_reference(next_elem.content):
                        merge_content.append(next_elem.content)
                        elements_to_merge.append(next_elem)
                        j += 1
                    else:
                        break
                
                # If we found elements to merge, create merged element
                if len(elements_to_merge) > 1:
                    merged_element = ParsedElement(
                        type=ElementType.METADATA,
                        content=" ".join(merge_content),
                        level=current.level,
                        tag_name=current.tag_name,
                        attributes=current.attributes,
                        line_number=current.line_number,
                        confidence=current.confidence,
                        metadata={**current.metadata, "merged_count": len(elements_to_merge)}
                    )
                    merged_elements.append(merged_element)
                    i = j  # Skip the merged elements
                else:
                    merged_elements.append(current)
                    i += 1
            else:
                merged_elements.append(current)
                i += 1
                
        return merged_elements
    
    def _is_confidential_metadata(self, text: str) -> bool:
        """Check if metadata is confidential treatment related"""
        confidential_patterns = [
            r"confidential\s+treatment",
            r"confidential.*requested",
            r"confidential.*under",
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in confidential_patterns)
    
    def _is_code_reference(self, text: str) -> bool:
        """Check if text contains legal/regulatory code references"""
        code_patterns = [
            r"\d+\s+c\.f\.r\.",  # CFR references
            r"section\s+\d+",    # Section references
            r"sections\s+\d+",   # Sections references
            r"\d+\.\d+[a-z]?\(",  # Numbered subsections like 200.80(b)
            r"\d+\.\d+[a-z]?-\d+", # Numbered sections like 240.24b-2
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in code_patterns)

    def _fix_signature_blocks(self, elements: List[ParsedElement]) -> List[ParsedElement]:
        """Fix signature block grouping and handle intentional blanks"""
        if not elements:
            return elements
            
        # Step 1: Handle intentional blanks first
        for element in elements:
            if self._is_intentional_blank(element.content):
                element.type = ElementType.METADATA
        
        # Step 2: Find signature block candidates
        signature_candidates = self._find_signature_candidates(elements)
        
        # Step 3: Select best signature block (usually the last/primary one)
        if signature_candidates:
            best_signature_block = self._select_best_signature_candidate(signature_candidates)
            
            # Step 4: Reclassify elements in the best signature block
            start_idx, end_idx = best_signature_block
            for i in range(start_idx, end_idx + 1):
                if i < len(elements):
                    elem = elements[i]
                    if self._is_signature_element(elem.content):
                        elem.type = ElementType.SIGNATURE
                    
        return elements
    
    def _is_intentional_blank(self, text: str) -> bool:
        """Check if text is an intentional blank marker"""
        blank_patterns = [
            r'\[\s*intentionally\s+blank\s*\]',
            r'\(\s*intentionally\s+blank\s*\)',
            r'intentionally\s+left\s+blank',
            r'this\s+page\s+intentionally\s+blank',
        ]
        
        text_lower = text.lower().strip()
        return any(re.search(pattern, text_lower) for pattern in blank_patterns)
    
    def _is_signature_start(self, text: str) -> bool:
        """Check if text indicates start of signature block"""
        signature_starts = [
            r'very\s+truly\s+yours',
            r'sincerely\s+yours',
            r'respectfully\s+submitted',
            r'signed\s*:',
            r'executed\s+by',
            r'approved\s+and\s+accepted',
            r'in\s+witness\s+whereof',
        ]
        
        text_lower = text.lower().strip()
        return any(re.search(pattern, text_lower) for pattern in signature_starts)
    
    def _is_signature_related(self, element: ParsedElement, position_in_block: int) -> bool:
        """Check if element is part of signature block"""
        text = element.content.strip()
        text_lower = text.lower()
        
        # Stop conditions - not part of signature
        if len(text) > 200:  # Too long to be signature
            return False
            
        if position_in_block > 15:  # Too far from signature start
            return False
            
        # Check for new section starting
        if re.match(r'^\d+\.', text) or re.match(r'^section\s+\d+', text_lower):
            return False
            
        # Signature-related patterns
        signature_patterns = [
            r'very\s+truly\s+yours',
            r'sincerely',
            r'by\s*:',
            r'name\s*:',
            r'title\s*:',
            r'date\s*:',
            r'/s/',
            r'authorized\s+agent',
            r'secretary',
            r'president',
            r'ceo',
            r'chief\s+executive',
            r'approved\s+and\s+accepted',
            r'corporation',
            r'llc',
            r'inc\.',
            r'company',
            r'signature\s+page',
            r'executed\s+by',
            r'witness\s+whereof',
        ]
        
        # Check if it's signature-related
        for pattern in signature_patterns:
            if re.search(pattern, text_lower):
                return True
                
        # Check if it's a short company/person name (likely signature)
        if len(text) < 50 and any(word in text_lower for word in ['llc', 'inc', 'corp', 'company', 'systems']):
            return True
            
        # Check if it's a person's name pattern
        if len(text) < 30 and ' ' in text and text.count(' ') <= 3:
            # Could be a person's name
            return True
            
        return False
    
    def _find_signature_candidates(self, elements: List[ParsedElement]) -> List[tuple]:
        """Find potential signature block regions"""
        candidates = []
        
        for i, element in enumerate(elements):
            if self._is_signature_start(element.content):
                # Find the end of this signature block
                end_idx = i
                for j in range(i + 1, len(elements)):
                    if (self._is_signature_related_simple(elements[j]) and 
                        j - i < 20):  # Limit signature block size
                        end_idx = j
                    else:
                        # Stop at next section or non-signature content
                        if (elements[j].type == ElementType.SECTION or 
                            len(elements[j].content) > 150):
                            break
                        
                candidates.append((i, end_idx))
                
        return candidates
    
    def _select_best_signature_candidate(self, candidates: List[tuple]) -> tuple:
        """Select the best signature block from candidates"""
        if not candidates:
            return None
            
        # Prefer the last signature block (main document signature)
        # Usually exhibits have signature blocks earlier, main doc at end
        best_candidate = candidates[-1]
        
        # Score candidates based on position and content quality
        best_score = 0
        for start_idx, end_idx in candidates:
            score = 0
            
            # Later position gets higher score (main signature usually at end)
            score += start_idx * 0.1
            
            # Larger signature blocks get higher score (more complete)
            block_size = end_idx - start_idx + 1
            score += min(block_size * 2, 20)  # Cap at 20 points
            
            if score > best_score:
                best_score = score
                best_candidate = (start_idx, end_idx)
                
        return best_candidate
    
    def _is_signature_related_simple(self, element: ParsedElement) -> bool:
        """Simple check if element is signature-related (for block detection)"""
        text = element.content.strip().lower()
        
        # Basic signature indicators
        simple_patterns = [
            r'very\s+truly\s+yours',
            r'sincerely',
            r'by\s*:',
            r'/s/',
            r'authorized\s+agent',
            r'signature\s+page',
            r'approved\s+and\s+accepted',
            r'witness\s+whereof',
        ]
        
        # Check for short company/person names
        if (len(element.content) < 50 and 
            any(word in text for word in ['llc', 'inc', 'corp', 'company', 'systems'])):
            return True
            
        # Check patterns
        return any(re.search(pattern, text) for pattern in simple_patterns)

    def _is_signature_element(self, text: str) -> bool:
        """Check if element should be classified as signature"""
        text_lower = text.lower().strip()
        
        signature_element_patterns = [
            r'very\s+truly\s+yours',
            r'sincerely',
            r'by\s*:',
            r'name\s*:',
            r'title\s*:',
            r'date\s*:',
            r'/s/',
            r'authorized\s+agent',
            r'signature\s+page',
            r'executed\s+by',
            r'approved\s+and\s+accepted',
            r'in\s+witness\s+whereof',
        ]
        
        return any(re.search(pattern, text_lower) for pattern in signature_element_patterns)

    def _calculate_quality_score(self, elements: List[ParsedElement], title: str) -> float:
        """Calculate quality score for parse result"""
        score = 0.0

        # Title bonus (25%)
        if title:
            score += 0.25

        # Structure bonus (35%)
        section_count = sum(1 for elem in elements if elem.type in [ElementType.SECTION, ElementType.ARTICLE])
        if section_count > 0:
            score += 0.25
        if section_count > 5:
            score += 0.10  # Extra bonus for well-structured documents

        # Element variety bonus (20%)
        element_types = set(elem.type for elem in elements)
        type_variety = len(element_types) / len(ElementType)
        score += type_variety * 0.20

        # Content quality bonus (20%)
        content_elements = [elem for elem in elements if elem.type == ElementType.PARAGRAPH]
        metadata_elements = [elem for elem in elements if elem.type == ElementType.METADATA]

        if len(content_elements) > 5:
            score += 0.10

        # Penalize excessive metadata
        if len(elements) > 0:
            metadata_ratio = len(metadata_elements) / len(elements)
            if metadata_ratio < 0.3:  # Good metadata ratio
                score += 0.10
            elif metadata_ratio > 0.5:  # Too much metadata
                score -= 0.05

        return min(1.0, max(0.0, score))

    def _update_stats(self, filename: str, result: ParseResult):
        """Update parsing statistics"""
        self.stats["total_parsed"] += 1

        if result.success:
            self.stats["successful_parses"] += 1
        else:
            self.stats["failures"].append({
                "filename": filename,
                "errors": result.errors,
                "format": result.format,
            })

        # Track format counts
        format_key = result.format.value
        self.stats["format_counts"][format_key] = self.stats["format_counts"].get(format_key, 0) + 1

    def get_stats_report(self) -> str:
        """Generate statistics report"""
        total = self.stats["total_parsed"]
        success = self.stats["successful_parses"]
        success_rate = (success / total * 100) if total > 0 else 0

        report = f"""
UNIVERSAL EDGAR PARSER STATISTICS
================================

Total files processed: {total}
Successful parses: {success}
Success rate: {success_rate:.1f}%

Format distribution:
"""

        for format_name, count in self.stats["format_counts"].items():
            percentage = (count / total * 100) if total > 0 else 0
            report += f"  {format_name}: {count} ({percentage:.1f}%)\n"

        if self.stats["failures"]:
            report += f"\nFailures ({len(self.stats['failures'])}):\n"
            for failure in self.stats["failures"]:
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
            with open(html_file, encoding="utf-8", errors="ignore") as f:
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
                    print(f"   Title: {result.title[:80]}...")

                # Show element type distribution
                type_counts = {}
                for elem in result.elements:
                    type_counts[elem.type.value] = type_counts.get(elem.type.value, 0) + 1

                print(f"   Element types: {dict(sorted(type_counts.items()))}")

                if result.warnings:
                    print(f"   Warnings: {len(result.warnings)}")

            else:
                print("❌ FAILED")
                for error in result.errors:
                    print(f"   Error: {error}")

        except Exception as e:
            print(f"❌ EXCEPTION: {e!s}")
            results[html_file.name] = None

    # Print final statistics
    print("\n" + "=" * 60)
    print(parser.get_stats_report())

    # Print detailed results
    print("\nDETAILED RESULTS:")
    print("=" * 60)

    for filename, result in results.items():
        if result and result.success:
            print(f"\n{filename}:")
            print(f"  Quality: {result.quality_score:.2f}")
            if result.title:
                print(f"  Title: {result.title}")
            print(f"  Elements: {len(result.elements)}")

    return results, parser


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Parse single file
        filename = sys.argv[1]
        parser = UniversalEDGARParser()

        with open(filename, encoding="utf-8", errors="ignore") as f:
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
