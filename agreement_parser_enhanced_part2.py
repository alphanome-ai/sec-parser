# Part 2 of agreement_parser_enhanced.py - append this to the file

class StructuralAnalyzer:
    """Analyzes document structure using DOM and visual cues"""
    
    def __init__(self):
        self.style_hierarchy = {}
        self.element_styles = {}
        
    def analyze(self, html_content: str) -> Dict[str, Any]:
        """Analyze document structure"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Build style hierarchy
        self._analyze_styles(soup)
        
        # Analyze document structure
        structure = {
            'elements': self._extract_all_elements(soup),
            'style_hierarchy': self.style_hierarchy,
            'nesting_patterns': self._analyze_nesting(soup),
            'visual_breaks': self._find_visual_breaks(soup),
            'metadata_elements': self._identify_metadata(soup),
        }
        
        return structure
    
    def _analyze_styles(self, soup: BeautifulSoup):
        """Analyze styling patterns to infer hierarchy"""
        text_elements = soup.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span'])
        
        style_groups = {}
        
        for elem in text_elements:
            if elem.get_text(strip=True):
                style_key = self._get_style_key(elem)
                if style_key not in style_groups:
                    style_groups[style_key] = []
                style_groups[style_key].append(elem)
        
        # Rank styles by visual prominence
        for style_key, elements in style_groups.items():
            prominence = self._calculate_prominence(style_key, elements)
            self.style_hierarchy[style_key] = prominence
            
    def _get_style_key(self, element: Tag) -> str:
        """Generate a key representing the element's style"""
        style_parts = []
        
        # Tag name
        style_parts.append(element.name)
        
        # Inline styles
        if element.get('style'):
            style = element.get('style').lower()
            if 'font-size' in style:
                size_match = re.search(r'font-size:\s*(\d+)', style)
                if size_match:
                    style_parts.append(f'size{size_match.group(1)}')
            if 'font-weight' in style and 'bold' in style:
                style_parts.append('bold')
            if 'text-align' in style:
                align_match = re.search(r'text-align:\s*(\w+)', style)
                if align_match:
                    style_parts.append(f'align{align_match.group(1)}')
                    
        # HTML attributes
        if element.get('align'):
            style_parts.append(f"align{element.get('align')}")
            
        # Check for bold/strong tags
        if element.find(['b', 'strong']) or element.parent.name in ['b', 'strong']:
            style_parts.append('bold')
            
        # Check for underline
        if element.find(['u']) or element.parent.name in ['u']:
            style_parts.append('underline')
            
        return '_'.join(style_parts)
    
    def _calculate_prominence(self, style_key: str, elements: List[Tag]) -> float:
        """Calculate visual prominence score"""
        score = 0.0
        
        # Tag type scores
        if 'h1' in style_key: score += 10
        elif 'h2' in style_key: score += 8
        elif 'h3' in style_key: score += 6
        elif 'h4' in style_key: score += 4
        elif 'h5' in style_key or 'h6' in style_key: score += 2
        
        # Style scores
        if 'bold' in style_key: score += 2
        if 'aligncenter' in style_key: score += 3
        if 'underline' in style_key: score += 1
        
        # Font size
        size_match = re.search(r'size(\d+)', style_key)
        if size_match:
            size = int(size_match.group(1))
            score += (size - 10) / 2
            
        # Frequency penalty (common styles are less likely to be headers)
        if len(elements) > 20:
            score -= 2
            
        return score
    
    def _extract_all_elements(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract all potential document elements"""
        elements = []
        
        # Get all text-containing elements
        for elem in soup.find_all(text=True):
            if elem.parent.name in ['script', 'style', 'meta', 'link']:
                continue
                
            text = elem.strip()
            if not text or len(text) < 3:
                continue
                
            parent = elem.parent
            element_info = {
                'text': text,
                'tag': parent.name,
                'style_key': self._get_style_key(parent),
                'attributes': dict(parent.attrs) if parent.attrs else {},
                'path': self._get_element_path(parent),
                'parent': parent,
                'position': len(elements),
            }
            elements.append(element_info)
            
        return elements
    
    def _get_element_path(self, element: Tag) -> str:
        """Get the path from root to element"""
        path = []
        current = element
        while current and current.name:
            path.append(current.name)
            current = current.parent
        return '/'.join(reversed(path))
    
    def _analyze_nesting(self, soup: BeautifulSoup) -> Dict:
        """Analyze nesting patterns in document"""
        nesting_patterns = {
            'max_depth': 0,
            'common_patterns': [],
            'div_structure': self._analyze_div_structure(soup),
            'table_structure': self._analyze_table_structure(soup),
        }
        
        # Find maximum nesting depth
        all_elements = soup.find_all()
        for elem in all_elements:
            depth = len(list(elem.parents))
            if depth > nesting_patterns['max_depth']:
                nesting_patterns['max_depth'] = depth
                
        return nesting_patterns
    
    def _analyze_div_structure(self, soup: BeautifulSoup) -> Dict:
        """Analyze DIV-based structure"""
        divs = soup.find_all('div')
        structure = {
            'total_divs': len(divs),
            'nested_divs': 0,
            'div_patterns': [],
        }
        
        for div in divs:
            if div.find_parent('div'):
                structure['nested_divs'] += 1
                
        return structure
    
    def _analyze_table_structure(self, soup: BeautifulSoup) -> Dict:
        """Analyze table-based structure"""
        tables = soup.find_all('table')
        structure = {
            'total_tables': len(tables),
            'nested_tables': 0,
            'table_patterns': [],
        }
        
        for table in tables:
            if table.find_parent('table'):
                structure['nested_tables'] += 1
                
        return structure
    
    def _find_visual_breaks(self, soup: BeautifulSoup) -> List[Tag]:
        """Find visual break elements"""
        breaks = []
        
        # HR tags
        breaks.extend(soup.find_all('hr'))
        
        # Page break patterns
        for elem in soup.find_all(text=re.compile(r'page\s+\d+', re.I)):
            breaks.append(elem.parent)
            
        # Large whitespace
        for elem in soup.find_all(['p', 'div']):
            if elem.get_text(strip=True) == '' and elem.find('br'):
                breaks.append(elem)
                
        return breaks
    
    def _identify_metadata(self, soup: BeautifulSoup) -> List[Tag]:
        """Identify metadata elements"""
        metadata = []
        
        # Common metadata patterns
        metadata_patterns = [
            r'exhibit\s+\d+',
            r'page\s+\d+',
            r'execution\s+copy',
            r'confidential',
            r'\*+\s*\*+\s*\*+',
            r'filed\s+with',
            r'securities\s+and\s+exchange',
        ]
        
        for pattern in metadata_patterns:
            for elem in soup.find_all(text=re.compile(pattern, re.I)):
                metadata.append(elem.parent)
                
        return metadata


class TitleDetector:
    """Intelligent title detection using multiple strategies"""
    
    def __init__(self):
        self.strategies = [
            self._detect_by_position_and_style,
            self._detect_by_content_analysis,
            self._detect_by_document_flow,
            self._detect_by_html_structure,
            self._detect_by_keyword_patterns,
        ]
        
    def detect_title(self, elements: List[Dict], structure: Dict) -> Optional[Dict]:
        """Detect document title using multiple strategies"""
        candidates = []
        
        for strategy in self.strategies:
            try:
                result = strategy(elements, structure)
                if result:
                    candidates.extend(result if isinstance(result, list) else [result])
            except Exception as e:
                logger.warning(f"Title detection strategy failed: {e}")
                
        if not candidates:
            return None
            
        # Score and rank candidates
        scored_candidates = []
        for candidate in candidates:
            score = self._score_title_candidate(candidate, elements, structure)
            scored_candidates.append((score, candidate))
            
        # Return highest scoring candidate
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        return scored_candidates[0][1] if scored_candidates else None
    
    def _detect_by_position_and_style(self, elements: List[Dict], structure: Dict) -> List[Dict]:
        """Detect title by position and visual style"""
        candidates = []
        
        # Skip metadata elements at start
        start_idx = 0
        for i, elem in enumerate(elements[:20]):
            if self._is_metadata(elem['text']):
                start_idx = i + 1
            else:
                break
                
        # Look for prominent elements after metadata
        for i in range(start_idx, min(start_idx + 10, len(elements))):
            elem = elements[i]
            
            # Check for centered, bold, or large text
            if ('aligncenter' in elem['style_key'] or 
                'bold' in elem['style_key'] or
                elem['tag'] in ['h1', 'h2', 'h3']):
                
                # Check if it contains agreement keywords
                if self._contains_agreement_keywords(elem['text']):
                    candidates.append(elem)
                    
        return candidates
    
    def _detect_by_content_analysis(self, elements: List[Dict], structure: Dict) -> List[Dict]:
        """Detect title by analyzing content"""
        candidates = []
        
        agreement_patterns = [
            r'(.*?)\s+agreement',
            r'agreement\s+(?:for|of|to)\s+(.*)',
            r'(.*?)\s+contract',
            r'(.*?)\s+plan',
            r'(.*?)\s+indenture',
            r'(.*?)\s+lease',
            r'form\s+of\s+(.*)',
        ]
        
        for elem in elements[:30]:  # Check first 30 elements
            text = elem['text'].strip()
            
            for pattern in agreement_patterns:
                if re.search(pattern, text, re.I):
                    # Check if it's not part of a larger paragraph
                    if len(text) < 200 and '\n\n' not in text:
                        candidates.append(elem)
                        break
                        
        return candidates
    
    def _detect_by_document_flow(self, elements: List[Dict], structure: Dict) -> List[Dict]:
        """Detect title by document flow analysis"""
        candidates = []
        
        # Look for first major text after metadata/headers
        found_content_start = False
        
        for i, elem in enumerate(elements):
            # Skip metadata
            if self._is_metadata(elem['text']):
                continue
                
            # Look for content start markers
            if not found_content_start:
                text_lower = elem['text'].lower()
                if any(marker in text_lower for marker in ['parties:', 'recitals:', 'whereas:', 'between:']):
                    found_content_start = True
                    # Title is likely before this
                    if i > 0:
                        for j in range(max(0, i-5), i):
                            if self._contains_agreement_keywords(elements[j]['text']):
                                candidates.append(elements[j])
                                
        return candidates
    
    def _detect_by_html_structure(self, elements: List[Dict], structure: Dict) -> List[Dict]:
        """Detect title using HTML structure"""
        candidates = []
        
        # Group elements by style
        style_groups = {}
        for elem in elements[:50]:
            style_key = elem['style_key']
            if style_key not in style_groups:
                style_groups[style_key] = []
            style_groups[style_key].append(elem)
            
        # Find unique prominent styles
        for style_key, group in style_groups.items():
            if len(group) <= 3:  # Unique styles
                prominence = structure['style_hierarchy'].get(style_key, 0)
                if prominence > 5:  # High prominence
                    for elem in group:
                        if self._contains_agreement_keywords(elem['text']):
                            candidates.append(elem)
                            
        return candidates
    
    def _detect_by_keyword_patterns(self, elements: List[Dict], structure: Dict) -> List[Dict]:
        """Detect title by specific keyword patterns"""
        candidates = []
        
        # Look for exhibit patterns
        exhibit_pattern = r'exhibit\s+[a-z0-9\.\-]+.*?(?:agreement|contract|plan|lease)'
        
        for elem in elements[:30]:
            if re.search(exhibit_pattern, elem['text'], re.I):
                candidates.append(elem)
                
        return candidates
    
    def _score_title_candidate(self, candidate: Dict, elements: List[Dict], structure: Dict) -> float:
        """Score a title candidate"""
        score = 0.0
        
        # Position score (earlier is better, but not too early)
        position = candidate['position']
        if position < 5:
            score += 2
        elif position < 10:
            score += 5
        elif position < 20:
            score += 3
        else:
            score += 1
            
        # Style score
        style_prominence = structure['style_hierarchy'].get(candidate['style_key'], 0)
        score += style_prominence
        
        # Content score
        text = candidate['text'].lower()
        if 'agreement' in text: score += 5
        if 'contract' in text: score += 4
        if 'lease' in text: score += 4
        if 'plan' in text: score += 3
        if 'form of' in text: score += 2
        if 'exhibit' in text: score += 2
        
        # Length score (titles are usually short)
        text_len = len(candidate['text'])
        if text_len < 50: score += 3
        elif text_len < 100: score += 2
        elif text_len > 200: score -= 2
        
        # Centered text bonus
        if 'aligncenter' in candidate['style_key']:
            score += 3
            
        # Bold text bonus
        if 'bold' in candidate['style_key']:
            score += 2
            
        # Isolated element bonus (not part of larger text block)
        if position > 0 and position < len(elements) - 1:
            prev_text = elements[position - 1]['text'] if position > 0 else ''
            next_text = elements[position + 1]['text'] if position < len(elements) - 1 else ''
            
            if len(prev_text) < 50 and len(next_text) < 50:
                score += 2
                
        return score
    
    def _is_metadata(self, text: str) -> bool:
        """Check if text is metadata"""
        metadata_patterns = [
            r'page\s+\d+',
            r'exhibit\s+\d+\.\d+',
            r'execution\s+copy',
            r'filed\s+with',
            r'securities.*commission',
            r'\*+\s*\*+\s*\*+',
            r'confidential',
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in metadata_patterns)
    
    def _contains_agreement_keywords(self, text: str) -> bool:
        """Check if text contains agreement keywords"""
        keywords = [
            'agreement', 'contract', 'lease', 'plan', 'indenture',
            'amendment', 'addendum', 'memorandum', 'deed', 'license'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in keywords)


# Continue with more components...