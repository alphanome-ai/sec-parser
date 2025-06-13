Based on the analysis of the parsing results and code, I'll provide comprehensive prompts for creating a robust EDGAR agreement parser that addresses all the identified issues:

## Task 1: Create Enhanced Agreement Parser Learning from Errors

### Prompt for Agent - Version 2 Parser Development

```
CONTEXT:
You are developing Version 2 of an EDGAR agreement parser. The current parser failed on 5/15 agreements and produced poor structural extraction on others. Key failures:
- Agreements 3,10,12,14,15: "Could not find HTML content" 
- Agreement 6: Contains non-HTML format (ZEQ metadata)
- Multiple agreements: Poor hierarchy detection, duplicate elements, missing structure

REQUIREMENTS:
Create a new agreement parser that:

1. PRE-PROCESSING PHASE
   - Implement format detection BEFORE parsing:
     ```python
     def detect_document_format(content: str) -> str:
         # Check for SGML format (look for <!DOCTYPE SGML)
         # Check for XML format (look for <?xml)
         # Check for wrapped HTML (EDGAR submission wrapper)
         # Check for text-based tables format
         # Return: 'html', 'sgml', 'xml', 'wrapped', 'text'
     ```
   
   - Create format converters:
     ```python
     class FormatConverter:
         def sgml_to_html(self, content: str) -> str:
             # Handle SGML entities (&nbsp; &amp; etc)
             # Convert SGML tags to HTML5
             # Preserve table structures
         
         def unwrap_edgar_submission(self, content: str) -> str:
             # Extract HTML from <HTML>...</HTML> or <XBRL>...</XBRL>
             # Handle multiple document boundaries
             # Preserve formatting
     ```

2. ROBUST HTML EXTRACTION
   - Don't assume BeautifulSoup will work on first try
   - Implement fallback parsing strategies:
     ```python
     def extract_html_content(raw_content: str) -> Optional[str]:
         # Try 1: Direct HTML extraction between <HTML> tags
         # Try 2: Extract between document markers
         # Try 3: Use regex to find HTML-like content
         # Try 4: Convert from detected format
         # Log which method succeeded for debugging
     ```

3. STRUCTURE-AWARE PARSING
   Instead of regex-first approach, use HTML structure:
   ```python
   class StructuralParser:
       def identify_hierarchy_by_formatting(self, elements: List[HtmlTag]) -> Dict:
           # Analyze font sizes, weights, styles
           # Identify hierarchy by visual prominence
           # Group elements by formatting similarity
           
       def identify_hierarchy_by_nesting(self, elements: List[HtmlTag]) -> Dict:
           # Use HTML nesting (div, p, table structures)
           # Identify parent-child relationships
           # Build tree from DOM structure
   ```

4. INTELLIGENT TITLE DETECTION
   ```python
   class TitleDetector:
       def __init__(self):
           self.strategies = [
               self.detect_by_position_and_style,
               self.detect_by_content_analysis,
               self.detect_by_document_flow,
               self.detect_by_metadata_context
           ]
       
       def detect_by_position_and_style(self, elements: List[HtmlTag]) -> Optional[HtmlTag]:
           # First substantive text after metadata
           # Centered + bold/large font
           # Isolated by whitespace
           # Contains agreement keywords
   ```

5. HANDLE SPECIAL CASES
   ```python
   # For Agreement 6 type (data format):
   def parse_data_format_agreement(content: str) -> List[Element]:
       # Extract key-value pairs
       # Identify section boundaries by patterns
       # Convert to standard elements
   
   # For table-heavy agreements:
   def parse_table_based_structure(tables: List[TableElement]) -> List[Element]:
       # Identify section headers in tables
       # Extract hierarchy from table structure
       # Preserve relationships
   ```

6. VALIDATION AND RECOVERY
   ```python
   class ParseValidator:
       def validate_parse_result(self, elements: List[Element]) -> ValidationResult:
           # Check: Has title?
           # Check: Has structure (sections/articles)?
           # Check: Reasonable element distribution?
           # Check: No massive text blocks?
           
       def attempt_recovery(self, elements: List[Element]) -> List[Element]:
           # If no title found, use first heading
           # If no structure, infer from numbering
           # If all text, split by patterns
   ```

DELIVERABLE:
Complete parser implementation with:
- All format detection/conversion code
- Structural parsing methods
- Special case handlers
- Comprehensive error handling
- Logging for debugging failed parses
```

