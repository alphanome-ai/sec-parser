# Comprehensive Review of sec-parser

**Scope:** US-listed entities, English-only filings, 2015+ (inline CSS era), 10-K and 10-Q initially.
**XBRL assumption:** Tagged facts handled separately by edgartools. sec-parser is responsible for structural parsing only.

---

## Revised Goals

| # | Goal | Description |
|---|------|-------------|
| G1 | **Segment-Addressed Text Extraction** | Extract all text from a filing with a stable, hierarchical segment header ID attached to each element. Every piece of text must know which section it belongs to. |
| G2 | **Smart TOC Navigation** | Build a structured Table of Contents that powers an interactive floating pill UI (Intersection Observer, idle/scroll/hover states, section-jump). Requires: unique section IDs, hierarchy levels, section boundaries, and active-section tracking data. |
| G3 | **Complete Table Inventory** | Identify and catalogue every table in the filing. Classify each by purpose (financial statement, footnote, layout, TOC, schedule). For tables not XBRL-tagged, capture surrounding prose as context where useful. |
| G4 | **Prose-Table Relationship** | For each table, determine whether the surrounding prose is substantive context (keep it) or a stub reference like "refer to the table below" (discard the prose, present only the table). |
| G5 | **Diff-Ready Output** | Produce normalized, segment-addressed text and table output suitable for downstream text-diffing (prose changes across periods) and number-diffing (financial figure changes across periods). |

**Non-goals for this phase:** Pre-2015 filing compatibility, non-English filings, XBRL fact extraction (handled by edgartools), non-10-K/10-Q form types.

---

## Part 1: Core Features

### 1.1 HTML Parsing Engine

**Files:** `processing_engine/html_tag_parser.py`, `processing_engine/html_tag.py`

The `HtmlTagParser` extracts top-level HTML elements from `<body>`, producing a flat list. Each is wrapped in `HtmlTag`, a cached abstraction over BeautifulSoup4 `Tag` objects.

`HtmlTag` provides:
- `text` - recursive text extraction (cached)
- `get_source_code()` - raw or prettified HTML (cached)
- `contains_tag()` - descendant tag search (cached)
- `get_text_styles_metrics()` - CSS style percentage distribution (cached)
- `get_approx_table_metrics()` - row/number counts for tables (cached)
- `table_to_markdown()` - markdown conversion via `TableToMarkdown` (cached)
- `is_table_of_content()` - TOC detection heuristic
- `get_children()`, `has_tag_children()`, `is_unary_tree()` - structural queries
- `without_tags()`, `count_tags()`, `has_text_outside_tags()` - filtering helpers
- `to_dict()` - hash + preview for debugging

**Verdict for our goals:** Strong foundation. The caching strategy is correct for immutable HTML. The `HtmlTag` abstraction isolates us from bs4 internals. Key gap: no positional/offset information (needed for G2 Intersection Observer mapping).

---

### 1.2 Processing Pipeline

**File:** `processing_engine/core.py`

Both `Edgar10QParser` and `Edgar10KParser` inherit from `AbstractSemanticElementParser` and define a 14-step pipeline. Every element starts as `NotYetClassifiedElement` and is progressively reclassified.

The pipeline is configured via `get_default_steps()` and `get_default_single_element_checks()`. Custom steps can be injected or replaced via the `get_steps` callable parameter.

**The 14 steps, reviewed against our goals:**

