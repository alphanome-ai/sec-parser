#!/usr/bin/env python3
"""Legal Agreement Parser V11 - Final fix for Agreement 6
Based on V6 with enhanced p tag detection
- Better handling of p tags with align="center"
- Checks parent tags for bold children.
"""

import re
from collections import defaultdict
from typing import Callable, Optional

# Import all element classes from V5
from agreement_parser_v5 import (
    AgreementTitleElement,
    ArticleElement,
    ClauseElement,
    ContentClassifierV4,
    EnhancedClauseClassifier,
    HeadingClassifierV4,
    ImprovedMetadataRemover,
    LegalContentClassifierV4,
    MetadataElement,
    SectionElement,
    SignatureBlockElement,
)
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
    NotYetClassifiedElement,
    TextElement,
)
from sec_parser.semantic_elements.table_element.table_element import TableElement


class ImprovedMainTitleClassifier(AbstractElementwiseProcessingStep):
    """V6: Better title detection with HTML attributes and position awareness."""

    def __init__(self, types_to_process=None) -> None:
        super().__init__(types_to_process=types_to_process or {NotYetClassifiedElement, TextElement})
        self.title_found = False
        self.elements_seen = 0

    def _process_element(self, element: AbstractSemanticElement, context=None) -> Optional[AbstractSemanticElement]:
        if not element.html_tag or self.title_found:
            return element

        self.elements_seen += 1
        text_content = element.html_tag.text.strip()

        # Skip if it's metadata
        if self._is_likely_metadata(text_content):
            return element

        # Check if this could be a title
        if self._is_main_title_v6(text_content, element.html_tag, self.elements_seen):
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
            r"Confidential Treatment",
            r"Text Omitted",
            r"Securities and Exchange Commission",
        ]

        return any(re.search(pattern, text.strip(), re.IGNORECASE) for pattern in metadata_patterns)

    def _is_main_title_v6(self, text: str, html_tag: HtmlTag, position: int) -> bool:
        """V6: Enhanced title detection with HTML attributes."""
        # Length check
        if len(text.split()) > 15 or len(text) < 5:
            return False

        # Must contain agreement-related keywords
        title_keywords = [
            "agreement", "contract", "note", "license", "lease",
            "amendment", "guaranty", "warranty", "deed", "indenture",
            "memorandum", "certificate", "letter", "terms", "plan",
        ]

        text_lower = text.lower()
        has_keyword = any(keyword in text_lower for keyword in title_keywords)

        if not has_keyword:
            return False

        # V11: Enhanced HTML attributes check (for Agreement 6)
        try:
            if hasattr(html_tag, "_bs4"):
                bs4_tag = html_tag._bs4

                # Get tag name and attributes safely
                tag_name = getattr(bs4_tag, "name", None)
                attrs = getattr(bs4_tag, "attrs", {})

                # Check if this is a p tag with align="center"
                if tag_name == "p" and attrs.get("align") == "center":
                    # Check if it contains bold text
                    has_bold = any(child.name in ["b", "strong"] for child in bs4_tag.descendants if hasattr(child, "name"))
                    if has_bold:
                        return True

                # Check style attribute
                style = attrs.get("style", "")
                is_centered_style = "text-align:center" in style or "text-align: center" in style
                is_bold_style = "bold" in style.lower()

                # Check if bold via child tags
                is_bold_tag = bool(bs4_tag.find("b") or bs4_tag.find("strong"))

                # Any centering method + bold = strong title indicator
                is_centered = attrs.get("align") == "center" or is_centered_style
                is_bold = is_bold_tag or is_bold_style

                if is_centered and is_bold:
                    return True

                # If it's early in document (within first 20 elements) and has strong pattern
                if position <= 20 and (is_centered or is_bold):
                    # Check for strong title patterns
                    strong_patterns = [
                        r"^[A-Z][A-Z\s\-]+(?:AGREEMENT|CONTRACT|LEASE)$",
                        r"^(?:AMENDED\s+AND\s+RESTATED\s+)?[A-Z\s]+AGREEMENT$",
                        r"^LEASE\s+AGREEMENT$",  # Added for Agreement 6
                        r"(?:AGREEMENT|CONTRACT|LEASE)$",
                    ]

                    if any(re.match(pattern, text.strip(), re.IGNORECASE) for pattern in strong_patterns):
                        return True
        except:
            pass

        # Pattern-based detection for other cases
        if text.isupper() and has_keyword:
            return True

        # Title case with agreement words (early in document)
        return bool(position <= 20 and text[0].isupper() and has_keyword and len(text.split()) <= 8)


