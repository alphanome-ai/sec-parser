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
  <a href="https://github.com/orgs/alphanome-ai/discussions">Join Discussions</a> |
  <a href="https://github.com/alphanome-ai/sec-parser/issues">Report Bugs</a>
  </b>
</div>
<br>

# Overview

The `sec-parser` project simplifies extracting meaningful information from SEC EDGAR HTML documents by organizing them into semantic elements and a tree structure. Semantic elements might include section titles, paragraphs, and tables, each classified for easier data manipulation. This forms a semantic tree that corresponds to the visual and informational structure of the document.

This tool is especially beneficial for Artificial Intelligence (AI), Machine Learning (ML), and Large Language Models (LLM) applications by streamlining data pre-processing and feature extraction.

- Explore the [**Demo**](https://parser.app.alphanome.dev/)
- Read the [**Documentation**](https://sec-parser.rtfd.io)
- Join the [**Discussions**](https://github.com/orgs/alphanome-ai/discussions) to get help, propose ideas, or chat with the community
- Report bugs in [**Issues**](https://github.com/alphanome-ai/sec-parser/issues)
- Stay updated and contribute to our project's direction in [**Announcements**](https://github.com/orgs/alphanome-ai/discussions/categories/announcements) and [**Roadmap**](https://github.com/orgs/alphanome-ai/discussions/categories/roadmap-future-plans)

# Getting Started

This guide will walk you through the process of installing the `sec-parser` package and using it to extract the "Segment Operating Performance" section as a semantic tree from the latest Apple 10-Q filing.

## Installation

First, install the `sec-parser` package using pip:

```bash
pip install sec-parser
```

In order to run the example code in this README, you'll also need the `sec_downloader` package:

```bash
pip install sec-downloader
```

## Usage

Once you've installed the necessary packages, you can start by downloading the filing from the SEC EDGAR website. Here's how you can do it:

```python
from sec_downloader import Downloader

# Initialize the downloader with your company name and email
dl = Downloader("MyCompanyName", "email@example.com")

# Download the latest 10-Q filing for Apple
html = dl.get_latest_html("10-Q", "AAPL")
```

> **Note**
The company name and email address are used to form a user-agent string that adheres to the SEC EDGAR's fair access policy for programmatic downloading. [Source](https://www.sec.gov/os/webmaster-faq#code-support)

Now, we can parse the filing into semantic elements and arrange them into a tree structure:

```python
import sec_parser as sp

# Parse the HTML into a list of semantic elements
elements = sp.Edgar10QParser().parse(html)

# Construct a semantic tree to allow for easy filtering by section
tree = sp.TreeBuilder().build(elements)

# Find section "Segment Operating Performance"
section = [n for n in tree.nodes if n.text.startswith("Segment")][0]

# Preview the tree
print("\n".join(sp.render(section).split("\n")[:13]) + "...")
```

<pre>
<b><font color="navy">TitleElement:</font></b> Segment Operating Performance
├── <b><font color="navy">TextElement:</font></b> The following table sho... (dollars in millions):
├── <b><font color="navy">TableElement:</font></b> 414 characters.
├── <b><font color="navy">TitleElement<font color="green">[L1]</font>:</font></b> Americas
│   └── <b><font color="navy">TextElement:</font></b> Americas net sales decr... net sales of Services.
├── <b><font color="navy">TitleElement<font color="green">[L1]</font>:</font></b> Europe
│   └── <b><font color="navy">TextElement:</font></b> The weakness in foreign...er net sales of iPhone.
├── <b><font color="navy">TitleElement<font color="green">[L1]</font>:</font></b> Greater China
│   └── <b><font color="navy">TextElement:</font></b> The weakness in the ren...er net sales of iPhone.
├── <b><font color="navy">TitleElement<font color="green">[L1]</font>:</font></b> Japan
│   └── <b><font color="navy">TextElement:</font></b> The weakness in the yen..., Home and Accessories.
└── <b><font color="navy">TitleElement<font color="green">[L1]</font>:</font></b> Rest of Asia Pacific
    ├── <b><font color="navy">TextElement:</font></b> The weakness in foreign...lower net sales of Mac....
</pre>

For more examples and advanced usage, you can continue learning how to use `sec-parser` by referring to the [**User Guide**](https://sec-parser.readthedocs.io/en/latest/notebooks/user_guide.html), [**Developer Guide**](https://sec-parser.readthedocs.io/en/latest/notebooks/developer_guide.html), and [**Documentation**](https://sec-parser.rtfd.io).

## What's Next?

You've successfully parsed an SEC document into semantic elements and arranged them into a tree structure. To further analyze this data with analytics or AI, you can use any tool of your choice.

For a tailored experience, consider using our free and open-source library for AI-powered financial analysis: 

```bash
pip install sec-ai
```

[**Explore `sec-ai` on GitHub**](https://github.com/alphanome-ai/sec-ai)

# Best Practices

## Importing modules

1. Standard: `import sec_parser as sp`
1. Package-Level: `from sec_parser import SomeClass`
1. Submodule: `from sec_parser import semantic_tree`
1. Submodule-Level: `from sec_parser.semantic_tree import SomeClass`

> **Note**
The root-level package `sec_parser` contains only the most common symbols. For more specialized functionalities, you should use submodule or submodule-level imports.

> **Warning**
To allow us to maintain backward compatibility with your code during internal structure refactoring for `sec-parser`, avoid deep or chained imports such as `sec_parser.semantic_tree.internal_utils import SomeInternalClass`.

# Contributing
For information about setting up the development environment, coding standards, and contribution workflows, please refer to our [CONTRIBUTING.md](https://github.com/alphanome-ai/sec-parser/blob/main/CONTRIBUTING.md) guide.

# License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/alphanome-ai/sec-parser/blob/main/LICENSE) file for details.