| # | Step Class | What It Does | Quality | Our Goals |
|---|-----------|--------------|---------|-----------|
| 1 | `IndividualSemanticElementExtractor` | Splits containers with mixed content (text + table, multiple tables) into `CompositeSemanticElement`. Uses `TableCheck`, `XbrlTagCheck`, `ImageCheck`, `TopSectionTitleCheck`. | Good | G3, G4 |
| 2 | `ImageClassifier` | Detects `<img>` tags, reclassifies to `ImageElement` | Fine as-is | - |
| 3 | `EmptyElementClassifier` | Tags content-free elements as `EmptyElement` (subclass of `IrrelevantElement`, filtered from output) | Fine as-is | G1 |
| 4 | `TableClassifier` | Tags elements containing `<table>` with >1 row as `TableElement`. Uses `get_approx_table_metrics()` for row counting. Threshold is hardcoded at 1 row. | Functional but needs enhancement | G3 |
| 5 | `TableOfContentsClassifier` | Reclassifies `TableElement` to `TableOfContentsElement` if any `<td>` contains "page"/"page no."/"page number" | Too simplistic | G2, G3 |
| 6 | `TopSectionManagerFor10Q` / `TopSectionManagerFor10K` | Two-pass: regex-matches "Part [I-IV]" and "Item [N]" against element text, groups candidates by section type, selects best match per section with monotonic ordering. | Core value-add, some brittleness | G1, G2 |
| 7 | `IntroductorySectionElementClassifier` | Two-pass: marks everything before "Part 1" as `IntroductorySectionElement` (an `IrrelevantElement` subclass, filtered out) | Fine as-is | G1 |
| 8 | `TextClassifier` | Catch-all: remaining elements with alphanumeric content become `TextElement` | Fine as-is | G1 |
| 9 | `HighlightedTextClassifier` | Analyzes inline CSS via `get_text_styles_metrics()` to produce a `TextStyle` (bold, italic, centered, uppercase, underline). Promotes `TextElement` to `HighlightedTextElement`. | Good for 2015+ filings | G2 |
| 10 | `SupplementaryTextClassifier` | Reclassifies text matching narrow patterns: parenthetical text `(...)`, italic text ending in `.`, or text mentioning "notes" + "financial statements". | Too narrow for G4 | G4 |
| 11 | `PageHeaderClassifier` | Two-pass statistical: short text (<100 chars) appearing 5+ times becomes `PageHeaderElement` (irrelevant). Considers both text content and style. | Clever, effective | G1 |
| 12 | `PageNumberClassifier` | Two-pass statistical: short text with digits, non-digit pattern appearing 5+ times becomes `PageNumberElement` (irrelevant). | Clever, effective | G1 |
| 13 | `TitleClassifier` | Converts every `HighlightedTextElement` to `TitleElement` with a hierarchy level based on the order each unique `TextStyle` first appears. | Fragile - core concern | G1, G2 |
| 14 | `TextElementMerger` | Merges adjacent `TextElement` instances separated only by `IrrelevantElement` gaps, wrapping them in a synthetic `<sec-parser-merged-text>` tag. | Important for XBRL-era text | G1, G5 |

**Key architectural properties:**
- `AbstractElementwiseProcessingStep._process_recursively()` handles `CompositeSemanticElement` children automatically
- `_NUM_ITERATIONS` on each step controls multi-pass behavior (used by steps 6, 7, 11, 12)
- `types_to_process` and `types_to_exclude` filter which elements each step touches
- Errors caught per-element via `ErrorWhileProcessingElement` wrapping
- `parse()` accepts `unwrap_elements`, `include_containers`, `include_irrelevant_elements` flags

---

### 1.3 Semantic Element Type System

**Files:** `semantic_elements/abstract_semantic_element.py`, `semantic_elements/semantic_elements.py`, and subclass files

```
AbstractSemanticElement
 ├── NotYetClassifiedElement
 ├── ErrorWhileProcessingElement
 ├── IrrelevantElement
 │   ├── EmptyElement
 │   ├── PageNumberElement
 │   ├── PageHeaderElement
 │   └── IntroductorySectionElement
 ├── TextElement (with DictTextContentMixin)
 ├── SupplementaryText (with DictTextContentMixin)
 ├── ImageElement
 ├── HighlightedTextElement (carries TextStyle)
 ├── TitleElement (AbstractLevelElement, with level: int)
 ├── TopSectionStartMarker (AbstractLevelElement, with section_type: TopSectionInFiling)
 │   └── TopSectionTitle (also has DictTextContentMixin)
 ├── TableElement
 │   └── TableOfContentsElement
 └── CompositeSemanticElement (container with inner_elements tuple)
```

Every element exposes:
- `.text` - plain text content
- `.html_tag` - underlying `HtmlTag`
- `.get_source_code()` - raw HTML
- `.get_summary()` - human-readable summary (overridden by `TableElement`)
- `.to_dict()` - serialization with optional previews/contents
- `.processing_log` - full audit trail of classification decisions
- `.contains_words()` - has alphanumeric content
- `.create_from_element()` - type-conversion factory that preserves the processing log

`AbstractLevelElement` adds `.level: int` (used by `TitleElement` and `TopSectionStartMarker`).
`TopSectionStartMarker` adds `.section_type: TopSectionInFiling` (identifier, title, order, level).

---

### 1.4 Tree Builder

**Files:** `semantic_tree/tree_builder.py`, `semantic_tree/nesting_rules.py`, `semantic_tree/semantic_tree.py`, `semantic_tree/tree_node.py`

`TreeBuilder.build()` converts a flat element list into a `SemanticTree` of `TreeNode` objects using a stack-based algorithm with three default nesting rules:

1. `AlwaysNestAsParentRule(TopSectionStartMarker)` - Part/Item sections parent everything
2. `AlwaysNestAsParentRule(TitleElement, exclude_children={TopSectionStartMarker})` - Titles parent non-title content
3. `NestSameTypeDependingOnLevelRule()` - Same-type elements with lower `.level` parent those with higher `.level`

