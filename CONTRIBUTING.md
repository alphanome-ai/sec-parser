# How to Contribute?

Contributing to `sec-parser` is a rewarding way to learn and improve this open-source project. Whether you are a user looking to expand your knowledge or a developer eager to delve into the codebase, this guide is here to help you get started.

## Understanding the Workflows

Before diving into the codebase guides, we recommend setting up your environment and understanding our contribution workflow. Please visit [**Common Contributing Guide**](https://github.com/alphanome-ai/common-contributing-guide) for information on environment setup, coding standards, and contribution workflows that are common across our repositories.

## Exploring the Codebase

If you are new to `sec-parser` and would like to get started, please refer to the [**Quickstart User Guide**](https://sec-parser.readthedocs.io/en/latest/notebooks/user_guide.html).
  
For those interested in contributing to `sec-parser`, the [**Comprehensive Developer Guide**](https://sec-parser.readthedocs.io/en/latest/notebooks/developer_guide.html) provides an in-depth walkthrough of the codebase and offers examples to help you contribute effectively.

Both guides are interactive and allow you to engage with the code and concepts as you learn. You can run and modify all the code examples for yourself by cloning the repository and running the respective notebooks in a Jupyter environment.

Alternatively, you can run the notebooks directly in your browser using Google Colab.

> **Note**
Before contributing, we highly recommend familiarizing yourself with these guides. They will help you understand the structure and style of our codebase, enabling you to make effective contributions.

## Running End-to-End (e2e) Tests

We take code quality and reliability seriously. Alongside unit tests, we have implemented an End-to-End (e2e) Testing workflow to validate the parser against real-world SEC EDGAR HTML documents. This section will guide you through running these e2e tests.

### Why e2e Tests?

While unit tests focus on individual components, e2e tests ensure the whole system, from parsing HTML documents to generating semantic elements and trees, works as expected. These tests use real-world data scenarios to measure the parser's reliability and efficiency.

### Prerequisites

The e2e tests pull data from the `sec-parser-e2e-data` repository, a separate repository containing a curated collection of real-world input documents and their expected outputs.

- **Automatic Cloning:** You don't need to manually download this dataset; it will be automatically cloned when you run the e2e test command.

### How to Run e2e Tests

To run the e2e tests, follow these steps:

1. **Navigate to the Project Directory:**
```bash
cd path/to/sec-parser
```

2. **Execute Verification Command:**
```bash
task e2e-verify-dataset
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
task e2e-generate-dataset
```
Make sure to include the `sec-parser` commit hash in your commit message for version tracking.

## What Can I Work On?

Check out the [Contribution Workflow](https://github.com/alphanome-ai/common-contributing-guide#contribution-workflow).
