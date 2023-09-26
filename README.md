<p align="center">&nbsp;</p>
<p align="center">
  <img src="docs/title.png" alt="sec-parser logo" height="40"/>
</p>
<p align="center">
  <a href="https://github.com/alphanome-ai/sec-parser/actions/workflows/check.yml"><img alt="GitHub Workflow Status (with event)" src="https://img.shields.io/github/actions/workflow/status/alphanome-ai/sec-parser/check.yml"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT" /></a>
  <a href="https://codecov.io/gh/alphanome-ai/sec-parser"><img src="https://codecov.io/gh/alphanome-ai/sec-parser/graph/badge.svg?token=KJLA96CBCN" alt="codecov" /></a>
  <a href="https://badge.fury.io/py/sec-parser"><img src="https://badge.fury.io/py/sec-parser.svg" alt="PyPI version" /></a>
  <br>
  <a href="https://pepy.tech/project/sec-parser"><img src="https://pepy.tech/badge/sec-parser/month" alt="Downloads" /></a>
  <a href="http://hits.dwyl.com/alphanome-ai/sec-parser"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fhits.dwyl.com%2Falphanome-ai%2Fsec-parser.json%3Fshow%3Dunique" alt="HitCount" /></a>
  <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
  <a href="https://project-types.github.io/#federation"><img src="https://img.shields.io/badge/project%20type-federation-brightgreen" alt="Federation Badge"/></a>
</p>
<div align="center">
  <b>
  <a href="https://sec-parser-output-visualizer.app.alphanome.dev">Demo</a> |
  <a href="https://github.com/alphanome-ai/sec-parser/discussions">Discussions</a> |
  <a href="https://github.com/alphanome-ai/sec-parser/issues">Issues</a>
  </b>
</div>

## Overview

The `sec-parser` project simplifies the process of extracting meaningful information from SEC EDGAR HTML documents. It organizes the document's source code into a list or tree of elements that correspond to the visual structure of the document. This includes distinct elements for section titles, paragraphs, and tables, making the data easier to analyze and understand. 

This tool is especially beneficial for Artificial Intelligence (AI) and Large Language Models (LLM) applications. It significantly improves the efficiency of data extraction and analysis in these fields.

[**Explore the Demo!**](https://sec-parser-output-visualizer.app.alphanome.dev/)

## Installation

You can install `sec-parser` using pip:

```bash
pip install sec-parser
```

## Usage

```python
import sec_parser as sp

tree = sp.parse_latest("10-K", ticker="AAPL")

# Show the general structure of the tree
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

# License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