`SemanticTree` provides:
- `__iter__()` - iterate root nodes
- `.nodes` - generator yielding all nodes (depth-first)
- `.render()` / `.print()` - ASCII tree visualization

`TreeNode` provides:
- `.semantic_element` - the wrapped element
- `.parent` / `.children` - tree navigation (parent setter auto-updates both sides)
- `.get_descendants()` - recursive depth-first traversal
- `.text` / `.get_source_code()` - pass-throughs to the semantic element

**Verdict for our goals:** This is the library's strongest feature and the foundation for G2. The rule system is composable. However, the tree lacks: section boundary information (start/end indices or byte offsets), serialization to a TOC data structure, and query/filter APIs.

---

### 1.5 Section Definitions

**File:** `semantic_elements/top_section_title_types.py`

`TopSectionInFiling` dataclass: `identifier`, `title`, `order`, `level`.
`FilingSections` dataclass: maps identifiers to sections.

10-Q: 12 sections (Part I Items 1-4, Part II Items 1-6, plus Part headings).
10-K: 27 sections (Part I-IV, Items 1-16 including 1c Cybersecurity).

`TopSectionManager` uses `match_part()` (regex for "Part [I-IV]") and `match_item()` (regex for "Item [N]") with a roman numeral map limited to `{"i": "1", "ii": "2", "iii": "3", "iv": "4"}`.

---

### 1.6 Table Features

**Detection:** `TableClassifier` + `TableCheck` (in `IndividualSemanticElementExtractor`)
**Metrics:** `get_approx_table_metrics()` returns `ApproxTableMetrics(rows, numbers)`
**Markdown:** `TableToMarkdown.convert()` - unmerges `colspan` cells, parses via `pd.read_html`, outputs markdown
**DataFrame:** `TableParser.parse_as_df()` - parses first table, drops NAs, merges `$`/`%` marker columns
**TOC detection:** `check_table_contains_text_page()` checks `<td>` text against "page"/"page no."/"page number"
**Summary:** `TableElement.get_summary()` returns row/number counts (has a bug - see flaws)

---

### 1.7 Text Style Analysis

**File:** `semantic_elements/highlighted_text_element.py`

`TextStyle` frozen dataclass tracks five boolean properties derived from inline CSS style percentages:
- `is_all_uppercase` - text-level check (>= 80% capitalized via `exceeds_capitalization_threshold()`)
- `bold_with_font_weight` - CSS `font-weight` >= 600 or "bold" (>= 80% of text length)
- `italic` - CSS `font-style: italic` (>= 80%)
- `centered` - CSS `text-align: center` (>= 80%)
- `underline` - CSS `text-decoration: underline` (>= 80%)

`TextStyle.__bool__()` returns `True` if any property is set.
`TextStyle.from_style_and_text()` is the factory that computes styles from metrics + text.

**Verdict for our goals:** Adequate for 2015+ filings which overwhelmingly use inline CSS. The 80% threshold and 600 bold weight are reasonable defaults but should be configurable.

---

### 1.8 Ancillary Features

**Rendering** (`semantic_tree/render_.py`): `render()` produces ASCII trees with ANSI colors. Supports `pretty`, `verbose` (shows levels), `char_display_limit`, and `ignored_types` parameters. Useful for debugging only.

**Processing Log** (`processing_engine/processing_log.py`): Append-only log on every element recording each classification decision. Invaluable for debugging why an element was classified a certain way.

**Composite Element Unwrapping** (`CompositeSemanticElement.unwrap_elements()`): Recursively flattens `CompositeSemanticElement` containers. The `include_containers` flag preserves the wrapper for document reconstruction.

**ParsingOptions** (`processing_engine/types.py`): Currently contains only `html_integrity_checks: bool = False`. Underutilized.

**Dashboard** (`dev_utils/dashboard_app/`): Streamlit-based visual debugger. Not production-relevant.

---

## Part 2: Function-by-Function Assessment

### Tier 1: Critical for Our Goals (use and enhance)

