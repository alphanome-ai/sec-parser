# Part 3 of agreement_parser_enhanced.py - Element Classification and Validation

class ElementClassifier:
    """Classifies document elements into semantic types"""
    
    def __init__(self):
        self.patterns = self._build_classification_patterns()
        
    def classify_all(self, structure: Dict) -> List[ParsedElement]:
        """Classify all elements in the document"""
        elements = structure['elements']
        classified_elements = []
        
        for elem_data in elements:
            element_type = self._classify_element(elem_data, structure)
            
            parsed_element = ParsedElement(
                type=element_type,
                content=elem_data['text'],
                level=self._determine_level(elem_data, element_type, structure),
                tag_name=elem_data['tag'],
                attributes=elem_data['attributes'],
                line_number=elem_data['position'],
                confidence=self._calculate_confidence(elem_data, element_type),
                metadata={'style_key': elem_data['style_key'], 'path': elem_data['path']}
            )
            
            classified_elements.append(parsed_element)
            
        return classified_elements
    
    def _classify_element(self, elem_data: Dict, structure: Dict) -> ElementType:
        """Classify a single element"""
        text = elem_data['text'].strip()
        text_lower = text.lower()
        style_key = elem_data['style_key']
        
        # Check for title
        if self._is_title(elem_data, structure):
            return ElementType.TITLE
            
        # Check for metadata
        if self._is_metadata(text):
            return ElementType.METADATA
            
        # Check for sections/articles
        section_type = self._classify_section(text, style_key)
        if section_type:
            return section_type
            
        # Check for definitions
        if self._is_definition(text):
            return ElementType.DEFINITION
            
        # Check for parties
        if self._is_party(text):
            return ElementType.PARTY
            
        # Check for signatures
        if self._is_signature(text):
            return ElementType.SIGNATURE
            
        # Check for tables
        if elem_data['tag'] in ['table', 'tr', 'td', 'th']:
            return ElementType.TABLE
            
        # Default to paragraph
        return ElementType.PARAGRAPH
    
    def _is_title(self, elem_data: Dict, structure: Dict) -> bool:
        """Check if element is a title"""
        text = elem_data['text']
        style_key = elem_data['style_key']
        
        # Check style prominence
        prominence = structure['style_hierarchy'].get(style_key, 0)
        if prominence < 5:
            return False
            
        # Check for agreement keywords
        title_keywords = ['agreement', 'contract', 'lease', 'plan', 'indenture', 'amendment']
        text_lower = text.lower()
        
        has_keywords = any(keyword in text_lower for keyword in title_keywords)
        is_prominent = prominence > 8
        is_early = elem_data['position'] < 20
        is_short = len(text) < 200
        
        return has_keywords and is_prominent and is_early and is_short
    
    def _classify_section(self, text: str, style_key: str) -> Optional[ElementType]:
        """Classify section-type elements"""
        text_stripped = text.strip()
        
        # Article patterns
        article_patterns = [
            r'^article\s+[ivxlc]+\b',
            r'^article\s+\d+\b',
            r'^\d+\.\s*[A-Z][^.]*$',  # Numbered sections
        ]
        
        for pattern in article_patterns:
            if re.match(pattern, text_stripped, re.I):
                return ElementType.ARTICLE
                
        # Section patterns
        section_patterns = [
            r'^section\s+\d+',
            r'^\d+\.\d+\s',
            r'^schedule\s+[a-z0-9]+',
            r'^exhibit\s+[a-z0-9]+',
        ]
        
        for pattern in section_patterns:
            if re.match(pattern, text_stripped, re.I):
                return ElementType.SECTION
                
        # Subsection patterns
        subsection_patterns = [
            r'^\([a-z]\)',
            r'^\([0-9]+\)',
            r'^\d+\.\d+\.\d+',
        ]
        
        for pattern in subsection_patterns:
            if re.match(pattern, text_stripped, re.I):
                return ElementType.SUBSECTION
                
        return None
    
    def _is_definition(self, text: str) -> bool:
        """Check if element is a definition"""
        definition_patterns = [
            r'"[^"]+"\s+means\s+',
            r'shall\s+mean\s+',
            r'defined\s+as\s+',
            r'definition[s]?\s*:',
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in definition_patterns)
    
    def _is_party(self, text: str) -> bool:
        """Check if element describes parties"""
        party_patterns = [
            r'parties\s*:',
            r'between\s+.*\sand\s+',
            r'party\s+of\s+the\s+first\s+part',
            r'party\s+of\s+the\s+second\s+part',
            r'borrower\s*:',
            r'lender\s*:',
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in party_patterns)
    
    def _is_signature(self, text: str) -> bool:
        """Check if element is signature-related"""
        signature_patterns = [
            r'signature\s+page',
            r'in\s+witness\s+whereof',
            r'executed\s+.*on\s+the\s+date',
            r'by:\s*/s/',
            r'name\s*:\s*$',
            r'title\s*:\s*$',
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in signature_patterns)
    
    def _is_metadata(self, text: str) -> bool:
        """Check if element is metadata"""
        metadata_patterns = [
            r'page\s+\d+',
            r'exhibit\s+\d+\.\d+',
            r'execution\s+copy',
            r'confidential',
            r'filed\s+with',
            r'securities.*commission',
            r'\*+\s*\*+\s*\*+',
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in metadata_patterns)
    
    def _determine_level(self, elem_data: Dict, element_type: ElementType, structure: Dict) -> int:
        """Determine hierarchical level of element"""
        if element_type == ElementType.TITLE:
            return 0
        elif element_type == ElementType.ARTICLE:
            return 1
        elif element_type == ElementType.SECTION:
            return 2
        elif element_type == ElementType.SUBSECTION:
            return 3
        elif element_type == ElementType.CLAUSE:
            return 4
        else:
            return 5
    
    def _calculate_confidence(self, elem_data: Dict, element_type: ElementType) -> float:
        """Calculate confidence in classification"""
        # Base confidence
        confidence = 0.7
        
        # Adjust based on style prominence
        style_key = elem_data['style_key']
        if 'bold' in style_key:
            confidence += 0.1
        if 'aligncenter' in style_key:
            confidence += 0.1
        if 'h1' in style_key or 'h2' in style_key:
            confidence += 0.2
            
        return min(1.0, confidence)
    
    def _build_classification_patterns(self) -> Dict:
        """Build pattern dictionary for classification"""
        return {
            'title': [
                r'(.*?)\s+agreement',
                r'form\s+of\s+(.*)',
                r'(.*?)\s+contract',
                r'(.*?)\s+lease',
            ],
            'article': [
                r'article\s+[ivxlc]+',
                r'article\s+\d+',
            ],
            'section': [
                r'section\s+\d+',
                r'schedule\s+[a-z0-9]+',
                r'exhibit\s+[a-z0-9]+',
            ],
            'clause': [
                r'^\([a-z]\)',
                r'^\([0-9]+\)',
            ]
        }


