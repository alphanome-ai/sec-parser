#!/usr/bin/env python3
"""Legal Agreement Parser V5 - Fresh instances for each document
- Fix the single-use step limitation
- Create new parser instance for each document
- All improvements from V4
- Better error handling.
"""

import re
from collections import defaultdict
from typing import Any, Callable, Optional

from sec_parser.processing_engine.core import AbstractSemanticElementParser
from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.processing_steps.abstract_classes.abstract_elementwise_processing_step import (
    AbstractElementwiseProcessingStep,
)
from sec_parser.processing_steps.abstract_classes.abstract_processing_step import (
    AbstractProcessingStep,
)
from sec_parser.processing_steps.empty_element_classifier import EmptyElementClassifier
from sec_parser.processing_steps.individual_semantic_element_extractor.single_element_checks.abstract_single_element_check import (
    AbstractSingleElementCheck,
)
from sec_parser.processing_steps.table_classifier import TableClassifier
from sec_parser.processing_steps.table_of_contents_classifier import (
    TableOfContentsClassifier,
)
from sec_parser.processing_steps.text_classifier import TextClassifier
from sec_parser.processing_steps.text_element_merger import TextElementMerger
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import (
    IrrelevantElement,
    NotYetClassifiedElement,
    TextElement,
)
from sec_parser.semantic_elements.table_element.table_element import TableElement


# Enhanced Semantic Elements (same as V3 but with improvements)
class AgreementTitleElement(AbstractSemanticElement):
    """Main agreement title."""



class ArticleElement(AbstractSemanticElement):
    """Article-level sections."""

    def __init__(self, html_tag: HtmlTag, article_number: str = "", article_title: str = "", **kwargs) -> None:
        super().__init__(html_tag, **kwargs)
        self.article_number = article_number
        self.article_title = article_title
        self.level = 1


class SectionElement(AbstractSemanticElement):
    """Numbered sections with normalized format."""

    def __init__(self, html_tag: HtmlTag, section_number: str = "", section_title: str = "", level: int = 1, **kwargs) -> None:
        super().__init__(html_tag, **kwargs)
        self.section_number = self._normalize_section_number(section_number)
        self.section_title = section_title
        self.level = level

    def _normalize_section_number(self, number: str) -> str:
        """Normalize section numbers to consistent format."""
        # If it's just a number, add "Section" prefix
        if re.match(r"^\d+(?:\.\d+)*$", number.strip()):
            return f"Section {number}"
        return number


class ClauseElement(AbstractSemanticElement):
    """Clauses with enhanced detection."""

    def __init__(self, html_tag: HtmlTag, clause_id: str = "", clause_text: str = "", level: int = 2, **kwargs) -> None:
        super().__init__(html_tag, **kwargs)
        self.clause_id = clause_id
        self.clause_text = clause_text
        self.level = level


class HeadingElement(AbstractSemanticElement):
    """Section headings."""

    def __init__(self, html_tag: HtmlTag, heading_text: str = "", level: int = 1, **kwargs) -> None:
        super().__init__(html_tag, **kwargs)
        self.heading_text = heading_text
        self.level = level


class ContentTextElement(AbstractSemanticElement):
    """Content text."""



# Legal content elements
class DefinitionElement(AbstractSemanticElement):
    """Definitions."""

    def __init__(self, html_tag: HtmlTag, term: str = "", definition: str = "", **kwargs) -> None:
        super().__init__(html_tag, **kwargs)
        self.term = term
        self.definition = definition


class PartyElement(AbstractSemanticElement):
    """Contract parties."""

    def __init__(self, html_tag: HtmlTag, party_name: str = "", party_type: str = "", **kwargs) -> None:
        super().__init__(html_tag, **kwargs)
        self.party_name = party_name
        self.party_type = party_type


class RecitalElement(AbstractSemanticElement):
    """WHEREAS clauses."""



class SignatureBlockElement(AbstractSemanticElement):
    """Signature blocks."""



class ExhibitElement(AbstractSemanticElement):
    """Exhibits and attachments."""

    def __init__(self, html_tag: HtmlTag, exhibit_id: str = "", exhibit_title: str = "", **kwargs) -> None:
        super().__init__(html_tag, **kwargs)
        self.exhibit_id = exhibit_id
        self.exhibit_title = exhibit_title


# Enhanced metadata elements
class MetadataElement(IrrelevantElement):
    """Base metadata class with tracking."""

    metadata_type = "generic"


class ExhibitStampElement(MetadataElement):
    """Exhibit stamps."""

    metadata_type = "exhibit_stamp"