| Function / Class | File | Relevance | Status |
|-----------------|------|-----------|--------|
| `TreeBuilder.build()` | `tree_builder.py` | Produces the hierarchy that G2's TOC pill navigates. Every section, subsection, and content block nests here. | **Needs enhancement:** no section boundary data, no serializable TOC output, stack-popping bug (see M6). |
| `TopSectionManager._process_element()` (and its 10K/10Q subclasses) | `top_section_manager.py` | Identifies Part/Item boundaries - the top-level segments for G1's IDs and G2's TOC. | **Needs enhancement:** regex brittleness, no tolerance for formatting variants, dead code at EOF. |
| `TopSectionTitle` + `TopSectionStartMarker` | `top_section_title.py`, `top_section_start_marker.py` | Carry `.section_type.identifier` (e.g., "part2item7") - the natural segment address root for G1. | **Usable as-is.** `.section_type.identifier` is already a decent segment address prefix. |
| `TitleClassifier._process_element()` | `title_classifier.py` | Assigns hierarchy levels to sub-section headings. These levels drive G2's TOC depth. | **Needs fix:** order-of-first-occurrence level assignment is fragile (see M1). |
| `TitleElement` | `title_element.py` | Carries `.level` for nesting depth. G2 needs this to render the mini-TOC list correctly. | **Usable as-is** once TitleClassifier is fixed. |
| `TableClassifier._process_element()` | `table_classifier.py` | Identifies all tables - the starting point for G3's complete inventory. | **Needs enhancement:** no table type classification, no context about surrounding prose. |
| `IndividualSemanticElementExtractor._create_composite_element()` | `individual_semantic_element_extractor.py` | Splits mixed containers (prose + table in one tag) into separate elements. Critical for G4's prose-table relationship detection. | **Good as-is.** `TableCheck.contains_single_element()` correctly handles multi-table and text-outside-table cases. |
| `AbstractSemanticElement.text` / `.get_source_code()` | `abstract_semantic_element.py` | Primary text extraction for G1 and G5. | **Usable as-is.** Need to add normalized text output for G5 diffing. |
| `SemanticTree.nodes` | `semantic_tree.py` | Depth-first iterator over all nodes - needed to walk the tree for G2 TOC generation and G1 segment ID assignment. | **Usable as-is.** |
| `CompositeSemanticElement.unwrap_elements()` | `composite_semantic_element.py` | Flattens nested containers for G1's flat text extraction while `include_containers=True` preserves structure for G4. | **Usable as-is.** |

### Tier 2: Important Supporting Features (use with minor modifications)

| Function / Class | File | Relevance | Status |
|-----------------|------|-----------|--------|
| `HighlightedTextClassifier._process_element()` | `highlighted_text_classifier.py` | Intermediate step feeding `TitleClassifier`. Quality of style detection directly impacts G2's TOC accuracy. | **Good for 2015+ filings.** Inline CSS detection works. |
| `TextStyle.from_style_and_text()` | `highlighted_text_element.py` | Produces the style fingerprint used for title level assignment. | **Good.** Consider making thresholds configurable. |
| `PageHeaderClassifier._process_element()` | `page_header_classifier.py` | Removes repeated page headers (company name, section name) that would pollute G1's text extraction and G5's diffs. | **Good.** Statistical approach (5+ occurrences of identical short text + style) is robust. |
| `PageNumberClassifier._process_element()` | `page_number_classifier.py` | Removes page numbers that would pollute G1/G5. | **Good.** Same statistical approach. |
| `TextElementMerger._process_elements()` | `text_element_merger.py` | Merges XBRL-split text fragments into coherent paragraphs. Without this, G1 produces fragmented text and G5's diffs are noisy. | **Important.** Works correctly for the common XBRL split case. |
| `SupplementaryTextClassifier._process_element()` | `supplementary_text_classifier.py` | Partial implementation of G4 - identifies parenthetical unit qualifiers and "accompanying notes" references. | **Needs enhancement:** too narrow for general stub detection. |
| `EmptyElementClassifier` | `empty_element_classifier.py` | Filters whitespace-only elements from output. Keeps G1 clean. | **Fine as-is.** |
| `IntroductorySectionElementClassifier._process_element()` | `introductory_section_classifier.py` | Removes cover pages and disclaimers before Part 1. | **Fine as-is.** |
| `HtmlTag` (entire class) | `html_tag.py` | Caching wrapper providing all low-level operations. Performance-critical for large 10-Ks. | **Good.** Would benefit from exposing byte offset / character offset for G2 position tracking. |
| `render()` | `render_.py` | Debugging visualization during development. | **Fine as-is** for development use. |

### Tier 3: Usable but Low Priority

| Function / Class | File | Relevance | Status |
|-----------------|------|-----------|--------|
| `ImageClassifier` | `image_classifier.py` | Tags images for filtering. Not central to any goal. | Fine as-is. |
| `TableElement.table_to_markdown()` / `TableToMarkdown.convert()` | `table_element.py`, `table_to_markdown.py` | Useful for G5 text-diffing of tables. Handles `colspan` unmerging. | Usable. Better than `parse_as_df()` for our purposes. |
| `TableOfContentsClassifier._process_element()` | `table_of_contents_classifier.py` | Detects TOC tables, which G2 could use as a fallback for section enumeration. | Too simplistic to rely on (see m8). |
| Processing log system | `processing_log.py` | Development/debugging aid. | Fine as-is. |
| `AbstractSemanticElement.to_dict()` | `abstract_semantic_element.py` | Serialization helper. Building block for G5 output. | Usable. |
| Nesting rules (`AlwaysNestAsParentRule`, `AlwaysNestAsChildRule`, `NestSameTypeDependingOnLevelRule`) | `nesting_rules.py` | Composable rules that let us customize tree building for G2. | Good design. We can add custom rules for our TOC needs. |