## Task 2: Alternative HTML Structure-Based Approaches

### Prompt for Agent - Structural Parsing Strategies

```
CONTEXT:
Current parser relies heavily on regex patterns which fail on non-standard formats. Need alternative approaches that leverage HTML document structure.

DESIGN ALTERNATIVE PARSING STRATEGIES:

1. DOM-BASED HIERARCHICAL ANALYSIS
   ```python
   class DOMHierarchyParser:
       def build_visual_hierarchy(self, root: BeautifulSoup) -> Tree:
           """
           Strategy: Use computed visual properties to infer hierarchy
           - Calculate effective font size for each element
           - Measure visual prominence (bold, caps, centering)
           - Build hierarchy where larger/bolder = higher level
           """
           
       def analyze_nesting_patterns(self, root: BeautifulSoup) -> Dict:
           """
           Strategy: Use HTML nesting depth and patterns
           - Map div/section/article nesting
           - Identify consistent wrapper patterns
           - Infer hierarchy from DOM depth
           """
   ```

2. MACHINE LEARNING APPROACH
   ```python
   class MLStructureDetector:
       """
       Strategy: Train classifier on visual/textual features
       - Features: position, size, style, content, context
       - Labels: title, section, clause, content, metadata
       - Use pre-trained model or few-shot learning
       """
       
       def extract_features(self, element: HtmlTag) -> np.array:
           # Position features (top, relative position)
           # Style features (font size, weight, decoration)
           # Content features (length, capitals, keywords)
           # Context features (previous/next elements)
       
       def classify_element(self, features: np.array) -> ElementType:
           # Use trained model or heuristic scoring
   ```

3. TEMPLATE MATCHING APPROACH
   ```python
   class TemplateBasedParser:
       """
       Strategy: Identify document template and apply specific rules
       """
       def identify_template(self, doc: BeautifulSoup) -> str:
           # Check for law firm signatures
           # Identify EDGAR submission patterns  
           # Match against known templates
           
       templates = {
           'davis_polk': {
               'title_selector': 'p[align="center"] > b',
               'section_selector': 'p > b:contains("Section")',
               'hierarchy': ['article', 'section', 'subsection']
           },
           'generic_edgar': {
               'title_pattern': 'first centered bold text',
               'section_pattern': 'numbered paragraphs'
           }
       }
   ```

4. SEGMENTATION-BASED APPROACH
   ```python
   class DocumentSegmenter:
       """
       Strategy: Segment document into logical blocks first
       """
       def segment_by_visual_breaks(self, elements: List[HtmlTag]) -> List[Segment]:
           # Identify visual breaks (HR, page breaks, spacing)
           # Group elements between breaks
           # Classify each segment
           
       def segment_by_content_similarity(self, elements: List[HtmlTag]) -> List[Segment]:
           # Cluster similar elements
           # Identify transitions between types
           # Create logical segments
   ```

5. HYBRID PROGRESSIVE APPROACH
   ```python
   class ProgressiveParser:
       """
       Strategy: Start broad, progressively refine
       """
       def parse_document(self, html: str) -> Document:
           # Phase 1: Rough segmentation
           segments = self.rough_segment(html)
           
           # Phase 2: Classify segment types
           typed_segments = self.classify_segments(segments)
           
           # Phase 3: Extract internal structure
           for segment in typed_segments:
               if segment.type == 'content':
                   self.extract_subsections(segment)
           
           # Phase 4: Build relationships
           return self.build_hierarchy(typed_segments)
   ```

EVALUATION CRITERIA FOR EACH APPROACH:
- Robustness to format variations
- Performance on edge cases
- Computational efficiency
- Ease of debugging/maintenance
- Accuracy metrics

RECOMMENDATION:
Implement hybrid approach combining:
1. Template matching for known formats
2. DOM analysis for structure
3. ML classification for ambiguous elements
4. Progressive refinement for complex documents
```

## Task 3: Format Detection and Conversion

### Prompt for Agent - Multi-Format Handler