class EnhancedSectionClassifier(AbstractElementwiseProcessingStep):
    """V6: Better section detection including underlined headers."""

    def __init__(self, types_to_process=None) -> None:
        super().__init__(types_to_process=types_to_process or {NotYetClassifiedElement, TextElement, TableElement})
        self.seen_sections = set()
        self.section_count = 0
        self.article_count = 0

    def _process_element(self, element: AbstractSemanticElement, context=None) -> Optional[AbstractSemanticElement]:
        if not element.html_tag:
            return element

        # Handle tables
        if element.html_tag.name.lower() == "table":
            result = self._process_table_element(element)
            if result and isinstance(result, (ArticleElement, SectionElement)):
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
            key = self._get_section_key(result)
            if key not in self.seen_sections:
                self.seen_sections.add(key)
                return result
            return element

        return result if result else element

    def _get_section_key(self, element) -> str:
        """Generate unique key for section/article."""
        if isinstance(element, ArticleElement):
            return f"article:{element.article_number}"
        if isinstance(element, SectionElement):
            return f"section:{element.section_number}"
        return ""

    def _extract_structured_element(self, text: str, html_tag: HtmlTag):
        """V6: Enhanced extraction with underline detection."""
        # Check for underlined text (for Agreement 2's "Schedule A")
        if self._is_underlined_header(text, html_tag):
            # This could be a section header
            if len(text.split()) <= 10:  # Headers are usually short
                self.section_count += 1
                return SectionElement(
                    html_tag,
                    section_number=text.strip(),
                    section_title="",
                    level=1,
                )

        # Check for Article patterns
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

        # Check for Section patterns
        section_patterns = [
            (r"^(Section)\s+(\d+(?:\.\d+)*)(?:\s*[-–—.]\s*(.*))?", "Section"),
            (r"^(\d+(?:\.\d+)*)\s*\.(?:\s+(.*))?", "number"),
            (r"^([A-Z])\.\s*(.*)$", "letter"),
            (r"^(Schedule)\s+([A-Z0-9]+)(?:\s*[-–—.]\s*(.*))?", "Schedule"),  # V6: Schedule pattern
        ]

        for pattern, pattern_type in section_patterns:
            match = re.match(pattern, text.strip())
            if match:
                self.section_count += 1

                if pattern_type in ["Section", "Schedule"]:
                    section_num = f"{match.group(1)} {match.group(2)}"
                    section_title = match.group(3).strip() if match.group(3) else ""
                elif pattern_type == "number":
                    section_num = match.group(1)
                    section_title = match.group(2).strip() if match.group(2) else ""
                else:  # letter
                    section_num = f"{match.group(1)}."
                    section_title = match.group(2).strip() if match.group(2) else ""

                level = 1 if pattern_type in ["Schedule", "letter"] else len(section_num.split("."))

                return SectionElement(
                    html_tag,
                    section_number=section_num,
                    section_title=section_title,
                    level=level,
                )

        return None

    def _is_underlined_header(self, text: str, html_tag: HtmlTag) -> bool:
        """V6: Check if text is underlined (header indicator)."""
        try:
            if hasattr(html_tag, "_bs4"):
                # Check for <u> tag
                if html_tag._bs4.find("u"):
                    return True

                # Check for text-decoration style
                style = html_tag._bs4.get("style", "")
                if "underline" in style.lower():
                    return True

                # Check child elements for underline
                for child in html_tag._bs4.find_all(["b", "font", "span"]):
                    child_style = child.get("style", "")
                    if "underline" in child_style.lower():
                        return True
                    if child.find("u"):
                        return True
        except:
            pass

        return False

    def _process_table_element(self, element: AbstractSemanticElement):
        """Process table for sections."""
        try:
            if not hasattr(element.html_tag, "_bs4"):
                return element

            tds = element.html_tag._bs4.find_all("td")

            if len(tds) >= 2:
                first_cell = tds[0].get_text().strip()
                second_cell = tds[1].get_text().strip()

                # Try section patterns on first cell
                if re.match(r"^\d+\.?$", first_cell):
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
        """Check if table represents a signature block."""
        combined_lower = (cell1 + " " + cell2).lower()
        signature_words = [
            "by:", "/s/", "signature", "name:", "title:", "date:",
            "authorized", "executed", "witness", "acknowledged",
        ]

        word_count = sum(1 for word in signature_words if word in combined_lower)
        return word_count >= 2


