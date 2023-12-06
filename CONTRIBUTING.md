# How to Contribute?

Contributing to `sec-parser` is a rewarding way to learn and improve this open-source project. Whether you are a user looking to expand your knowledge or a developer eager to delve into the codebase, this guide is here to help you get started.

## Find specific things to work on

Check out our [**Contribution Workflow**](https://github.com/alphanome-ai/common-contributing-guide#contribution-workflow).

## Understanding the Workflows

Before diving into the codebase guides, we recommend setting up your environment and understanding our contribution workflow. Please visit [**Common Contributing Guide**](https://github.com/alphanome-ai/common-contributing-guide) for information on environment setup, coding standards, and contribution workflows that are common across our repositories.

## Exploring the Codebase

If you are new to `sec-parser` and would like to get started, please refer to the [**Quickstart User Guide**](https://sec-parser.readthedocs.io/en/latest/notebooks/user_guide.html).
  
For those interested in contributing to `sec-parser`, the [**Comprehensive Developer Guide**](https://sec-parser.readthedocs.io/en/latest/notebooks/developer_guide.html) provides an in-depth walkthrough of the codebase and offers examples to help you contribute effectively.

Both guides are interactive and allow you to engage with the code and concepts as you learn. You can run and modify all the code examples for yourself by cloning the repository and running the respective notebooks in a Jupyter environment.

Alternatively, you can run the notebooks directly in your browser using Google Colab.

> [!NOTE]
Before contributing, we highly recommend familiarizing yourself with these guides. They will help you understand the structure and style of our codebase, enabling you to make effective contributions.

# Advanced Topics

## Running End-to-End (e2e) Tests

We take code quality and reliability seriously. Alongside unit tests, we have implemented an End-to-End (e2e) Testing workflow to validate the parser against real-world SEC EDGAR HTML documents. This section will guide you through running these e2e tests.

### Why e2e Tests?

While unit tests focus on individual components, e2e tests ensure the whole system, from parsing HTML documents to generating semantic elements and trees, works as expected. These tests use real-world data scenarios to measure the parser's reliability and efficiency.

### Prerequisites

The e2e tests pull data from the [sec-parser-test-data](https://github.com/alphanome-ai/sec-parser-test-data) repository, a separate repository containing a curated collection of real-world input documents and their expected outputs.

- **Automatic Cloning:** You don't need to manually download this dataset; it will be automatically cloned when you run the e2e test command.

### How to Run e2e Tests

To run the e2e tests, follow these steps:

1. **Navigate to the Project Directory:**
```bash
cd path/to/sec-parser
```

2. **Execute Verification Command:**
```bash
task snapshot-verify
```

#### Expected Outcomes

- **Success:** If the dataset matches, the output will look like this:

    ![Screenshot 2023-10-15 at 08 12 15](https://user-images.githubusercontent.com/4084885/275303580-1b98e567-3c9f-40a3-a127-316cfc5adcce.png)

- **Failure:** If discrepancies are found, the output will indicate the issues:

    ![Screenshot 2023-10-15 at 08 11 45](https://user-images.githubusercontent.com/4084885/275303575-5a84f757-3a07-4189-b19d-5b515b534f44.png)

### Performance Metrics

Note that certain performance metrics, such as parsing time, are also tracked. This helps us ensure efficiency as the project grows.

### CI/CD Integration

These e2e tests are part of our [Continuous Integration and Continuous Deployment (CI/CD) pipeline](https://github.com/alphanome-ai/sec-parser/actions) and run automatically after each commit to prevent regressions.

### Updating the e2e Dataset

To update the e2e dataset in line with any changes you've made to `sec-parser`, execute:

```bash
task e2e-generate
```

Make sure to include the `sec-parser` commit hash in your commit message for version tracking.

## Introduction to Exploratory Tests
### What are Exploratory Tests?
Exploratory Tests are designed to assess the parser's performance across a diverse set of financial documents. These tests ensure the parser's ability to operate consistently and accurately on different types of reports.

### Why Run Exploratory Tests?
Exploratory Tests add an extra layer of quality assurance beyond our existing unit and end-to-end tests. They help us quickly discover any issues the parser may have with specific kinds of documents.

### How to Run Exploratory Tests?

1. **Navigate to the Project Directory:** Open your terminal and go to the sec-parser folder.

2. **Execute the Test Command:** Run the following command to initiate the tests:

    ```
    task exploratory-tests
    ```

For a more focused test, you can run a customized test command. Locate the exploratory-tests command in the `Taskfile.yml`, copy it, and modify it to meet your needs. You could replace `tests/exploratory/` with a specific test, like `tests/exploratory/processing_steps/test_top_level_section_title_classifier.py`.

> [!NOTE]
We offer a script that allows you to expand the test database locally. Simply provide the stock tickers you're interested in, and the script will do the rest.

## Other helpful tips

- [Quick Tip: Speed Up sec-parser by Using a Profiler to Find Slow Areas](https://github.com/orgs/alphanome-ai/discussions/36)
- [Introducing Processing Logs: Enhancing Transparency in Semantic Element Transformations](https://github.com/orgs/alphanome-ai/discussions/37)

## What Can I Work On?

Check out the [Contribution Workflow](https://github.com/alphanome-ai/common-contributing-guide#contribution-workflow).
