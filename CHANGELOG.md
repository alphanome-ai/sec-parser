## 0.9.0 (2023-09-27)

### Feat

- **ci**: use GitHub run_number for post-release versioning

### Fix

- **packaging**: use post-release versions for PyPI compatibility

## 0.8.0 (2023-09-26)

### Feat

- **debug_tools**: set more user friendly defaults
- **semantic_tree**: implement getting textual representation of a tree

## 0.7.0 (2023-09-25)

### Feat

- **debug_tools**: Add Tree View
- **build**: add speed test that finished the check fast
- **TitlePlugin**: implement TitleElement detection
- **title_plugin**: add an ordered set to hold found title styles
- parse all-bolded text as HighlightedElement
- add bulletpoint parsing
- **plugins**: implement rudimentary versions of all plugins
- add new types of plugins (not yet the implementations of them)
- simplify user interface, improve parsing
- **debug_tools**: add pagination and columnization to visualizer
- **debug_tools**: add support to viewing multiple reports at the same time
- **test/speed**: update readabilty of speed test output
- **tests/speed**: improve speed benchmark output
- implement Text parser plugin
- **parsing_engine**: refactor class hierarchy and naming for extensibility and clarity
- **debug_tools**: add cached downloaded documents for default values to the repository
- **RootSectionPlugin**: implement parsing of RootSectionElement
- **tests/speed**: implement speed benchmark for parsing
- **debug_tools**: add page to view nested semantic tree
- **debug_tools**: add pretty formatting for TitleElement elements
- **debug_tools**: add auto-reloading upon source code changes
- **debug_tools**: display parsed semantic elements with view options
- **debug_tools**: add navigation to show parsing steps
- **debug_tools**: remove <ix:...> tags from displayed html
- **debug_tools**: create sec-parser output visualizer and implement document downloading
- **SecParser**: add ContentlessElement and fix small typing nits

### Fix

- **ci-cd**: PEP 604 support
- **ci-cd**: 'pytest not found'
- **ci-cd**: install Task
- **ci-cd**: poetry install
- **TitlePlugin**: not finding elements
- **e2e**: handle not found document condition
- **title_plugin**: replace deprecated 'text' with 'string'
- **debug_tools**: filter element type counts
- **debug_tools**: trees for different documents being built from one documents elements
- **debug_tools**: use appropriate caching decorator (one that does not allow mutation)
- **SemanticTree**: not nesting RootSectionElement as parents
- **secapio_data_retriever**: error message
- **data_sources**: export exceptions
- **debug_tools**: setting api key
- **debug_tools**: fix bugs when setting the api key
- **visualizer**: api key is now saved correctly
- **debug_tools**: add pre-downloaded documents
- **debug_tools**: add pre-downloaded documents
- **debug_tools**: improve message
- **ddebug_tools**: fix cache path
- **debug_tools**: fix and refactor the SecParser output visualizer
- **debug_tools**: regenerate .txt files if they're missing
- **debug_tools**: remove warning about streamlit caching
- **debug_tools**: avoid commas in filenames

### Refactor

- **ElementWiseParsingPlugin**: extract to a separate file
- **tree_builder**: fix readability of nesting rules
- **HighlightedElement**: move to TitlePlugin file as it is only an intermediate object and not used elsewhere
- **debug_tools**: add tiny nits
- **abstract_nesting_rule**: move to a separate file
- **sec_parser**: move less relevant code to 'html_parsers'
- refactor sec_parser to improve readability and maintainability

## 0.6.1 (2023-09-11)

### Refactor

- make the library well-structured
- improve config values handling

## 0.6.0 (2023-09-11)

### Feat

- implement passthrough parser and refactor codebase

### Refactor

- make internal packages private

## 0.5.0 (2023-09-10)

## 0.4.0 (2023-09-10)

### Feat

- **data_retrievers**: add sec-api.io 10-Q document downloader

## 0.3.0 (2023-09-09)

### Feat

- **utils**: add TreeNode class for tree data structure representation

### Fix

- **pre-commit**: fix yaml indentation

## 0.2.1 (2023-09-09)

### Fix

- **Taskfile.yml**: fix mypy folder arg

## 0.2.0 (2023-09-09)

### Feat

- add initial project files