class ExecutionStampElement(MetadataElement):
    """Execution stamps."""

    metadata_type = "execution_stamp"


class PageNumberMetadataElement(MetadataElement):
    """Page numbers."""

    metadata_type = "page_number"


class SignaturePageFollowsElement(MetadataElement):
    """Signature page markers."""

    metadata_type = "signature_follows"


class PageHeaderElement(MetadataElement):
    """Page headers."""

    metadata_type = "page_header"


# V4 Processing Steps
class ImprovedMetadataRemover(AbstractElementwiseProcessingStep):
    """Enhanced metadata removal with better patterns."""

    def __init__(self, types_to_process=None) -> None:
        super().__init__(types_to_process=types_to_process or {NotYetClassifiedElement, TextElement})
        self.metadata_stats = defaultdict(int)

    def _process_element(self, element: AbstractSemanticElement, context=None) -> Optional[AbstractSemanticElement]:
        if not element.html_tag:
            return element

        text_content = element.html_tag.text.strip()

        # Check metadata patterns
        metadata_result = self._identify_metadata(text_content)

        if metadata_result:
            metadata_type, metadata_class = metadata_result
            self.metadata_stats[metadata_type] += 1
            return metadata_class(element.html_tag)

        return element

    def _identify_metadata(self, text: str) -> Optional[tuple[str, type]]:
        """Enhanced metadata identification."""
        text_stripped = text.strip()
        text_lower = text.lower().strip()

        # Exhibit/Document stamps (more patterns)
        exhibit_patterns = [
            r"^Exhibit\s+\d+(\.\d+)?(?:\s|$)",
            r"^EX-?\d+(\.\d+)?(?:\s|$)",
            r"^EXHIBIT\s+[A-Z0-9]+(?:\s|$)",
            r"^Schedule\s+[A-Z0-9]+(?:\s|$)",
            r"^Annex\s+[A-Z0-9]+(?:\s|$)",
            r"^Appendix\s+[A-Z0-9]+(?:\s|$)",
            r"^Attachment\s+[A-Z0-9]+(?:\s|$)",
        ]
        for pattern in exhibit_patterns:
            if re.match(pattern, text_stripped, re.IGNORECASE):
                return ("exhibit_stamp", ExhibitStampElement)

        # Execution stamps
        execution_keywords = [
            "execution version", "execution copy", "execution draft",
            "final execution", "executed version", "conformed copy",
            "draft", "preliminary", "confidential", "strictly confidential",
        ]
        if any(keyword in text_lower for keyword in execution_keywords):
            if len(text.split()) <= 8:  # Short phrases
                return ("execution_stamp", ExecutionStampElement)

        # Page numbers (enhanced patterns)
        page_patterns = [
            (r"^Page\s+\d+\s+of\s+\d+$", 20),
            (r"^-\s*\d+\s*-$", 10),
            (r"^\d+$", 3),
            (r"^PAGE\s+\d+$", 10),
            (r"^\[\s*\d+\s*\]$", 10),
            (r"^Page\s+\d+$", 10),
            (r"^\d+\s+of\s+\d+$", 10),
        ]
        for pattern, max_len in page_patterns:
            if re.match(pattern, text_stripped, re.IGNORECASE):
                if len(text_stripped) <= max_len:
                    return ("page_number", PageNumberMetadataElement)

        # Page headers (company names with page numbers)
        if "page" in text_lower and re.search(r"\d+\s+of\s+\d+|\bpage\s+\d+", text_lower):
            if len(text.split("\n")) <= 3:  # Multi-line headers
                return ("page_header", PageHeaderElement)

        # Signature page markers
        signature_markers = [
            r"\*+\s*signature\s+page\s+follows\s*\*+",
            r"\[\s*signature\s+page\s+follows\s*\]",
            r"signature\s+page\s+to\s+follow",
            r"signatures\s+on\s+following\s+page",
            r"remainder\s+of\s+(?:this\s+)?page\s+intentionally\s+left\s+blank",
            r"intentionally\s+left\s+blank",
            r"\[this\s+page\s+intentionally\s+left\s+blank\]",
            r"end\s+of\s+page",
            r"\*+\s*\*+\s*\*+",  # ***
        ]
        for pattern in signature_markers:
            if re.search(pattern, text_lower):
                return ("signature_follows", SignaturePageFollowsElement)

        # Table of contents
        if text_lower in ["table of contents", "contents", "index", "toc"]:
            return ("toc", MetadataElement)

        return None

    def get_stats(self) -> dict[str, int]:
        """Return metadata removal statistics."""
        return dict(self.metadata_stats)


