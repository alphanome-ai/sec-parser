<p align="center">&nbsp;</p>
<p align="center">
  <h1 align="center"><b>sec-parser</b></h1>
</p>
<p align="left">
  <!-- Using &nbsp; for alignment due to GitHub README limitations -->
  <b>Essentials ➔&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</b>
  <a href='https://sec-parser.readthedocs.io/en/latest/?badge=latest'><img src='https://readthedocs.org/projects/sec-parser/badge/?version=latest' alt='Documentation Status' /></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/alphanome-ai/sec-parser.svg" alt="Licence"></a>
  <a href="https://project-types.github.io/#federation"><img src="https://img.shields.io/badge/project%20type-federation-brightgreen" alt="Project Type: Federation"></a>
  <!-- NOTE: After changing stability level here, also change it in pyproject.toml -->
  <a href="https://github.com/mkenney/software-guides/blob/master/STABILITY-BADGES.md#beta"><img src="https://img.shields.io/badge/stability-beta-33bbff.svg" alt="Beta"></a>
  <br>
  <b>Health ➔&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</b>
  <a href="https://github.com/alphanome-ai/sec-parser/actions/workflows/ci.yml"><img alt="GitHub Workflow Status: ci.yml" src="https://img.shields.io/github/actions/workflow/status/alphanome-ai/sec-parser/ci.yml?label=ci"></a>
  <a href="https://github.com/alphanome-ai/sec-parser/actions/workflows/cd.yml"><img alt="GitHub Workflow Status: cd.yml" src="https://img.shields.io/github/actions/workflow/status/alphanome-ai/sec-parser/cd.yml?label=cd"></a>
  <a href="https://github.com/alphanome-ai/sec-parser/commits/main"><img alt="Last Commit" src="https://img.shields.io/github/last-commit/alphanome-ai/sec-parser"></a>  
  <br>
  <b>Quality ➔&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</b>
  <a href="https://codecov.io/gh/alphanome-ai/sec-parser"><img src="https://codecov.io/gh/alphanome-ai/sec-parser/graph/badge.svg?token=KJLA96CBCN" alt="codecov" /></a>
  <a href="https://mypy-lang.org/"><img src="https://img.shields.io/badge/type%20checked-mypy-blue.svg"></a>
  <a href="https://github.com/psf/black"><img alt="Code Style: Black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <br>
  <b>Distribution ➔&nbsp;&nbsp;&nbsp;</b>
  <a href="https://badge.fury.io/py/sec-parser"><img src="https://badge.fury.io/py/sec-parser.svg" alt="PyPI version" /></a>
  <a href="https://pypi.org/project/sec-parser/"><img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/sec-parser"></a>
  <a href="https://pypistats.org/packages/sec-parser"><img src="https://img.shields.io/pypi/dm/sec-parser.svg" alt="PyPI downloads"></a>
  <br>
  <b>Community ➔&nbsp;&nbsp;&nbsp;&nbsp;</b>
  <a href="http://hits.dwyl.com/alphanome-ai/sec-parser"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fhits.dwyl.com%2Falphanome-ai%2Fsec-parser.json%3Fshow%3Dunique" alt="HitCount" /></a>
  <a href="https://twitter.com/alphanomeai"><img alt="X (formerly Twitter) Follow" src="https://img.shields.io/twitter/follow/alphanomeai"></a>
  <a href="https://github.com/alphanome-ai/sec-parser"><img src="https://img.shields.io/github/stars/alphanome-ai/sec-parser.svg?style=social&label=Star us on GitHub!" alt="GitHub stars"></a>


</p>

<div align="left">
  Parse SEC EDGAR HTML documents into a tree of elements that correspond to the visual structure of the document.
</div>
<br>
<div align="center">
  <b>
  <a href="https://parser.app.alphanome.dev">See Demo</a> |
  <a href="https://sec-parser.rtfd.io">Read Docs</a> |
  <a href="https://github.com/alphanome-ai/sec-parser/discussions">Ask Questions</a> |
  <a href="https://github.com/alphanome-ai/sec-parser/issues">Report Bugs</a>
  </b>
</div>
<be>

# Overview

The `sec-parser` project simplifies extracting meaningful information from SEC EDGAR HTML documents by organizing them into semantic elements and a tree structure. Semantic elements might include section titles, paragraphs, and tables, each classified for easier data manipulation. This forms a semantic tree that corresponds to the visual and informational structure of the document.

This tool is especially beneficial for Artificial Intelligence (AI) and Large Language Models (LLM) applications by streamlining data pre-processing and feature extraction.

- Explore the [**Demo**](https://parser.app.alphanome.dev/)
- Read the [**Documentation**](https://sec-parser.rtfd.io)
- Ask questions in [**Discussions**](https://github.com/alphanome-ai/sec-parser/discussions)
- Report bugs in [**Issues**](https://github.com/alphanome-ai/sec-parser/issues)

# Installation

Open a terminal and run the following command to install `sec-parser`:

```bash
pip install sec-parser
```

# Usage

```python
import sec_parser as sp

# Fetch and parse the latest Apple 10-Q report
tree = sp.parse_latest("10-Q", ticker="AAPL")

# Display the tree structure of the parsed document
print(tree.render())
```
Console output:
```
RootSectionElement: PART I — FINANCIAL INFORMATION
├── TitleElement: Item 1. Financial Statements
│   ├── TitleElement: CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (U...
│   │   ├── TextElement: (In millions, except number of shares which are re...
│   │   ├── TableElement: ...
│   ...
```

For more examples and advanced usage, you can continue learning how to use sec-parser by referring to the [**Quickstart User Guide**](https://sec-parser.readthedocs.io/en/latest/notebooks/quickstart_user_guide.html).

# Contributing

Contributing to `sec-parser` is a rewarding way to improve this open-source project. Whether you are a user interested in expanding your knowledge or a developer who wants to dive deeper into the codebase, we have comprehensive guides to get you started.

- **User Guide**: If you are new to `sec-parser` and would like to get started, please refer to the [**Quickstart User Guide**](https://sec-parser.readthedocs.io/en/latest/notebooks/quickstart_user_guide.html).
  
- **Developer Guide**: For those interested in contributing to `sec-parser`, the [**Comprehensive Developer Guide**](https://sec-parser.readthedocs.io/en/latest/notebooks/comprehensive_developer_guide.html) provides an in-depth walkthrough of the codebase and offers examples to help you contribute effectively.

Both guides are interactive and allow you to engage with the code and concepts as you learn. You can run and modify all the code examples for yourself by cloning the repository and running the respective notebooks in a Jupyter environment.

Alternatively, you can run the notebooks directly in your browser using Google Colab.

> **Note**
Before contributing, we highly recommend familiarizing yourself with these guides. They will help you understand the structure and style of our codebase, enabling you to make effective contributions.

# Best Practices

### Importing modules

1. Standard: `import sec_parser as sp`
1. Package-Level: `from sec_parser import SomeClass`
1. Submodule: `from sec_parser import semantic_tree`
1. Submodule-Level: `from sec_parser.semantic_tree import SomeClass`

> **Note**
The root-level package `sec_parser` contains only the most common symbols. For more specialized functionalities, you should use submodule or submodule-level imports.

> **Warning**
To allow us to maintain backward compatibility with your code during internal structure refactoring for `sec-parser`, avoid deep or chained imports such as `sec_parser.semantic_tree.internal_utils import SomeInternalClass`.

# License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