class AgreementParserV11(AbstractSemanticElementParser):
    """Legal Agreement Parser V6 - Targeted improvements
    - HTML attribute-aware title detection
    - Underlined header detection
    - Better early title recognition.
    """

    def get_default_steps(
        self,
        get_checks: Optional[Callable[[], list[AbstractSingleElementCheck]]] = None,
    ) -> list[AbstractProcessingStep]:
        """V6 processing pipeline with incremental improvements."""
        return [
            # Phase 1: Initial cleanup
            EmptyElementClassifier(types_to_process={NotYetClassifiedElement}),

            # Phase 2: Metadata removal
            ImprovedMetadataRemover(types_to_process={NotYetClassifiedElement, TextElement}),

            # Phase 3: Table processing
            TableClassifier(types_to_process={NotYetClassifiedElement}),
            TableOfContentsClassifier(types_to_process={TableElement}),

            # Phase 4: V6 Main title detection
            ImprovedMainTitleClassifier(types_to_process={NotYetClassifiedElement, TextElement}),

            # Phase 5: V6 Structure detection
            EnhancedSectionClassifier(types_to_process={NotYetClassifiedElement, TextElement, TableElement}),
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


def test_v6_improvements() -> None:
    """Test V6 improvements on specific problematic agreements."""
    from pathlib import Path


    # Test on the three problematic agreements
    test_agreements = [
        (2, "Should detect 'Schedule A' as section"),
        (3, "Incentive plan - may not have standard structure"),
        (6, "Should detect 'LEASE AGREEMENT' title with align attribute"),
    ]

    for agreement_num, _expected in test_agreements:

        html_file = Path(f"html_files/agreement_{agreement_num:02d}.html")
        if not html_file.exists():
            continue

        # Parse with V11
        parser = AgreementParserV11()
        html_content = html_file.read_text()
        elements = parser.parse(html_content)

        # Filter relevant elements
        relevant_elements = [e for e in elements if not isinstance(e, MetadataElement)]

        # Analysis
        type_counts = defaultdict(int)
        for elem in relevant_elements:
            type_counts[type(elem).__name__] += 1

        # Check improvements

        # Title detection
        titles = [e for e in relevant_elements if isinstance(e, AgreementTitleElement)]
        if titles:
            pass
        else:
            pass

        # Section detection
        sections = [e for e in relevant_elements if isinstance(e, SectionElement)]
        if sections:
            for _section in sections[:3]:
                pass
        else:
            pass

        # Other elements
        for _elem_type, count in sorted(type_counts.items()):
            if count > 0:
                pass

    # Test all agreements for overall success rate

    success_count = 0

    for i in range(1, 16):
        html_file = Path(f"html_files/agreement_{i:02d}.html")
        if html_file.exists():
            parser = AgreementParserV11()
            elements = parser.parse(html_file.read_text())
            relevant = [e for e in elements if not isinstance(e, MetadataElement)]

            # Count types
            has_title = any(isinstance(e, AgreementTitleElement) for e in relevant)
            has_structure = any(isinstance(e, (ArticleElement, SectionElement, ClauseElement)) for e in relevant)

            if has_title and has_structure:
                success_count += 1
            else:
                pass




if __name__ == "__main__":
    test_v6_improvements()