class SmartSectionClassifier(AbstractElementwiseProcessingStep):
    """Smarter section classification with deduplication."""

    def __init__(self, types_to_process=None) -> None:
        super().__init__(types_to_process=types_to_process or {NotYetClassifiedElement, TextElement, TableElement})
        self.seen_sections = set()  # Track seen sections to avoid duplicates
        self.section_count = 0
        self.article_count = 0

    def _process_element(self, element: AbstractSemanticElement, context=None) -> Optional[AbstractSemanticElement]:
        if not element.html_tag:
            return element

        # Handle tables
        if element.html_tag.name.lower() == "table":
            result = self._process_table_element(element)
            if result and isinstance(result, (ArticleElement, SectionElement)):
                # Check for duplicates
                key = self._get_section_key(result)
                if key not in self.seen_sections:
                    self.seen_sections.add(key)
                    return result
            return result

        # Handle text
        text_content = element.html_tag.text.strip()

        # Try to extract structured elements
        result = self._extract_structured_element(text_content, element.html_tag)

        if result and isinstance(result, (ArticleElement, SectionElement)):
            # Check for duplicates
            key = self._get_section_key(result)
            if key not in self.seen_sections:
                self.seen_sections.add(key)
                return result
            return element  # Skip duplicate

        return result if result else element

    def _get_section_key(self, element) -> str:
        """Generate unique key for section/article."""
        if isinstance(element, ArticleElement):
            return f"article:{element.article_number}"
        if isinstance(element, SectionElement):
            return f"section:{element.section_number}"
        return ""

    def _extract_structured_element(self, text: str, html_tag: HtmlTag):
        """Extract article or section from text."""
        # Check for Article
        article_patterns = [
            r"^(ARTICLE|Article)\s+([IVX]+|\d+)(?:\s*[-–—.]\s*(.*))?",
        ]

        for pattern in article_patterns:
            match = re.match(pattern, text.strip())
            if match:
                self.article_count += 1
                article_num = f"{match.group(1)} {match.group(2)}"
                article_title = match.group(3).strip() if match.group(3) else ""
                return ArticleElement(
                    html_tag,
                    article_number=article_num,
                    article_title=article_title,
                )

        # Check for Section
        section_patterns = [
            (r"^(Section)\s+(\d+(?:\.\d+)*)(?:\s*[-–—.]\s*(.*))?", "Section"),
            (r"^(\d+(?:\.\d+)*)\s*\.(?:\s+(.*))?", "number"),
        ]

        for pattern, pattern_type in section_patterns:
            match = re.match(pattern, text.strip())
            if match:
                self.section_count += 1

                if pattern_type == "Section":
                    section_num = f"Section {match.group(2)}"
                    section_title = match.group(3).strip() if match.group(3) else ""
                else:
                    section_num = match.group(1)
                    section_title = match.group(2).strip() if match.group(2) else ""

                level = len(section_num.split("."))

                return SectionElement(
                    html_tag,
                    section_number=section_num,
                    section_title=section_title,
                    level=level,
                )

        return None

    def _process_table_element(self, element: AbstractSemanticElement):
        """Process table for sections with better logic."""
        try:
            if not hasattr(element.html_tag, "_bs4"):
                return element

            tds = element.html_tag._bs4.find_all("td")

            if len(tds) >= 2:
                first_cell = tds[0].get_text().strip()
                second_cell = tds[1].get_text().strip()

                # Try section patterns on first cell
                if re.match(r"^\d+\.?$", first_cell):
                    # This is likely a section number
                    section_num = first_cell.rstrip(".")
                    section_title = second_cell

                    self.section_count += 1
                    return SectionElement(
                        element.html_tag,
                        section_number=section_num,
                        section_title=section_title,
                        level=1,
                    )

                # Try combined text
                combined = f"{first_cell} {second_cell}"
                result = self._extract_structured_element(combined, element.html_tag)
                if result:
                    return result

                # Check for signatures
                if self._is_signature_table(first_cell, second_cell):
                    return SignatureBlockElement(element.html_tag)

        except Exception:
            pass

        return element

    def _is_signature_table(self, cell1: str, cell2: str) -> bool:
        """Enhanced signature detection."""
        combined_lower = (cell1 + " " + cell2).lower()
        signature_words = [
            "by:", "/s/", "signature", "name:", "title:", "date:",
            "authorized", "executed", "witness", "acknowledged",
        ]

        # Count how many signature words appear
        word_count = sum(1 for word in signature_words if word in combined_lower)

        # Need at least 2 signature-related words
        return word_count >= 2