```
CONTEXT:
EDGAR documents come in multiple formats: HTML, SGML, XML, wrapped submissions, text tables. Parser must detect and handle all formats.

IMPLEMENT COMPREHENSIVE FORMAT HANDLER:

1. FORMAT DETECTION ENGINE
   ```python
   class FormatDetector:
       def detect_format(self, content: str) -> DocumentFormat:
           # Check file magic/headers
           if content.strip().startswith('<?xml'):
               return self.classify_xml_format(content)
           elif '<!DOCTYPE' in content[:1000]:
               return self.analyze_doctype(content)
           elif '<HTML>' in content or '<html>' in content:
               return DocumentFormat.HTML
           elif self.is_structured_text(content):
               return DocumentFormat.STRUCTURED_TEXT
           elif 'ZEQ=' in content[:100]:  # Agreement 6 pattern
               return DocumentFormat.DATA_FORMAT
           
       def classify_xml_format(self, content: str) -> DocumentFormat:
           # XBRL, EDGAR XML, or wrapped HTML?
           
       def is_structured_text(self, content: str) -> bool:
           # Tables with pipes or tabs?
           # Consistent indentation patterns?
   ```

2. FORMAT CONVERTERS
   ```python
   class UniversalConverter:
       converters = {
           DocumentFormat.SGML: SGMLToHTMLConverter(),
           DocumentFormat.EDGAR_WRAPPED: EdgarUnwrapper(),
           DocumentFormat.DATA_FORMAT: DataFormatParser(),
           DocumentFormat.TEXT_TABLE: TextTableToHTML(),
           DocumentFormat.XBRL: XBRLExtractor()
       }
       
   class SGMLToHTMLConverter:
       def convert(self, sgml_content: str) -> str:
           # Handle SGML specific entities
           # Convert deprecated tags
           # Fix malformed structures
           
   class EdgarUnwrapper:
       def unwrap(self, wrapped_content: str) -> str:
           # Find document boundaries
           # Extract each document
           # Return primary document HTML
           
   class DataFormatParser:
       def parse_data_format(self, content: str) -> str:
           # Parse key=value patterns
           # Identify logical sections
           # Generate clean HTML representation
   ```

3. ROBUST EXTRACTION
   ```python
   class ContentExtractor:
       def extract_document_content(self, raw_input: str) -> str:
           # Try multiple extraction strategies
           strategies = [
               self.extract_between_tags('<HTML>', '</HTML>'),
               self.extract_between_tags('<DOCUMENT>', '</DOCUMENT>'),
               self.extract_after_headers(),
               self.extract_by_content_detection()
           ]
           
           for strategy in strategies:
               result = strategy(raw_input)
               if self.validate_extraction(result):
                   return result
                   
       def validate_extraction(self, content: str) -> bool:
           # Has reasonable length?
           # Contains expected keywords?
           # Valid HTML structure?
   ```

4. SPECIAL FORMAT HANDLERS
   ```python
   # For ZEQ format (Agreement 6):
   class ZEQFormatHandler:
       def parse(self, content: str) -> Document:
           # Extract metadata fields
           # Identify content sections
           # Build structured document
           
   # For text-based tables:
   class TextTableHandler:
       def convert_to_html(self, text_table: str) -> str:
           # Detect column boundaries
           # Identify headers
           # Generate HTML table
   ```

5. ERROR RECOVERY
   ```python
   class FormatRecovery:
       def attempt_recovery(self, content: str, error: Exception) -> Optional[str]:
           # Try encoding fixes
           # Remove problematic characters
           # Attempt partial extraction
           # Last resort: extract all text
   ```

TESTING REQUIREMENTS:
- Test on all 15 agreement samples
- Verify each format detection works
- Ensure no data loss in conversion
- Maintain formatting fidelity
- Log format detection results
```

## Task 4: Universal EDGAR Parser - Final Integration

### Prompt for Agent - Complete System Integration

