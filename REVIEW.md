# Comprehensive Review of sec-parser

## Table of Contents
- [Executive Summary](#executive-summary)
- [Part 1: Core Features](#part-1-core-features)
- [Part 2: Ancillary Features](#part-2-ancillary-features)
- [Part 3: Function Usefulness Ranking for Your Use Case](#part-3-function-usefulness-ranking)
- [Part 4: Major and Minor Flaws](#part-4-major-and-minor-flaws)
- [Part 5: Suggested Improvements](#part-5-suggested-improvements)

---

## Executive Summary

**sec-parser** is an MIT-licensed Python library that parses SEC EDGAR HTML filings (10-K, 10-Q) into a hierarchical semantic tree of classified elements. It uses a pipeline architecture with 14 sequential processing steps, BeautifulSoup4/lxml for HTML parsing, and pandas for table extraction.

**Bottom line for your use case:** This library provides a solid ~60% foundation for what you need. It handles document segmentation, title hierarchy, and table detection well. However, it has significant gaps in table content extraction, no segment header ID system, no prose-vs-stub classification, and no diff-ready output. Forking and enhancing is the right approach.

---

## Part 1: Core Features

### 1.1 HTML Parsing Engine (`processing_engine/`)

**What it does:** Parses raw HTML into a flat list of top-level tags, then wraps each in an `HtmlTag` object (a cached wrapper around BeautifulSoup4 `Tag`).

**Key assumption:** SEC filings have *flat HTML structure* where each top-level `<div>`, `<p>`, or `<table>` typically maps to one semantic element. This is mostly true for EDGAR filings.

**Files:**
- `processing_engine/html_tag_parser.py` - Extracts top-level tags from `<body>`
- `processing_engine/html_tag.py` - `HtmlTag` wrapper with extensive caching (text, styles, metrics, markdown, source code)

**Verdict:** Well-designed. The caching strategy is appropriate given HTML immutability. The bs4 abstraction layer makes it easy to swap parsing backends later.

---

### 1.2 14-Step Processing Pipeline (`processing_engine/core.py`)

The core pipeline transforms `NotYetClassifiedElement` instances through these steps:

| # | Step | Purpose | Quality |
|---|------|---------|---------|
| 1 | `IndividualSemanticElementExtractor` | Splits multi-element containers (XBRL wrappers, text+table combos) into `CompositeSemanticElement` | Good |
| 2 | `ImageClassifier` | Tags elements containing `<img>` | Simple, correct |
| 3 | `EmptyElementClassifier` | Tags elements without alphanumeric content as `EmptyElement` (IrrelevantElement) | Simple, correct |
| 4 | `TableClassifier` | Tags elements containing `<table>` with >1 row as `TableElement` | Functional but basic |
| 5 | `TableOfContentsClassifier` | Identifies tables that are TOCs (contain "page" text) | Very basic heuristic |
| 6 | `TopSectionManager` (10Q/10K) | Two-pass: collects section title candidates, then selects best match per section type | Core value-add |
| 7 | `IntroductorySectionElementClassifier` | Tags content before first `TopSectionTitle` as introductory | Simple, correct |
| 8 | `TextClassifier` | Catch-all: any remaining element with alphanumeric text becomes `TextElement` | Simple, correct |
| 9 | `HighlightedTextClassifier` | Analyzes CSS styles to detect bold/italic/centered/uppercase/underline text | Good intermediate step |
| 10 | `SupplementaryTextClassifier` | Identifies parenthetical notes, italic disclaimers, financial statement references | Narrow rules |
| 11 | `PageHeaderClassifier` | Two-pass: finds short text appearing >= 5 times, marks as `PageHeaderElement` | Clever heuristic |
| 12 | `PageNumberClassifier` | Two-pass: finds short numeric patterns appearing >= 5 times, marks as `PageNumberElement` | Clever heuristic |
| 13 | `TitleClassifier` | Converts `HighlightedTextElement` to `TitleElement` with hierarchy level based on style order | Core value-add but fragile |
| 14 | `TextElementMerger` | Merges adjacent `TextElement` instances (fixes XBRL-split text) | Important for XBRL filings |

**Verdict:** The pipeline is well-structured and extensible. Steps 6, 11, 12, and 13 are the most valuable. Step 10 (supplementary text) is too narrow. Step 4 (table classification) is too simplistic for serious table work.

---

### 1.3 Semantic Element Type System (`semantic_elements/`)

```
AbstractSemanticElement
├── NotYetClassifiedElement          (starting point)
├── ErrorWhileProcessingElement      (error wrapper)
├── IrrelevantElement (base)
│   ├── PageNumberElement
│   ├── PageHeaderElement
│   ├── EmptyElement
│   └── IntroductorySectionElement
├── TextElement                      (standard prose)
├── SupplementaryText                (parenthetical notes)
├── ImageElement
├── HighlightedTextElement           (intermediate: styled text)
├── TitleElement (AbstractLevelElement) (with hierarchy level)
├── TableElement
│   └── TableOfContentsElement
├── CompositeSemanticElement         (container for multi-element wrappers)
├── TopSectionTitle                  (Part I, Item 1, etc.)
└── TopSectionStartMarker
```

**Verdict:** The hierarchy is reasonable but missing several element types you'll need (see improvements section).

---

### 1.4 Semantic Tree Builder (`semantic_tree/`)

**What it does:** Converts the flat element list into a hierarchical tree using stack-based nesting with configurable rules.

**Default nesting rules (in order):**
1. `AlwaysNestAsParentRule(TopSectionStartMarker)` - Top sections parent everything except other top sections
2. `AlwaysNestAsParentRule(TitleElement, exclude_children={TopSectionStartMarker})` - Titles parent non-titles
3. `NestSameTypeDependingOnLevelRule()` - Same-type elements nest by level (e.g., Title[L0] > Title[L1])

**Algorithm:** Stack-based. For each new element, walk the stack backward looking for a valid parent. If found, nest under it. If not, add as root.

**Verdict:** The tree builder is the library's strongest feature. The rule system is composable and extensible. The stack-based approach is correct for the document model.

---

### 1.5 Section Recognition (`top_section_manager.py`, `top_section_title_types.py`)

**10-Q sections defined:** 12 (Part I Items 1-4, Part II Items 1-6, plus Part headings)
**10-K sections defined:** 27 (Part I-IV with all sub-items including 1c Cybersecurity)

**Algorithm:** Two-pass.
- Pass 1: Regex-match "Part [I-IV]" and "Item [N]" patterns against element text
- Pass 2: Group candidates by section type, select best (prefer non-table elements), enforce monotonic ordering

**Verdict:** Handles standard section formats well. Brittle against non-standard formatting (e.g., "ITEM 1A:" with no space, merged Part+Item lines, tabular TOC entries matching the pattern). The ordering enforcement (`_last_order_number`) is a useful guard against false positives.

---

## Part 2: Ancillary Features

### 2.1 Table Extraction (`table_element/table_parser.py`)

**What it does:** Wraps `pandas.read_html()` with post-processing:
1. Parse HTML table via pandas/lxml
2. Drop all-NA rows and columns
3. Treat first row as headers
4. Remove blank duplicate columns
5. Merge `$` and `%` marker columns back into data columns
6. Re-index columns numerically

**Verdict:** This is the weakest part of the library for your use case. It only parses the *first* table found, loses structural information (merged cells, row spans), and the `$`/`%` marker merging is fragile. The `table_to_markdown()` method is more useful than `parse_as_df()` for downstream processing.

---

### 2.2 Text Style Analysis (`highlighted_text_element.py`, `bs4_/text_styles_metrics.py`)

**TextStyle** tracks 5 properties:
- `is_all_uppercase` (>= 80% caps in text)
- `bold_with_font_weight` (font-weight >= 600 or "bold", affecting >= 80% of text)
- `italic` (font-style: italic, >= 80%)
- `centered` (text-align: center, >= 80%)
- `underline` (text-decoration: underline, >= 80%)

**Limitation:** Only reads inline `style` attributes. Does **not** read `<b>`, `<i>`, `<u>`, `<strong>`, `<em>` HTML tags directly, nor `<style>` blocks or class-based CSS. The 80% threshold is hard-coded and non-configurable.

**Verdict:** Sufficient for most EDGAR filings (which use inline styles heavily), but will miss formatting in older filings that use HTML tags for styling.

---

### 2.3 Tree Rendering (`render_.py`)

**What it does:** Produces ASCII tree visualizations with ANSI color codes:
```
TopSectionTitle: Part I - Financial Information
├── TitleElement: Financial Statements
│   ├── TextElement: The accompanying notes...
│   └── TableElement: Table with ~45 rows, ~12 numbers...
└── TitleElement: MD&A
    └── TextElement: Management believes...
```

**Verdict:** Useful for debugging. Not designed for production output. The `char_display_limit=65` truncation is too aggressive for real analysis.

---

### 2.4 Processing Log (`processing_log.py`)

Each semantic element carries a `ProcessingLog` recording every classification decision:
```
"Identified as candidate: part1item2"
"this.order=2 last_order_number=1"
"Contains single element: False"
```

**Verdict:** Excellent for debugging and understanding classification decisions. No performance concern since it's append-only.

---

### 2.5 XBRL Handling (`xbrl_tag_check.py`, `text_element_merger.py`)

**What it does:** Detects `<ix:*>` XBRL inline tags that wrap multiple visual elements. Splits these into `CompositeSemanticElement` with children. Later, `TextElementMerger` recombines adjacent text fragments that were split by XBRL tagging.

**Verdict:** This is important for modern EDGAR filings (post-2020) which are heavily XBRL-tagged. The splitting and re-merging approach is correct. However, the XBRL tag metadata (concept names, context references) is **completely discarded** - a major loss for your financial analysis use case.

---

### 2.6 Composite Element System (`composite_semantic_element.py`)

**What it does:** Wraps elements that contain multiple semantic children (e.g., a `<div>` containing both prose and a table). Supports recursive unwrapping via `unwrap_elements()`.

**Verdict:** Architecturally sound. Correctly preserves the original HTML structure while allowing flat iteration. The `include_containers` option is useful for document reconstruction.

---

### 2.7 Dashboard App (`dev_utils/dashboard_app/`)

A Streamlit-based debugging dashboard for visualizing parsed filings. Not part of the core library.

**Verdict:** Useful for development/debugging only. Not relevant to your production use case.

---

## Part 3: Function Usefulness Ranking

Ranked by relevance to your 5 stated goals:

### Tier 1: Essential (use directly, enhance in fork)

| Component | Why Essential | Your Goal |
|-----------|--------------|-----------|
| `TreeBuilder.build()` | Creates the hierarchical document structure you need for TOC navigation | Goal 2 (TOC navigation) |
| `TopSectionManager` + `FilingSectionsIn10K/10Q` | Identifies Part/Item sections - your top-level segment headers | Goals 1, 2 |
| `TitleClassifier` + `TitleElement` | Provides the sub-section heading hierarchy within each Part/Item | Goals 1, 2 |
| `TableClassifier` + `TableElement` | Identifies all tables in the document | Goal 3 |
| `IndividualSemanticElementExtractor` + `TableCheck` | Separates tables from surrounding prose (critical for Goal 4) | Goals 3, 4 |
| `AbstractSemanticElement.text` / `.get_source_code()` | Your primary text extraction mechanism | Goal 1 |
| `HtmlTag` caching layer | Performance-critical for large filings (10-Ks can be 500+ pages) | All goals |

### Tier 2: Very Useful (use with minor modifications)

| Component | Why Useful | Your Goal |
|-----------|-----------|-----------|
| `HighlightedTextClassifier` + `TextStyle` | Identifies styled text (headings, emphasis) for hierarchy detection | Goal 2 |
| `PageNumberClassifier` + `PageHeaderClassifier` | Removes noise from your text extraction | Goal 1 |
| `TextElementMerger` | Fixes XBRL-split text (critical for clean text extraction) | Goals 1, 5 |
| `EmptyElementClassifier` | Removes whitespace-only elements from output | Goal 1 |
| `CompositeSemanticElement` | Preserves table-with-prose relationships (critical for Goal 4) | Goal 4 |
| Nesting rules system | Extensible - add custom rules for your TOC builder | Goal 2 |
| `SupplementaryTextClassifier` | Identifies the "stub prose" you want to discard around tables (Goal 4) | Goal 4 |
| `TableElement.table_to_markdown()` | Quick text representation of tables for diffing | Goal 5 |

### Tier 3: Useful As-Is (no modification needed)

| Component | Why Useful | Your Goal |
|-----------|-----------|-----------|
| `IntroductorySectionElementClassifier` | Correctly skips cover pages and disclaimers | Goal 1 |
| `ImageClassifier` | Identifies and classifies images you can filter out | Goal 1 |
| Pipeline architecture (step injection/replacement) | Your enhancement strategy - add/replace steps without rewriting | All goals |
| Processing logs | Debugging aid during enhancement | All goals |
| `render()` | Quick visual verification of parse results | Debugging |

### Tier 4: Low Value for Your Use Case

| Component | Why Low Value |
|-----------|--------------|
| `TableParser.parse_as_df()` | Too lossy - you need better table extraction |
| `TableOfContentsClassifier` | Detects TOC tables but doesn't parse them - you need actual TOC extraction |
| Dashboard app | Development tool, not production |
| `get_approx_table_metrics()` | Rough estimates, not useful for serious table analysis |

---

## Part 4: Major and Minor Flaws

### MAJOR FLAWS

#### M1. Title Hierarchy Detection is Fragile (`title_classifier.py:45-66`)

**The problem:** Title levels are assigned based on *order of first style occurrence* in the document. The first unique `TextStyle` seen becomes Level 0, second becomes Level 1, etc.

**Why this is major:** This assumes the document presents styles in hierarchical order (broadest heading first). Many 10-Ks start with a centered bold title, then use bold for items and italic-bold for sub-items. If the first styled text in the document happens to be an italic disclaimer, the entire hierarchy gets shifted.

**Example failure:**
```
<p style="font-style:italic">See accompanying notes</p>  ← Style A = Level 0 (wrong!)
<p style="font-weight:bold">PART I</p>                    ← Style B = Level 1 (should be 0)
<p style="font-weight:bold;font-style:italic">Item 1</p>  ← Style C = Level 2 (should be 1)
```

**Impact on your goals:** Incorrect title hierarchy will break your TOC navigation (Goal 2) and segment header identification (Goal 1).

**Note:** The `SupplementaryTextClassifier` runs *before* `TitleClassifier` and would catch the italic disclaimer in this specific example - but many edge cases remain where a non-title styled element appears first.

---

#### M2. No Element-Level Identifier System

**The problem:** Semantic elements have no stable identifier (no ID, no index, no hash-based reference). Elements are identified only by their Python object identity or position in the list.

**Why this is major:** You need "segment header IDs" (Goal 1) and "table identification" (Goal 3). Currently there's no way to reference a specific element across parses or between versions of a filing (critical for Goal 5: text-diffing).

---

#### M3. XBRL Metadata is Completely Discarded

**The problem:** XBRL inline tags (`<ix:nonnumeric>`, `<ix:nonFraction>`) contain rich metadata:
- `name="us-gaap:Revenue"` - the GAAP concept
- `contextref="c-1"` - time period/entity context
- `unitref="usd"` - currency/unit
- `id="f-123"` - unique identifier

The library strips all of this during the XBRL handling step (`xbrl_tag_check.py`), keeping only the visual text.

**Why this is major:** For Goal 3 (identifying non-XBRL-tagged tables), you first need to know *which* tables ARE XBRL-tagged. And the discarded XBRL metadata is extremely valuable for table identification and number-diffing (Goal 5).

---

#### M4. Table Content Extraction is Inadequate (`table_parser.py`)

**The problem:**
1. `parse_as_df()` only extracts the *first* `<table>` found via `pd.read_html()`
2. Header detection is naive (assumes first row = header)
3. Merged cells (`colspan`, `rowspan`) are not handled
4. The `$`/`%` marker merging logic modifies DataFrames in place during iteration - can produce incorrect results with certain column arrangements
5. No metadata about table type (financial statement, schedule, footnote table, etc.)

**Why this is major:** Table extraction is central to Goals 3, 4, and 5. The current implementation loses too much structural information for financial analysis.

---

#### M5. Style Detection Ignores HTML Tags (`highlighted_text_element.py:80-143`)

**The problem:** `TextStyle.from_style_and_text()` only analyzes CSS `style` attributes. It does not detect:
- `<b>`, `<strong>` - bold
- `<i>`, `<em>` - italic
- `<u>` - underline
- `<h1>`-`<h6>` - heading tags
- Class-based styles from `<style>` blocks

**Why this is major:** Older EDGAR filings (pre-2015) and some filers use HTML tags rather than inline CSS for formatting. These filings will have **zero title detection**, causing a flat tree with no hierarchy.

---

#### M6. `FilingSections` Definitions Have No Validation Against SEC Standards

**The problem:** The `FilingSectionsIn10K` and `FilingSectionsIn10Q` definitions in `top_section_title_types.py` are hardcoded. There's no mechanism to validate that these match current SEC Regulation S-K requirements or to handle historical filing format changes.

**Example:** The 10-K definition includes `part1item1c` (Cybersecurity) which was added by SEC rule in Dec 2023. Filings before that date won't have this section, yet the code doesn't handle its absence gracefully.

---

### MINOR FLAWS

#### m1. Bug in `TableElement.get_summary()` (line 23)

```python
return "Table with {len(self.text)} characters."  # Missing f-string prefix!
```

This returns the literal string `"Table with {len(self.text)} characters."` instead of the actual character count. Should be:
```python
return f"Table with {len(self.text)} characters."
```

---

#### m2. `TopSectionManager` Contains Dead/Debugging Code (`top_section_manager.py:347-379`)

The file ends with two large multi-line docstrings that appear to be algorithm notes and a "ChatGPT improved version" of the algorithm description. These are dead code sitting at module level and suggest the code was written with AI assistance and not cleaned up.

---

#### m3. Hard-Coded Thresholds Throughout

- `TextStyle.PERCENTAGE_THRESHOLD = 80` - style detection threshold
- `TextStyle.BOLD_THRESHOLD = 600` - font-weight for bold
- `PageNumberCandidate.TEXT_LENGTH_THRESHOLD = 100` - max length for page number candidates
- `PageNumberCandidate.OCCURRENCE_THRESHOLD = 5` - min occurrences to qualify
- `PageHeaderCandidate.OCCURRENCE_THRESHOLD = 5`
- `TableClassifier._row_count_threshold = 1`

None of these are configurable via `ParsingOptions` or constructor parameters (except `_row_count_threshold` which is set in `__init__` but not exposed).

---

#### m4. `_find_parent_node` Destructively Pops the Stack (`tree_builder.py:91-104`)

```python
def _find_parent_node(self, new_node, stack, rules):
    while stack:
        potential_parent = stack[-1]
        if self._should_nest_under(new_node, potential_parent, rules):
            return potential_parent
        stack.pop()  # <-- Destructive! Removes elements that could be parents for LATER nodes
    return None
```

This means if a sequence of elements doesn't nest properly, earlier context is permanently lost. For example, after a table that doesn't nest under any title, all accumulated title context is popped off the stack.

---

#### m5. No Error Recovery in Pipeline

If a processing step throws an exception for one element, `ErrorWhileProcessingElement` wraps it - but the pipeline continues. There's no mechanism to:
- Retry with different parameters
- Fall back to a simpler classification
- Report aggregate error statistics

---

#### m6. `render_` Has Incorrect Prefix Accumulation (`render_.py:98`)

```python
_prefix=_prefix + (_prefix if _is_root else new_prefix),
```

When rendering the first level of children under a root, this doubles the prefix string unnecessarily. The visual output is still correct in most cases due to the empty initial prefix, but the string grows quadratically for deep trees.

---

#### m7. Page Header/Number Detection Requires 5+ Occurrences

The `OCCURRENCE_THRESHOLD = 5` means filings shorter than ~5 pages won't have their page numbers or headers detected. This is fine for typical 10-Ks (50-300 pages) but may fail for short 10-Qs or amendment filings.

---

#### m8. `TopSectionManager.match_part()` Only Handles Parts I-IV

```python
roman_map = {"i": "1", "ii": "2", "iii": "3", "iv": "4"}
```

No Part V+ handling. While SEC filings don't currently have Part V, this is a needless limitation if you expand to other filing types.

---

#### m9. Single-Pass Pipeline Cannot Reclassify

Once an element is classified (e.g., as `TextElement`), later steps cannot reclassify it unless the step explicitly processes that type. This means:
- A `TextElement` that should be `SupplementaryText` but doesn't match the narrow rules stays as `TextElement`
- A `HighlightedTextElement` that's actually a table header (not a document title) gets promoted to `TitleElement`

---

#### m10. `TableOfContentsClassifier` is Extremely Simplistic

The TOC detection (`is_table_of_content()`) simply checks if the table contains the text "page" via `check_table_contains_text_page()`. This will:
- Miss TOCs that use "Pg." or "Page No." or have no page column
- False-positive on tables that mention "page" in their data (e.g., "as described on page 45")

---

## Part 5: Suggested Improvements

### Aligned to Goal 1: Extract All Text with Segment Header ID

#### I1. Add a Stable Element Identifier System

**What:** Add a `segment_id` property to `AbstractSemanticElement` that encodes the element's position in the document hierarchy.

**Format suggestion:** `{filing_type}:{section}:{subsection}:{element_index}` e.g., `10-K:part2item7:mda_overview:p3`

**How it helps:** Enables referencing specific segments across parses, between filing versions, and in downstream databases. Critical for your diff pipeline (Goal 5).

**Implementation approach:**
- Add `element_index: int` to `AbstractSemanticElement.__init__` (assigned during parsing)
- Add a post-processing step that generates hierarchical IDs from the tree structure
- IDs should be deterministic given the same input HTML

---

#### I2. Preserve XBRL Tag Metadata

**What:** Instead of stripping `<ix:*>` tags, extract their attributes into a metadata dict on the element.

**How it helps:**
- Identifies which text/numbers are XBRL-tagged (Goal 3: finding non-tagged tables)
- Provides GAAP concept names for downstream financial analysis
- Gives you unique IDs from the filing itself (`id="f-123"`)

**Implementation approach:**
- Modify `XbrlTagCheck` to store `{name, contextref, unitref, id, format, scale}`
- Add `xbrl_metadata: dict | None` to `AbstractSemanticElement`
- Propagate through `CompositeSemanticElement` to children

---

### Aligned to Goal 2: Intelligent Table of Contents Navigation

#### I3. Build a Proper TOC Data Structure

**What:** Create a `DocumentTableOfContents` class that the `TreeBuilder` output can populate, with:
- Section title text
- Section type (Part/Item/subsection)
- Hierarchy level
- Element count per section
- Contains-tables flag
- Byte offset range in source HTML

**How it helps:** Directly serves your TOC navigation feature. The current tree has the structure but lacks the metadata and query interface.

**Implementation approach:**
- New post-processing step: `TocBuilder` that walks the `SemanticTree`
- Each `TocEntry` contains: `id`, `title`, `level`, `parent_id`, `element_range`, `has_tables`, `has_financial_data`
- Add `tree.get_toc()` convenience method

---

#### I4. Fix Title Hierarchy Detection

**What:** Replace the order-of-first-occurrence approach with a scoring system:

```
Score = (is_uppercase * 4) + (is_bold * 3) + (is_centered * 2) + (is_underline * 1) - (is_italic * 0.5)
Higher score = higher-level heading
```

**How it helps:** Produces correct title levels regardless of which styled element appears first in the document. Critical for accurate TOC.

**Implementation approach:**
- Modify `TitleClassifier` to collect all `HighlightedTextElement` styles in pass 1
- Score and rank styles in pass 2
- Assign levels based on score rank rather than insertion order

---

### Aligned to Goal 3: Identify All Tables (Including Non-XBRL)

#### I5. Enhanced Table Classification

**What:** Add a `TableType` enum and classifier that categorizes tables:

```python
class TableType(Enum):
    FINANCIAL_STATEMENT = "financial_statement"  # Balance sheet, income statement, etc.
    FOOTNOTE_TABLE = "footnote_table"            # Tables within footnotes
    SCHEDULE = "schedule"                         # Supporting schedules
    PROSE_TABLE = "prose_table"                   # Tables used for text layout (not real data)
    TOC_TABLE = "toc_table"                       # Table of contents
    EXHIBIT_TABLE = "exhibit_table"               # Exhibit lists
    UNKNOWN = "unknown"
```

**How it helps:** Lets you filter tables by purpose. Financial statement tables need different handling than prose layout tables.

**Classification heuristics:**
- FINANCIAL_STATEMENT: Contains `$` markers, has numeric columns, near financial statement section titles
- FOOTNOTE_TABLE: Inside a footnote section, smaller than financial statements
- PROSE_TABLE: Single column or mostly text cells, used for formatting
- TOC_TABLE: Contains "page" column, matches section title patterns

---

#### I6. XBRL Coverage Annotation

**What:** For each `TableElement`, add a property `xbrl_coverage: float` indicating what percentage of the table's numeric cells are XBRL-tagged.

**How it helps:** Tables with 0% XBRL coverage are your non-tagged tables (Goal 3). Tables with partial coverage may have important un-tagged supplemental data.

---

### Aligned to Goal 4: Prose Stub Detection and Table-Prose Relationship

#### I7. Table Context Classifier

**What:** A new processing step that examines the text elements immediately before and after each table, classifying the relationship:

```python
class TableContext(Enum):
    STANDALONE = "standalone"           # Table needs no surrounding prose
    PROSE_INTRODUCES = "prose_intro"    # Preceding prose explains the table
    STUB_REFERENCE = "stub_reference"   # "See table below" type stub (discard)
    CONTINUATION = "continuation"       # Table continues from previous
```

**How it helps:** Directly implements Goal 4 - discard stub prose, keep useful surrounding context.

**Heuristics for stub detection:**
- Text < 100 characters AND contains "table below", "following table", "refer to", "as follows"
- Text immediately followed by table with no intervening content
- No independent information beyond pointing to the table

**Implementation approach:**
- New step: `TableContextClassifier` runs after `TextElementMerger`
- Adds `context: TableContext` metadata to `TableElement`
- Optionally links the related `TextElement` to the `TableElement` as `context_text`

---

### Aligned to Goal 5: Downstream Processing for Text-Diffing and Number-Diffing

#### I8. Serialization to Diff-Ready Format

**What:** Add export methods that produce structured output suitable for diffing:

```python
# Text diffing
element.to_diff_text() -> str
# Returns: "{segment_id}\t{element_type}\t{normalized_text}"

# Number diffing for tables
table_element.to_diff_numbers() -> list[dict]
# Returns: [{"segment_id": "...", "row": 0, "col": "Revenue", "value": "1234.56", "xbrl_concept": "us-gaap:Revenue"}]

# Full document
tree.to_diff_document() -> str
# Returns line-per-element format for standard diff tools
```

**How it helps:** Enables `diff`/`git diff` workflows between filing periods. The segment IDs make alignment across periods trivial.

---

#### I9. Numeric Value Extraction from Tables

**What:** Add a `TableElement.extract_numbers()` method that returns structured numeric data:

```python
@dataclass
class ExtractedNumber:
    value: Decimal
    raw_text: str          # "(1,234.56)"
    row_label: str         # "Total Revenue"
    column_label: str      # "2024"
    is_negative: bool      # True (parenthetical)
    unit: str | None       # "$" or "%" or None
    xbrl_concept: str | None  # "us-gaap:Revenue"
    scale: int             # 6 for "in millions"
```

**How it helps:** Critical for number-diffing (Goal 5). Current `parse_as_df()` returns strings, losing numeric semantics.

---

### General Architecture Improvements

#### I10. Make Thresholds Configurable

**What:** Consolidate all thresholds into a `ParsingConfig` dataclass passed through the pipeline:

```python
@dataclass
class ParsingConfig:
    style_percentage_threshold: float = 80.0
    bold_font_weight_threshold: int = 600
    page_number_occurrence_threshold: int = 5
    page_header_occurrence_threshold: int = 5
    table_min_rows: int = 1
    page_element_text_length_max: int = 100
    capitalize_threshold: float = 80.0
```

**How it helps:** Different filings/filers may need different thresholds. Hardcoded values force fork users to modify library internals.

---

#### I11. Add HTML Tag-Based Style Detection

**What:** Extend `TextStyle.from_style_and_text()` to also check for `<b>`, `<strong>`, `<i>`, `<em>`, `<u>`, `<h1>`-`<h6>` tags.

**How it helps:** Fixes Major Flaw M5. Enables correct title detection for older filings and non-CSS-styled documents.

**Implementation:** In `compute_text_styles_metrics()`, traverse the tag hierarchy and add synthetic style entries for formatting tags:
- `<b>`, `<strong>` → `("font-weight", "bold")`
- `<i>`, `<em>` → `("font-style", "italic")`
- `<u>` → `("text-decoration", "underline")`
- `<h1>`-`<h6>` → `("font-weight", "bold")` + custom heading level metadata

---

#### I12. Fix the f-string Bug

**What:** In `table_element.py:23`, change:
```python
return "Table with {len(self.text)} characters."
```
to:
```python
return f"Table with {len(self.text)} characters."
```

---

### Improvement Priority Matrix

For your fork focusing on 10-K/10-Q with the 5 stated goals:

| Priority | Improvement | Effort | Impact |
|----------|------------|--------|--------|
| **P0 - Do First** | I2 (Preserve XBRL metadata) | Medium | Unlocks Goals 3, 5 |
| **P0 - Do First** | I1 (Stable element IDs) | Medium | Unlocks Goals 1, 5 |
| **P0 - Do First** | I12 (Fix f-string bug) | Trivial | Bug fix |
| **P1 - Do Soon** | I4 (Fix title hierarchy) | Medium | Fixes Goal 2 reliability |
| **P1 - Do Soon** | I11 (HTML tag style detection) | Medium | Fixes title detection for older filings |
| **P1 - Do Soon** | I7 (Table context classifier) | Medium | Enables Goal 4 |
| **P1 - Do Soon** | I5 (Enhanced table classification) | Medium | Enables Goal 3 |
| **P2 - Important** | I3 (TOC data structure) | Medium | Enables Goal 2 |
| **P2 - Important** | I8 (Diff-ready serialization) | Medium | Enables Goal 5 |
| **P2 - Important** | I10 (Configurable thresholds) | Low | Improves maintainability |
| **P3 - Nice to Have** | I9 (Numeric extraction) | High | Enhances Goal 5 |
| **P3 - Nice to Have** | I6 (XBRL coverage annotation) | Low | Enhances Goal 3 |

---

## Appendix: Key File Locations

| Component | File |
|-----------|------|
| Main parser entry | `sec_parser/processing_engine/core.py` |
| HTML tag wrapper | `sec_parser/processing_engine/html_tag.py` |
| All element types | `sec_parser/semantic_elements/semantic_elements.py` |
| Title classification | `sec_parser/processing_steps/title_classifier.py` |
| Table classification | `sec_parser/processing_steps/table_classifier.py` |
| Table parsing | `sec_parser/semantic_elements/table_element/table_parser.py` |
| Section recognition | `sec_parser/processing_steps/top_section_manager.py` |
| Section definitions | `sec_parser/semantic_elements/top_section_title_types.py` |
| Tree builder | `sec_parser/semantic_tree/tree_builder.py` |
| Nesting rules | `sec_parser/semantic_tree/nesting_rules.py` |
| Style detection | `sec_parser/semantic_elements/highlighted_text_element.py` |
| Supplementary text | `sec_parser/processing_steps/supplementary_text_classifier.py` |
| XBRL handling | `sec_parser/processing_steps/individual_semantic_element_extractor/single_element_checks/xbrl_tag_check.py` |
| TOC detection | `sec_parser/processing_steps/table_of_contents_classifier.py` |
| Page number detection | `sec_parser/processing_steps/page_number_classifier.py` |
| Text merging | `sec_parser/processing_steps/text_element_merger.py` |
| Rendering | `sec_parser/semantic_tree/render_.py` |