class EnhancedClauseClassifier(AbstractElementwiseProcessingStep):
    """Better clause detection including inline clauses."""

    def __init__(self, types_to_process=None) -> None:
        super().__init__(types_to_process=types_to_process or {NotYetClassifiedElement, TextElement})
        self.clause_count = 0

    def _process_element(self, element: AbstractSemanticElement, context=None) -> Optional[AbstractSemanticElement]:
        if not element.html_tag:
            return element

        text_content = element.html_tag.text.strip()

        # Check for clause patterns
        clause_info = self._extract_clause(text_content)

        if clause_info:
            self.clause_count += 1
            clause_id, clause_text, level = clause_info
            return ClauseElement(
                element.html_tag,
                clause_id=clause_id,
                clause_text=clause_text,
                level=level,
            )

        return element

    def _extract_clause(self, text: str) -> Optional[tuple[str, str, int]]:
        """Enhanced clause extraction."""
        # Comprehensive clause patterns
        clause_patterns = [
            # Parenthetical format
            (r"^\(([a-z])\)(?:\s+(.*))?", 2),           # (a) text
            (r"^\(([A-Z])\)(?:\s+(.*))?", 3),           # (A) text
            (r"^\((\d+)\)(?:\s+(.*))?", 3),             # (1) text
            (r"^\(([ivxlcdm]+)\)(?:\s+(.*))?", 4),      # (i) text - expanded roman

            # Dot format (for certain styles)
            (r"^([a-z])\.(?:\s+(.*))?", 2),             # a. text
            (r"^([A-Z])\.(?:\s+(.*))?", 3),             # A. text
            (r"^([ivxlcdm]+)\.(?:\s+(.*))?", 4),        # i. text

            # Special patterns for embedded clauses
            (r"^[;,]\s*\(([a-z])\)(?:\s+(.*))?", 2),    # , (a) text
            (r"^[;,]\s*\((\d+)\)(?:\s+(.*))?", 3),      # , (1) text
        ]

        for pattern, level in clause_patterns:
            match = re.match(pattern, text, re.IGNORECASE if "ivx" in pattern else 0)
            if match:
                clause_id = match.group(1)

                # Format clause ID based on pattern
                clause_id = f"({clause_id})" if "(" in pattern else f"{clause_id}."

                clause_text = match.group(2).strip() if match.group(2) else ""

                # Additional validation - ensure it's not a full section
                if self._is_likely_clause(text, clause_text):
                    return (clause_id, clause_text, level)

        return None

    def _is_likely_clause(self, full_text: str, clause_text: str) -> bool:
        """Validate that this is likely a clause, not a section."""
        # Clauses are typically shorter
        if len(full_text) > 500:  # Very long = probably not a clause header
            return False

        # Check if it looks like a section title instead
        section_words = ["section", "article", "chapter", "part"]
        return not any(word in full_text.lower()[:50] for word in section_words)