### Tier 4: Low Value / Needs Replacement

| Function / Class | File | Why Low Value |
|-----------------|------|---------------|
| `TableParser.parse_as_df()` | `table_parser.py` | Parses only first table, naive headers, `$`/`%` merging is fragile, loses structure. Not useful for G3 or G5. |
| `get_approx_table_metrics()` | `approx_table_metrics.py` | Only provides rough row/number counts. Not granular enough for G3's table classification. |
| `check_table_contains_text_page()` | `table_check_data_cell.py` | Checks only exact matches of "page"/"page no."/"page number" in `<td>` cells. Misses common variants, false-positives possible. |
| `ParsingOptions` | `types.py` | Contains only `html_integrity_checks: bool`. Severely underutilized. |
| Dashboard app | `dev_utils/` | Development tool, not production. |

---

## Part 3: Flaws

### Major Flaws

#### M1. Title Hierarchy Levels Are Assigned by Order of First Occurrence

`TitleClassifier` maintains `_unique_styles_by_order`, a tuple of `TextStyle` objects. The first unique style encountered in the document gets level 0, the second gets level 1, etc.

This assumes the document presents heading styles top-down. If a styled disclaimer or note appears before the first real heading, all levels shift. For 2015+ filings, the `SupplementaryTextClassifier` catches some of these cases (parenthetical text, italic notes), but edge cases remain: a bold legal notice before Part I, a centered company name that wasn't caught by `PageHeaderClassifier`, or a styled exhibit reference.

**Impact:** G2's TOC mini-list will show incorrect nesting. G1's segment hierarchy will be unreliable for sub-section granularity.

**Fix:** Replace insertion-order level assignment with a style-scoring approach. Score each `TextStyle` by its visual weight (bold > centered > uppercase > underline > italic), rank all unique styles, assign levels by rank. This requires changing `TitleClassifier` from single-pass to two-pass (`_NUM_ITERATIONS = 2`): first pass collects all styles, second pass assigns levels by score rank.

---

#### M2. No Stable Element Identifier System

Elements have no `id`, `index`, or content-hash-based identifier. `AbstractSemanticElement` is identified only by Python object identity. `to_dict()` produces an `html_hash` via xxhash but it's on `HtmlTag`, not propagated as a stable element ID.

**Impact:** G1 cannot assign segment header IDs. G2 cannot produce TOC entries with stable anchor links. G5 cannot align elements across filing periods for diffing.

**Fix:** Add a post-tree-building step that assigns hierarchical IDs. For `TopSectionTitle`, use `.section_type.identifier` (already exists: "part2item7"). For `TitleElement`, derive from parent section + normalized title text. For content elements, use parent ID + sequential index.

---

#### M3. Table Detection Has No Type Classification

`TableClassifier` produces a single `TableElement` type for all tables. There is no distinction between financial statement tables, footnote tables, layout/formatting tables, TOC tables, exhibit lists, or schedule tables.

**Impact:** G3 requires a complete inventory classified by purpose. G4's prose-stub logic depends on knowing whether a table is a data table or a layout artifact.

**Fix:** Add a `TableTypeClassifier` step after `TableClassifier` that assigns a `table_type` attribute. Heuristics: financial statement tables have `$` markers, numeric columns, proximity to financial statement section titles; footnote tables are smaller and inside footnote sections; layout tables have single columns or mostly text; TOC tables match section title patterns.

---

#### M4. No Prose-Table Context Relationship Tracking

The pipeline classifies elements individually. There is no step that examines the relationship between a `TextElement` and an adjacent `TableElement`. `SupplementaryTextClassifier` catches a few specific patterns (parenthetical text, "accompanying notes") but does not detect generic stub references like "the following table presents..." or "refer to the table below."

**Impact:** G4 cannot distinguish substantive prose from stub references without manual post-processing.

**Fix:** Add a `TableContextClassifier` step that runs after `TextElementMerger`. For each `TableElement`, examine the preceding and following `TextElement`. Classify the relationship as: standalone (no relevant surrounding text), substantive-context (preceding prose adds value), stub-reference (preceding prose only points to the table), or continuation (table spans multiple elements).

---

#### M5. Tree Has No Section Boundary or Position Data

`TreeNode` carries only the `semantic_element` reference, `parent`, and `children`. There is no information about where a section starts and ends in the document (element index range, character offset, byte offset, or percentage through the document).