class ParseValidator:
    """Validates parse results and attempts recovery"""
    
    def validate_and_fix(self, elements: List[ParsedElement]) -> List[ParsedElement]:
        """Validate parse results and fix issues"""
        # Run validation checks
        validation_result = self._validate_parse(elements)
        
        if validation_result['is_valid']:
            return elements
            
        # Attempt recovery
        logger.warning(f"Parse validation failed: {validation_result['issues']}")
        return self._attempt_recovery(elements, validation_result['issues'])
    
    def _validate_parse(self, elements: List[ParsedElement]) -> Dict:
        """Validate parsed elements"""
        issues = []
        
        # Check for title
        has_title = any(elem.type == ElementType.TITLE for elem in elements)
        if not has_title:
            issues.append("No title found")
            
        # Check for structure
        has_structure = any(elem.type in [ElementType.ARTICLE, ElementType.SECTION] for elem in elements)
        if not has_structure:
            issues.append("No document structure found")
            
        # Check for reasonable distribution
        content_elements = [elem for elem in elements if elem.type == ElementType.PARAGRAPH]
        if len(content_elements) < 3:
            issues.append("Too few content elements")
            
        # Check for massive text blocks
        for elem in elements:
            if len(elem.content) > 5000:
                issues.append("Found overly large text blocks")
                break
                
        # Check metadata pollution
        metadata_count = sum(1 for elem in elements if elem.type == ElementType.METADATA)
        if metadata_count > len(elements) * 0.3:
            issues.append("Too much metadata pollution")
            
        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'title_found': has_title,
            'structure_found': has_structure,
            'element_count': len(elements),
        }
    
    def _attempt_recovery(self, elements: List[ParsedElement], issues: List[str]) -> List[ParsedElement]:
        """Attempt to recover from parsing issues"""
        recovered_elements = elements.copy()
        
        # If no title found, try to infer one
        if "No title found" in issues:
            recovered_elements = self._recover_title(recovered_elements)
            
        # If no structure found, try to infer structure
        if "No document structure found" in issues:
            recovered_elements = self._recover_structure(recovered_elements)
            
        # Clean up metadata pollution
        if "Too much metadata pollution" in issues:
            recovered_elements = self._clean_metadata(recovered_elements)
            
        # Break up large text blocks
        if "Found overly large text blocks" in issues:
            recovered_elements = self._break_large_blocks(recovered_elements)
            
        return recovered_elements
    
    def _recover_title(self, elements: List[ParsedElement]) -> List[ParsedElement]:
        """Try to recover missing title"""
        # Look for first prominent element with agreement keywords
        for i, elem in enumerate(elements[:20]):
            if (elem.confidence > 0.8 and 
                any(keyword in elem.content.lower() for keyword in ['agreement', 'contract', 'lease'])):
                
                # Convert to title
                elem.type = ElementType.TITLE
                elem.level = 0
                logger.info(f"Recovered title: {elem.content[:50]}...")
                break
                
        return elements
    
    def _recover_structure(self, elements: List[ParsedElement]) -> List[ParsedElement]:
        """Try to recover document structure"""
        # Look for numbered patterns that could be sections
        for elem in elements:
            content = elem.content.strip()
            
            # Check for section-like patterns
            if re.match(r'^\d+\.', content):
                elem.type = ElementType.SECTION
                elem.level = 2
            elif re.match(r'^\([a-z]\)', content):
                elem.type = ElementType.SUBSECTION
                elem.level = 3
                
        return elements
    
    def _clean_metadata(self, elements: List[ParsedElement]) -> List[ParsedElement]:
        """Clean metadata pollution"""
        cleaned = []
        
        for elem in elements:
            # Skip obvious metadata
            if elem.type == ElementType.METADATA and len(elem.content) < 50:
                continue
            cleaned.append(elem)
            
        return cleaned
    
    def _break_large_blocks(self, elements: List[ParsedElement]) -> List[ParsedElement]:
        """Break up large text blocks"""
        broken_elements = []
        
        for elem in elements:
            if len(elem.content) > 5000:
                # Split on paragraph boundaries
                paragraphs = elem.content.split('\n\n')
                for i, para in enumerate(paragraphs):
                    if para.strip():
                        new_elem = ParsedElement(
                            type=ElementType.PARAGRAPH,
                            content=para.strip(),
                            level=elem.level,
                            tag_name=elem.tag_name,
                            attributes=elem.attributes,
                            line_number=elem.line_number + i,
                            confidence=elem.confidence * 0.8,
                            metadata=elem.metadata
                        )
                        broken_elements.append(new_elem)
            else:
                broken_elements.append(elem)
                
        return broken_elements