class LegalContentClassifierV4(AbstractElementwiseProcessingStep):
    """Enhanced legal content classification."""

    def __init__(self, types_to_process=None) -> None:
        super().__init__(types_to_process=types_to_process or {NotYetClassifiedElement, TextElement})

    def _process_element(self, element: AbstractSemanticElement, context=None) -> Optional[AbstractSemanticElement]:
        if not element.html_tag:
            return element

        text_content = element.html_tag.text.strip()

        # Check patterns in order of specificity

        # WHEREAS clauses
        if self._is_recital(text_content):
            return RecitalElement(element.html_tag)

        # Definitions
        definition_info = self._extract_definition(text_content)
        if definition_info:
            term, definition = definition_info
            return DefinitionElement(
                element.html_tag,
                term=term,
                definition=definition,
            )

        # Party identification
        party_info = self._extract_party(text_content)
        if party_info:
            party_name, party_type = party_info
            return PartyElement(
                element.html_tag,
                party_name=party_name,
                party_type=party_type,
            )

        # Exhibit references
        exhibit_info = self._extract_exhibit_reference(text_content)
        if exhibit_info:
            exhibit_id, exhibit_title = exhibit_info
            return ExhibitElement(
                element.html_tag,
                exhibit_id=exhibit_id,
                exhibit_title=exhibit_title,
            )

        return element

    def _is_recital(self, text: str) -> bool:
        """Check if text is a recital."""
        # More flexible WHEREAS detection
        recital_patterns = [
            r"^WHEREAS[,:]?\s",
            r"^Whereas[,:]?\s",
            r"^NOW,?\s+THEREFORE",
            r"^WITNESSETH[,:]?\s",
        ]

        return any(re.match(pattern, text.strip()) for pattern in recital_patterns)

    def _extract_definition(self, text: str) -> Optional[tuple[str, str]]:
        """Enhanced definition extraction."""
        patterns = [
            # Standard patterns
            r'"([^"]+)"\s+(?:means?|shall\s+mean)\s+(.+)',
            r'"([^"]+)"\s+(?:has\s+the\s+meaning|shall\s+have\s+the\s+meaning)\s+(.+)',
            r'(?:the\s+)?term\s+"([^"]+)"\s+(?:means?|refers?\s+to)\s+(.+)',

            # Parenthetical definitions
            r'"([^"]+)"\s*\((?:as\s+)?defined\s+(?:herein|below|above)\)',
            r'"([^"]+)"\s*\((?:the\s+)?"[^"]+"\)',

            # With or without quotes
            r"\b([A-Z][a-zA-Z\s]+?)\s+(?:means?|shall\s+mean)\s+(.+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text[:500], re.IGNORECASE)  # Check first 500 chars
            if match:
                term = match.group(1).strip()
                definition = match.group(2).strip() if len(match.groups()) > 1 else text

                # Validate it's a real definition
                if len(term) > 2 and len(term.split()) <= 5:  # Reasonable term length
                    return (term, definition)

        return None

    def _extract_party(self, text: str) -> Optional[tuple[str, str]]:
        """Enhanced party extraction."""
        # Multiple patterns for party identification
        patterns = [
            # Standard format: Name, a Delaware corporation
            r"([A-Z][^,]{2,50}?),\s+a\s+([^(,]{3,40}(?:\([^)]+\))?)",

            # With quotes: "Company", a corporation
            r'"([^"]+)",\s+a\s+([^(,]{3,40})',

            # Between format: between X and Y
            r"between\s+([A-Z][^,\s]{2,40}?)\s+(?:and|AND)\s+([A-Z][^,\s]{2,40})",

            # By and between
            r"by\s+and\s+between\s+([A-Z][^,]{2,40}?)\s+and\s+([A-Z][^,]{2,40})",
        ]

        for pattern in patterns:
            match = re.search(pattern, text[:300])  # Check beginning of text
            if match and len(match.groups()) >= 2:
                party_name = match.group(1).strip()
                party_type = match.group(2).strip()

                # Validate party type
                entity_types = [
                    "corporation", "company", "llc", "partnership",
                    "trust", "individual", "bank", "fund", "lp", "inc",
                ]

                if any(entity in party_type.lower() for entity in entity_types):
                    return (party_name, party_type)

        return None

    def _extract_exhibit_reference(self, text: str) -> Optional[tuple[str, str]]:
        """Enhanced exhibit extraction."""
        patterns = [
            r"attached\s+(?:hereto\s+)?as\s+(Exhibit|Schedule|Annex|Appendix)\s+([A-Z0-9]+)",
            r"set\s+forth\s+(?:on|in)\s+(Exhibit|Schedule|Annex|Appendix)\s+([A-Z0-9]+)",
            r"(?:See|see)\s+(Exhibit|Schedule|Annex|Appendix)\s+([A-Z0-9]+)",
            r"incorporated\s+.*\s+(Exhibit|Schedule|Annex|Appendix)\s+([A-Z0-9]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                exhibit_type = match.group(1).title()
                exhibit_num = match.group(2).upper()
                return (f"{exhibit_type} {exhibit_num}", "")

        return None


class HeadingClassifierV4(AbstractElementwiseProcessingStep):
    """Better heading detection."""

    def __init__(self, types_to_process=None) -> None:
        super().__init__(types_to_process=types_to_process or {TextElement})

    def _process_element(self, element: AbstractSemanticElement, context=None) -> Optional[AbstractSemanticElement]:
        if not element.html_tag:
            return element

        text_content = element.html_tag.text.strip()

        if self._is_heading(text_content, element.html_tag):
            level = self._infer_heading_level(text_content, element.html_tag)
            return HeadingElement(
                element.html_tag,
                heading_text=text_content,
                level=level,
            )

        return element

    def _is_heading(self, text: str, html_tag: HtmlTag) -> bool:
        """Enhanced heading detection."""
        # Length constraints
        word_count = len(text.split())
        if word_count > 12 or word_count < 1:
            return False

        # Don't classify single numbers as headings
        if re.match(r"^\d+\.?$", text.strip()):
            return False

        # Style-based detection
        try:
            style = html_tag._bs4.get("style", "") if hasattr(html_tag, "_bs4") else ""
            style_indicators = ["bold", "underline", "uppercase"]
            has_style = any(indicator in style.lower() for indicator in style_indicators)

            if has_style and word_count <= 8:
                return True
        except:
            pass

        # ALL CAPS detection (but not single words)
        if text.isupper() and len(text) > 3 and word_count > 1:
            return True

        # Heading keywords
        heading_patterns = [
            r"^\d+\.\d+\s+[A-Z]",  # "1.1 Definitions"
            r"^[A-Z][A-Za-z\s]+:$",  # "Definitions:"
            r"^(?:ARTICLE|SECTION)\s+\d+",  # "ARTICLE 1"
        ]

        if any(re.match(pattern, text) for pattern in heading_patterns):
            return True

        # Common heading words (but must be short)
        if word_count <= 5:
            heading_keywords = [
                "definitions", "representations", "warranties", "covenants",
                "conditions", "termination", "indemnification", "miscellaneous",
                "general provisions", "notices", "governing law", "recitals",
            ]

            text_lower = text.lower()
            if any(keyword in text_lower for keyword in heading_keywords):
                return True

        return False

    def _infer_heading_level(self, text: str, html_tag: HtmlTag) -> int:
        """Infer heading level."""
        # ALL CAPS = level 1
        if text.isupper():
            return 1

        # With number prefix = level 2
        if re.match(r"^\d+\.\d+\s+", text):
            return 2

        # Style-based
        try:
            style = html_tag._bs4.get("style", "") if hasattr(html_tag, "_bs4") else ""
            if "bold" in style.lower() and "underline" in style.lower():
                return 1
            if "bold" in style.lower():
                return 2
        except:
            pass

        return 2


class MainTitleClassifierV4(AbstractElementwiseProcessingStep):
    """Improved main title detection."""

    def __init__(self, types_to_process=None) -> None:
        super().__init__(types_to_process=types_to_process or {NotYetClassifiedElement, TextElement})
        self.title_found = False

    def _process_element(self, element: AbstractSemanticElement, context=None) -> Optional[AbstractSemanticElement]:
        if not element.html_tag or self.title_found:
            return element

        text_content = element.html_tag.text.strip()

        # Skip if it's metadata
        if self._is_likely_metadata(text_content):
            return element

        if self._is_main_title(text_content, element.html_tag):
            self.title_found = True
            return AgreementTitleElement(element.html_tag)

        return element

    def _is_likely_metadata(self, text: str) -> bool:
        """Check if text is likely metadata."""
        metadata_patterns = [
            r"^Exhibit\s+\d+",
            r"^EX-\d+",
            r"^Page\s+\d+",
            r"^\d+$",
            r"^-\s*\d+\s*-$",
        ]

        return any(re.match(pattern, text.strip(), re.IGNORECASE) for pattern in metadata_patterns)

    def _is_main_title(self, text: str, html_tag: HtmlTag) -> bool:
        """Enhanced main title detection."""
        # Length check
        if len(text.split()) > 15 or len(text) < 5:
            return False

        # Must contain agreement-related keywords
        title_keywords = [
            "agreement", "contract", "note", "license", "lease",
            "amendment", "guaranty", "warranty", "deed", "indenture",
            "memorandum", "certificate", "letter", "terms",
        ]

        text_lower = text.lower()
        has_keyword = any(keyword in text_lower for keyword in title_keywords)

        if not has_keyword:
            return False

        # Check position and style
        try:
            style = html_tag._bs4.get("style", "") if hasattr(html_tag, "_bs4") else ""
            is_centered = "center" in style.lower()
            is_bold = "bold" in style.lower()

            # Strong indicator
            if is_centered and is_bold:
                return True

            # If centered OR bold with strong pattern
            if is_centered or is_bold:
                # Check for strong title patterns
                strong_patterns = [
                    r"^[A-Z][A-Z\s\-]+(?:AGREEMENT|CONTRACT|NOTE)$",
                    r"^(?:AMENDED\s+AND\s+RESTATED\s+)?[A-Z\s]+AGREEMENT$",
                    r"(?:AGREEMENT|CONTRACT|NOTE)$",
                ]

                if any(re.match(pattern, text.strip(), re.IGNORECASE) for pattern in strong_patterns):
                    return True
        except:
            pass

        # Pattern-based detection
        if text.isupper() and has_keyword:
            return True

        # Title case with agreement words
        return bool(text[0].isupper() and has_keyword and len(text.split()) <= 8)


class ContentClassifierV4(AbstractElementwiseProcessingStep):
    """Classify substantial text as content."""

    def __init__(self, types_to_process=None) -> None:
        super().__init__(types_to_process=types_to_process or {TextElement})

    def _process_element(self, element: AbstractSemanticElement, context=None) -> Optional[AbstractSemanticElement]:
        if not element.html_tag:
            return element

        text_content = element.html_tag.text.strip()

        # More selective content classification
        if self._is_content_text(text_content):
            return ContentTextElement(element.html_tag)

        return element

    def _is_content_text(self, text: str) -> bool:
        """Determine if text is content."""
        # Minimum length
        if len(text) < 50:
            return False

        # Must have some substance (not just numbers/symbols)
        alpha_count = sum(1 for c in text if c.isalpha())
        if alpha_count < 20:
            return False

        # Not all caps (likely heading)
        return not (text.isupper() and len(text.split()) < 20)


class AgreementParserV5(AbstractSemanticElementParser):
    """Legal Agreement Parser V5 - Creates fresh processing steps for each parse."""

    def get_default_steps(
        self,
        get_checks: Optional[Callable[[], list[AbstractSingleElementCheck]]] = None,
    ) -> list[AbstractProcessingStep]:
        """Create fresh processing steps for each parse."""
        # Create new instances every time this is called
        return [
            # Phase 1: Initial cleanup
            EmptyElementClassifier(types_to_process={NotYetClassifiedElement}),

            # Phase 2: Aggressive metadata removal
            ImprovedMetadataRemover(types_to_process={NotYetClassifiedElement, TextElement}),

            # Phase 3: Table processing
            TableClassifier(types_to_process={NotYetClassifiedElement}),
            TableOfContentsClassifier(types_to_process={TableElement}),

            # Phase 4: Main title (early detection)
            MainTitleClassifierV4(types_to_process={NotYetClassifiedElement, TextElement}),

            # Phase 5: Structure detection
            SmartSectionClassifier(types_to_process={NotYetClassifiedElement, TextElement, TableElement}),
            EnhancedClauseClassifier(types_to_process={NotYetClassifiedElement, TextElement}),

            # Phase 6: Legal content
            LegalContentClassifierV4(types_to_process={NotYetClassifiedElement, TextElement}),

            # Phase 7: Text processing
            TextClassifier(types_to_process={NotYetClassifiedElement}),
            HeadingClassifierV4(types_to_process={TextElement}),
            ContentClassifierV4(types_to_process={TextElement}),

            # Phase 8: Final merge
            TextElementMerger(),
        ]

    def get_default_single_element_checks(self) -> list[AbstractSingleElementCheck]:
        """No special checks needed."""
        return []


def analyze_agreement(parser: AgreementParserV5, html_content: str, agreement_num: int) -> dict[str, Any]:
    """Analyze a single agreement and return results."""
    try:
        elements = parser.parse(html_content)

        # Get metadata stats from processing steps
        metadata_stats = {}
        for step in parser.get_default_steps():
            if isinstance(step, ImprovedMetadataRemover):
                metadata_stats = step.get_stats()
                break

        # Filter elements
        relevant_elements = [e for e in elements if not isinstance(e, MetadataElement)]
        metadata_elements = [e for e in elements if isinstance(e, MetadataElement)]

        # Count by type
        type_counts = defaultdict(int)
        for elem in relevant_elements:
            type_counts[type(elem).__name__] += 1

        # Extract key metrics
        has_title = type_counts["AgreementTitleElement"] > 0
        has_articles = type_counts["ArticleElement"] > 0
        has_sections = type_counts["SectionElement"] > 0
        has_clauses = type_counts["ClauseElement"] > 0
        has_structure = has_articles or has_sections or has_clauses

        # Get title text
        title_text = ""
        titles = [e for e in relevant_elements if isinstance(e, AgreementTitleElement)]
        if titles:
            title_text = titles[0].text

        # Calculate status
        status = "❌ FAILED"
        if has_title and has_structure:
            structure_score = 0
            if has_articles: structure_score += 2
            if has_sections: structure_score += 2
            if has_clauses: structure_score += 1
            if type_counts["HeadingElement"] > 0: structure_score += 1
            if type_counts["ContentTextElement"] > 0: structure_score += 1

            if structure_score >= 5:
                status = "✅ EXCELLENT"
            elif structure_score >= 3:
                status = "✅ SUCCESS"
            else:
                status = "⚠️ PARTIAL"

        return {
            "num": agreement_num,
            "status": status,
            "title": has_title,
            "title_text": title_text,
            "structure": has_structure,
            "elements": elements,
            "relevant_elements": relevant_elements,
            "metadata_removed": len(metadata_elements),
            "metadata_stats": metadata_stats,
            "type_counts": dict(type_counts),
            "has_articles": has_articles,
            "has_sections": has_sections,
            "has_clauses": has_clauses,
            "total_elements": len(elements),
            "relevant_count": len(relevant_elements),
        }

    except Exception as e:
        return {
            "num": agreement_num,
            "status": "💥 ERROR",
            "error": str(e),
            "metadata_removed": 0,
        }


def visualize_structure_v5(elements: list[AbstractSemanticElement], title: str = "", max_elements: int = 50) -> None:
    """Enhanced structure visualization."""
    # Find main title
    titles = [e for e in elements if isinstance(e, AgreementTitleElement)]
    if titles:
        pass

    # Build hierarchical view
    current_article = None
    current_section = None
    element_count = 0

    for elem in elements:
        if element_count >= max_elements:
            break

        element_count += 1

        if isinstance(elem, ArticleElement):
            current_article = elem
            current_section = None
            if elem.article_title:
                pass
            else:
                pass

        elif isinstance(elem, SectionElement):
            current_section = elem
            if elem.section_title:
                elem.section_title[:50] + "..." if len(elem.section_title) > 50 else elem.section_title
            else:
                pass

        elif isinstance(elem, ClauseElement):
            base_indent = ""
            if current_section:
                base_indent = "        " if current_article else "    "
            elif current_article:
                base_indent = "    "

            level_indent = "    " * (elem.level - 2)
            base_indent + level_indent

            if elem.clause_text:
                elem.clause_text[:40] + "..." if len(elem.clause_text) > 40 else elem.clause_text
            else:
                pass

        elif isinstance(elem, HeadingElement) and elem.level <= 2:
            "    " * elem.level

        elif isinstance(elem, RecitalElement):
            elem.text[:60] + "..." if len(elem.text) > 60 else elem.text

        elif isinstance(elem, (DefinitionElement, PartyElement)):
            pass


def comprehensive_test_v5() -> None:
    """Test V5 parser on all agreements."""
    from pathlib import Path

    html_dir = Path("html_files")

    if not html_dir.exists():
        return

    html_files = sorted(html_dir.glob("*.html"))


    results = []

    # Process each agreement
    for i, html_file in enumerate(html_files, 1):

        # Create fresh parser for each document
        parser = AgreementParserV5()

        # Read and analyze
        html_content = html_file.read_text()
        result = analyze_agreement(parser, html_content, i)

        # Display results

        if result.get("metadata_stats"):
            ", ".join([f"{k}: {v}" for k, v in result["metadata_stats"].items()])
        else:
            pass

        if result.get("title_text"):
            pass

        # Structure metrics
        if "type_counts" in result:
            counts = result["type_counts"]

            # Additional elements
            if counts.get("DefinitionElement", 0) > 0:
                pass
            if counts.get("PartyElement", 0) > 0:
                pass
            if counts.get("RecitalElement", 0) > 0:
                pass

        # Show structure for successful parses (first 5)
        if result["status"] in ["✅ SUCCESS", "✅ EXCELLENT", "⚠️ PARTIAL"] and i <= 5:
            if "relevant_elements" in result:
                visualize_structure_v5(result["relevant_elements"], f"Agreement {i}", max_elements=30)

        # Handle errors
        if "error" in result:
            pass

        results.append(result)

    # Summary statistics

    sum(1 for r in results if "SUCCESS" in r["status"] or "EXCELLENT" in r["status"])
    sum(1 for r in results if "PARTIAL" in r["status"])
    sum(1 for r in results if "FAILED" in r["status"])
    sum(1 for r in results if "ERROR" in r["status"])


    sum(r.get("metadata_removed", 0) for r in results)

    # Detailed table

    for r in results:
        if r.get("title_text"):
            r["title_text"][:28] + "..." if len(r["title_text"]) > 28 else r["title_text"]


    # Success breakdown
    sum(1 for r in results if "EXCELLENT" in r["status"])
    sum(1 for r in results if r["status"] == "✅ SUCCESS")



if __name__ == "__main__":
    comprehensive_test_v5()