**Impact:** G2's Intersection Observer needs to map scroll position to the current section. Without positional data from the parser, the frontend must re-walk the DOM to compute section boundaries, duplicating work and risking desynchronization with the parse tree.

**Fix:** Add `start_index`, `end_index`, and optionally `char_offset` to `TreeNode` during tree construction. Compute from element positions in the flat list. Expose a `tree.get_section_map()` method returning a list of `(section_id, start_offset, end_offset)` tuples.

---

#### M6. `_find_parent_node` Destructively Pops the Stack

In `TreeBuilder._find_parent_node()`, the `while stack` loop pops elements that don't match as parents. This is destructive: if element N can't find a parent, it pops context that element N+1 might have needed.

**Impact:** After a standalone table or image that doesn't nest under any title, all accumulated title context is lost. Subsequent text elements become root nodes instead of nesting under their section. This produces a broken tree for G2 and incorrect segment addresses for G1.

**Fix:** Use a non-destructive search (iterate backward without popping), only trimming the stack after finding a match or determining root status.

---

### Minor Flaws

#### m1. Bug: Missing f-string in `TableElement.get_summary()`

`table_element.py:23` reads `return "Table with {len(self.text)} characters."` - the `f` prefix is missing. Returns a literal string instead of the actual character count.

---

#### m2. Dead Code in `TopSectionManager`

`top_section_manager.py:347-379` contains two module-level docstrings with algorithm descriptions and a "ChatGPT improved version." These are unreachable dead code.

---

#### m3. Hard-Coded Thresholds Not Configurable

| Threshold | Location | Value |
|-----------|----------|-------|
| Style percentage | `TextStyle.PERCENTAGE_THRESHOLD` | 80 |
| Bold font-weight | `TextStyle.BOLD_THRESHOLD` | 600 |
| Page number text length | `PageNumberCandidate.TEXT_LENGTH_THRESHOLD` | 100 |
| Page number min occurrences | `PageNumberCandidate.OCCURRENCE_THRESHOLD` | 5 |
| Page header min occurrences | `PageHeaderCandidate.OCCURRENCE_THRESHOLD` | 5 |
| Table min rows | `TableClassifier._row_count_threshold` | 1 |

None are exposed via `ParsingOptions` or constructor parameters. `ParsingOptions` itself has only a single `html_integrity_checks` field.

---

#### m4. `TopSectionManager.match_part()` Limited to Parts I-IV

The roman numeral map is `{"i": "1", "ii": "2", "iii": "3", "iv": "4"}`. Sufficient for 10-K/10-Q but will need extension for other filing types. Low priority given our current scope.

---

#### m5. Page Header/Number Detection Requires 5+ Occurrences

`OCCURRENCE_THRESHOLD = 5` means very short filings (under ~5 pages) won't have page noise removed. This is fine for typical 10-Ks/10-Qs but may affect short amendment filings.

---

#### m6. `render_()` Has Quadratic Prefix Growth

`render_.py:98` doubles the prefix string for root-level children. Not a correctness issue (root prefix is empty) but causes O(n^2) string growth in deeply nested trees.

---

#### m7. Single-Pass Pipeline Cannot Reclassify Elements

Once an element is typed (e.g., `TextElement`), later steps can only reclassify it if they explicitly include that type in `types_to_process`. A `HighlightedTextElement` near a table header that looks like a section title will be promoted to `TitleElement` by `TitleClassifier` even if it's clearly a table caption.

---

#### m8. `TableOfContentsClassifier` Heuristic is Too Weak

`check_table_contains_text_page()` only matches exact cell text in `{"page", "page no.", "page number"}`. Misses "Pg.", "PAGE", cells with additional whitespace, and tables where the page column has a different label. Also false-positives on any data table mentioning "page" in a cell.

---

#### m9. `CompositeSemanticElement` Loses Ordering Context

When `unwrap_elements()` flattens composites, the original container-level context (what XBRL tag wrapped these elements, what the parent `<div>` attributes were) is discarded unless `include_containers=True`. For G4 (prose-table relationship), we need to know that a text and table were siblings inside the same container.

---

## Part 4: Improvement Recommendations

### Priority 0 - Do First

#### I1. Stable Hierarchical Element IDs

Add a post-tree-building step that assigns a deterministic `segment_id` to every element. Format: `{section_identifier}:{title_slug}:{element_type}_{index}`.

Example: `part2item7:revenue_recognition:text_3`, `part1item1:financial_statements:table_1`.

For `TopSectionTitle`, use the existing `.section_type.identifier`. For `TitleElement`, slugify the title text. For content elements, use parent's ID + type + index.

Enables: G1 (segment-addressed text), G2 (TOC anchor IDs), G5 (cross-period element alignment).

---

#### I2. Fix Title Level Assignment in `TitleClassifier`