```
CONTEXT:
Build final parser that handles ALL EDGAR contract formats by integrating previous components.

CREATE UNIVERSAL EDGAR PARSER:

1. MAIN PARSER CLASS
   ```python
   class UniversalEDGARParser:
       def __init__(self):
           self.format_detector = FormatDetector()
           self.converter = UniversalConverter()
           self.structure_analyzer = StructureAnalyzer()
           self.element_classifier = ElementClassifier()
           self.hierarchy_builder = HierarchyBuilder()
           self.validator = ParseValidator()
           
       def parse(self, raw_content: str, metadata: Dict = None) -> ParseResult:
           try:
               # Step 1: Detect format
               doc_format = self.format_detector.detect_format(raw_content)
               self.log(f"Detected format: {doc_format}")
               
               # Step 2: Convert to normalized HTML
               html_content = self.converter.convert(raw_content, doc_format)
               
               # Step 3: Extract and preprocess
               cleaned_html = self.preprocess(html_content)
               
               # Step 4: Structural analysis
               structure = self.structure_analyzer.analyze(cleaned_html)
               
               # Step 5: Element classification
               elements = self.element_classifier.classify_all(structure)
               
               # Step 6: Build hierarchy
               tree = self.hierarchy_builder.build(elements)
               
               # Step 7: Validate and recover
               tree = self.validator.validate_and_fix(tree)
               
               return ParseResult(
                   success=True,
                   tree=tree,
                   format=doc_format,
                   elements=elements,
                   metadata=self.extract_metadata(elements)
               )
               
           except Exception as e:
               return self.handle_parse_failure(e, raw_content)
   ```

2. QUALITY ASSURANCE SYSTEM
   ```python
   class ParseQualityChecker:
       def check_parse_quality(self, result: ParseResult) -> QualityReport:
           checks = {
               'has_title': self.check_has_title(result),
               'has_structure': self.check_has_structure(result),
               'reasonable_hierarchy': self.check_hierarchy_depth(result),
               'no_giant_blocks': self.check_text_distribution(result),
               'metadata_removed': self.check_metadata_removal(result),
               'complete_content': self.check_content_completeness(result)
           }
           
           score = sum(1 for check in checks.values() if check) / len(checks)
           return QualityReport(score=score, checks=checks, suggestions=self.suggest_improvements(checks))
   ```

3. FALLBACK CASCADE
   ```python
   class FallbackParser:
       def parse_with_fallbacks(self, content: str) -> ParseResult:
           strategies = [
               ('structural', self.structural_parse),
               ('template', self.template_parse),
               ('heuristic', self.heuristic_parse),
               ('ml_assisted', self.ml_parse),
               ('basic', self.basic_parse)
           ]
           
           for name, strategy in strategies:
               try:
                   result = strategy(content)
                   if result.quality_score > 0.6:
                       return result
               except Exception as e:
                   self.log(f"Strategy {name} failed: {e}")
                   
           # Last resort
           return self.minimal_parse(content)
   ```

4. DEBUGGING AND MONITORING
   ```python
   class ParseMonitor:
       def __init__(self):
           self.stats = defaultdict(int)
           self.failures = []
           
       def record_parse(self, filename: str, result: ParseResult):
           self.stats['total'] += 1
           self.stats[f'format_{result.format}'] += 1
           self.stats[f'quality_{result.get_quality_tier()}'] += 1
           
           if not result.success:
               self.failures.append({
                   'file': filename,
                   'error': result.error,
                   'stage': result.failure_stage
               })
               
       def generate_report(self) -> str:
           # Success rate by format
           # Common failure patterns
           # Quality distribution
           # Recommendations
   ```

5. CONFIGURATION SYSTEM
   ```python
   class ParserConfig:
       # Adjustable parameters for different document types
       config = {
           'standard_html': {
               'title_detection_aggressive': False,
               'metadata_patterns': 'standard',
               'hierarchy_inference': 'strict'
           },
           'wrapped_edgar': {
               'title_detection_aggressive': True,
               'metadata_patterns': 'edgar_specific',
               'hierarchy_inference': 'flexible'
           },
           'text_format': {
               'structure_detection': 'indentation_based',
               'section_markers': 'numeric_and_alpha'
           }
       }
   ```

DELIVERABLES:
1. Complete parser implementation handling all formats
2. Test results on all 15 agreements showing 100% parse rate
3. Quality metrics for each parse
4. Documentation of handling strategies for each format type
5. Debug logs showing parse decisions

SUCCESS CRITERIA:
- All 15 agreements parse without errors
- Each agreement has identified title and structure  
- No metadata pollution in final output
- Hierarchical relationships preserved
- Human-readable output for all formats
```

## Summary of Key Improvements

The enhanced parser should:

1. **Pre-detect format** before attempting to parse
2. **Use HTML structure** instead of relying solely on regex
3. **Implement multiple strategies** with intelligent fallbacks
4. **Handle special formats** like data files and wrapped documents
5. **Validate results** and attempt recovery when needed
6. **Provide detailed debugging** to understand parse failures
7. **Learn from patterns** in successfully parsed documents

This comprehensive approach ensures the parser can handle the full variety of EDGAR filing formats while maintaining high accuracy in structure extraction.