class SpecialCaseHandler:
    """Handles special document formats and edge cases"""
    
    def handle_data_format(self, content: str) -> List[ParsedElement]:
        """Handle data format documents (like Agreement 6)"""
        elements = []
        lines = content.split('\n')
        
        current_section = None
        current_content = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Check for section headers (all caps, substantial length)
            if (re.match(r'^[A-Z][A-Z\s]+$', line) and 
                len(line) > 10 and 
                not re.search(r'\d', line)):
                
                # Save previous section
                if current_section and current_content:
                    elem = ParsedElement(
                        type=ElementType.SECTION,
                        content='\n'.join(current_content),
                        level=2,
                        line_number=i,
                        metadata={'section_title': current_section}
                    )
                    elements.append(elem)
                    
                # Start new section
                current_section = line
                current_content = []
                
                # Add section header
                header_elem = ParsedElement(
                    type=ElementType.SECTION,
                    content=line,
                    level=1,
                    line_number=i
                )
                elements.append(header_elem)
                
            else:
                current_content.append(line)
                
        # Add final section
        if current_section and current_content:
            elem = ParsedElement(
                type=ElementType.PARAGRAPH,
                content='\n'.join(current_content),
                level=3,
                line_number=len(lines)
            )
            elements.append(elem)
            
        return elements
    
    def handle_table_based(self, soup: BeautifulSoup) -> List[ParsedElement]:
        """Handle table-based agreement structure"""
        elements = []
        tables = soup.find_all('table')
        
        for table in tables:
            # Check if table contains document structure
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    # First cell might be section number/title
                    first_cell = cells[0].get_text(strip=True)
                    content_cell = cells[1].get_text(strip=True)
                    
                    if first_cell and content_cell:
                        # Determine element type
                        if re.match(r'^\d+\.', first_cell):
                            elem_type = ElementType.SECTION
                            level = 2
                        elif re.match(r'^\([a-z]\)', first_cell):
                            elem_type = ElementType.SUBSECTION
                            level = 3
                        else:
                            elem_type = ElementType.PARAGRAPH
                            level = 4
                            
                        elem = ParsedElement(
                            type=elem_type,
                            content=f"{first_cell} {content_cell}",
                            level=level,
                            tag_name='td'
                        )
                        elements.append(elem)
                        
        return elements