Convert to two-pass (`_NUM_ITERATIONS = 2`). Pass 1: collect all unique `TextStyle` instances from `HighlightedTextElement` across the document. Score each style by visual weight. Pass 2: assign levels based on score rank.

Scoring suggestion: `(bold * 3) + (uppercase * 2) + (centered * 2) + (underline * 1) - (italic * 1)`. Higher score = higher-level heading = lower level number.

Enables: G2 (correct TOC hierarchy), G1 (correct segment nesting).

---

#### I3. Fix f-string Bug in `TableElement.get_summary()`

Add the `f` prefix to the fallback return string. Trivial fix.

---

### Priority 1 - Do Soon

#### I4. Section Boundary Data on Tree Nodes

During `TreeBuilder.build()`, track `start_index` and `end_index` (position in the flat element list) on each `TreeNode`. After building, compute cumulative character offsets for each node.

Expose `SemanticTree.get_section_boundaries()` returning a list of `(segment_id, start_element_index, end_element_index, char_start, char_end)`.

Enables: G2 (Intersection Observer can map scroll position to active section, the pill UI can show "Note 5 - 42%" progress within a section).

---

#### I5. Table Type Classification Step

Add `TableTypeClassifier` as a new step after `TableOfContentsClassifier`. Assign `table_type` to each `TableElement`:
- `FINANCIAL_STATEMENT` - `$` markers or numeric-heavy, near financial statement section
- `FOOTNOTE` - smaller table inside a footnote section
- `LAYOUT` - single-column or predominantly text cells
- `TOC` - already classified by `TableOfContentsClassifier`
- `SCHEDULE` - supporting schedule format
- `OTHER` - default

Enables: G3 (complete classified table inventory).

---

#### I6. Table-Prose Context Classifier

Add `TableContextClassifier` step after `TextElementMerger`. For each `TableElement`, examine the immediately preceding `TextElement` (or `SupplementaryText`):

- **Stub patterns:** text length < 120 chars AND matches phrases like "following table", "table below", "set forth below", "as follows", "presented below", "summarized below"
- **Substantive context:** preceding text > 120 chars, or contains analytical/explanatory content beyond a pointer
- **Standalone:** no preceding text element, or preceding element is another table/title

Store the classification and optionally link the related prose element to the table.

Enables: G4 (discard stubs, keep context).

---

#### I7. Expand `SupplementaryTextClassifier` Rules

Broaden the current narrow patterns to catch more stub prose. Add detection for:
- "Refer to [Note/table/section]..." patterns
- "The following [table/chart/graph]..." patterns
- Single-sentence paragraphs that end with a colon (often introduce a table)
- Parenthetical references like "(see table X)"

Keep the existing parenthetical and "accompanying notes" patterns. Mark the new detections differently so G4 can distinguish unit qualifiers from table-reference stubs.

Enables: G4.

---

### Priority 2 - Important

#### I8. TOC Data Structure Generation

Add `SemanticTree.to_toc()` method that walks the tree and produces a serializable TOC.

Each entry should contain: `segment_id`, `title` (text content), `level` (hierarchy depth), `element_type` (TopSectionTitle, TitleElement), `parent_id`, `child_count`, `has_tables` (boolean), `content_length` (total text characters in section). This structure directly feeds G2's expandable mini-TOC list.

Enables: G2 (the pill UI's hover-expand TOC list needs exactly this data).

---

#### I9. Diff-Ready Serialization

Add export methods to `SemanticTree`:
- `to_diff_text()` - one line per element: `{segment_id}\t{element_type}\t{normalized_text}`
- Normalize text: collapse whitespace, strip page artifacts, normalize quotes/dashes

For tables, `TableElement.table_to_markdown()` already produces diff-friendly output. Pair it with the segment ID.

Enables: G5 (text-diffing and number-diffing across periods).

---

#### I10. Make Thresholds Configurable

Expand `ParsingOptions` (or create a new `ParsingConfig`) to expose all hardcoded thresholds. Pass through the pipeline so each step reads from config rather than class constants.

Enables: Tuning for different filer styles without modifying library internals.

---

### Priority 3 - Nice to Have

#### I11. Non-Destructive Stack in `TreeBuilder._find_parent_node()`

Replace the destructive `stack.pop()` loop with a backward index scan. Only trim the stack after finding a match or determining root status.

Enables: More robust tree building, fewer orphaned elements.

---

#### I12. Clean Up Dead Code

Remove the module-level algorithm description docstrings at the end of `top_section_manager.py`.

---

#### I13. Improve `TableOfContentsClassifier`

Expand `is_page_data_cell()` to handle case-insensitive matching, "Pg.", "PAGE", and cells with surrounding whitespace. Add a second heuristic: if a table has 5+ rows where one column contains section-title-like text and another column contains numbers, it's likely a TOC.

Enables: G2 (filing's own TOC can serve as ground truth for section enumeration).

---

### Improvement Priority Matrix

| Priority | ID | Improvement | Effort | Primary Goal |
|----------|----|------------|--------|-------------|
| **P0** | I1 | Stable hierarchical element IDs | Medium | G1, G2, G5 |
| **P0** | I2 | Fix title level assignment scoring | Medium | G1, G2 |
| **P0** | I3 | Fix f-string bug | Trivial | Bug fix |
| **P1** | I4 | Section boundary data on tree nodes | Medium | G2 |
| **P1** | I5 | Table type classification | Medium | G3 |
| **P1** | I6 | Table-prose context classifier | Medium | G4 |
| **P1** | I7 | Expand supplementary text rules | Low | G4 |
| **P2** | I8 | TOC data structure generation | Medium | G2 |
| **P2** | I9 | Diff-ready serialization | Medium | G5 |
| **P2** | I10 | Configurable thresholds | Low | All |
| **P3** | I11 | Non-destructive tree builder stack | Low | G1, G2 |
| **P3** | I12 | Clean up dead code | Trivial | Maintenance |
| **P3** | I13 | Improve TOC classifier heuristic | Low | G2 |

---

## Appendix: File Map

| Component | File |
|-----------|------|
| Public API | `sec_parser/__init__.py` |
| Parser entry point | `sec_parser/processing_engine/core.py` |
| HTML tag wrapper | `sec_parser/processing_engine/html_tag.py` |
| HTML tag parser | `sec_parser/processing_engine/html_tag_parser.py` |
| Parsing options | `sec_parser/processing_engine/types.py` |
| Processing step base | `sec_parser/processing_steps/abstract_classes/abstract_elementwise_processing_step.py` |
| Batch step base | `sec_parser/processing_steps/abstract_classes/abstract_element_batch_processing_step.py` |
| Element extractor | `sec_parser/processing_steps/individual_semantic_element_extractor/individual_semantic_element_extractor.py` |
| Table check | `sec_parser/processing_steps/individual_semantic_element_extractor/single_element_checks/table_check.py` |
| XBRL check | `sec_parser/processing_steps/individual_semantic_element_extractor/single_element_checks/xbrl_tag_check.py` |
| Image classifier | `sec_parser/processing_steps/image_classifier.py` |
| Empty classifier | `sec_parser/processing_steps/empty_element_classifier.py` |
| Table classifier | `sec_parser/processing_steps/table_classifier.py` |
| TOC classifier | `sec_parser/processing_steps/table_of_contents_classifier.py` |
| Section manager | `sec_parser/processing_steps/top_section_manager.py` |
| Intro classifier | `sec_parser/processing_steps/introductory_section_classifier.py` |
| Text classifier | `sec_parser/processing_steps/text_classifier.py` |
| Highlighted text | `sec_parser/processing_steps/highlighted_text_classifier.py` |
| Supplementary text | `sec_parser/processing_steps/supplementary_text_classifier.py` |
| Page header | `sec_parser/processing_steps/page_header_classifier.py` |
| Page number | `sec_parser/processing_steps/page_number_classifier.py` |
| Title classifier | `sec_parser/processing_steps/title_classifier.py` |
| Text merger | `sec_parser/processing_steps/text_element_merger.py` |
| Base element | `sec_parser/semantic_elements/abstract_semantic_element.py` |
| Element types | `sec_parser/semantic_elements/semantic_elements.py` |
| Highlighted element | `sec_parser/semantic_elements/highlighted_text_element.py` |
| Title element | `sec_parser/semantic_elements/title_element.py` |
| Top section title | `sec_parser/semantic_elements/top_section_title.py` |
| Top section marker | `sec_parser/semantic_elements/top_section_start_marker.py` |
| Section definitions | `sec_parser/semantic_elements/top_section_title_types.py` |
| Table element | `sec_parser/semantic_elements/table_element/table_element.py` |
| Table parser | `sec_parser/semantic_elements/table_element/table_parser.py` |
| Table to markdown | `sec_parser/utils/bs4_/table_to_markdown.py` |
| TOC check | `sec_parser/utils/bs4_/table_check_data_cell.py` |
| Table metrics | `sec_parser/utils/bs4_/approx_table_metrics.py` |
| Composite element | `sec_parser/semantic_elements/composite_semantic_element.py` |
| Tree builder | `sec_parser/semantic_tree/tree_builder.py` |
| Nesting rules | `sec_parser/semantic_tree/nesting_rules.py` |
| Semantic tree | `sec_parser/semantic_tree/semantic_tree.py` |
| Tree node | `sec_parser/semantic_tree/tree_node.py` |
| Render | `sec_parser/semantic_tree/render_.py` |
