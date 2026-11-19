# Learning Guide

**Português:** [Leia a versão em português](learning-guide.md).

## 1. Why does this guide exist?

This project has two equally important goals:

1. **Software development portfolio:** present a solution built around a practical problem and document its technical decisions, implementation, and evolution.
2. **Learning and knowledge sharing:** help others understand the problem, follow the solution, reproduce it locally, and adapt it to similar needs.

This guide turns the repository into a learning path, rather than just a collection of files to copy.

## 2. The scenario being simulated

Imagine a workflow that an employee would perform manually:

1. Open a CRM and sign in.
2. Generate a deals report.
3. Download the report as an Excel file.
4. Open another system used to store documents.
5. Sign in to that second system.
6. Upload the downloaded file.

This project demonstrates how to automate that workflow with a robot that controls a browser.

**Important:** the CRM and Cloud Library in this repository are fictional applications built for demonstration purposes. The project does not connect to real CRMs, cloud providers, or corporate systems.

## 3. What you can learn

By studying this project, you can understand:

- How to break a problem into automatable steps.
- How Python organizes an application's logic.
- How FastAPI and Uvicorn serve web applications locally.
- How Playwright controls a browser through its interface.
- How an Excel report can be generated with openpyxl.
- How files can be received, validated, and stored.
- How SQLite records metadata and version history.
- How configuration and demonstration credentials are separated from source code.
- How to document, run, and verify a solution.

## 4. Recommended learning path

### Step 1 — Understand the scenario before reading the code

Read the opening sections of the [README](../README.md) and the [Project Architecture](architecture.en.md).

Before opening the Python files, try to answer:

- What manual work are we automating?
- Which two systems are involved?
- What is the robot responsible for?
- Why are the systems simulated locally?

**Goal:** understand the problem and its components before getting into implementation details.

### Step 2 — Set up and run the environment

Follow the requirements, installation, configuration, and execution instructions in the [README](../README.md).

The project uses three local processes:

| Component | Address or command | Purpose |
|---|---|---|
| Demo CRM | http://127.0.0.1:8000 | Generates the report |
| Cloud Library | http://127.0.0.1:8001 | Receives and stores the report |
| Robot | python -m crm_cloud_demo.automation.run | Controls the browser and transfers the file |

Start both applications and open their pages in a browser first. Then run the robot and observe the workflow.

**Goal:** recognize that the CRM, Cloud Library, and automation are separate components.

### Step 3 — Follow the robot's execution path

Read these files in order:

1. **src/crm_cloud_demo/automation/run.py** — entry point and main sequence. The run_automation function coordinates the steps.
2. **src/crm_cloud_demo/automation/browser.py** — creates the browser session, enables downloads, and closes resources at the end.
3. **src/crm_cloud_demo/automation/crm.py** — contains CRM login and report download.
4. **src/crm_cloud_demo/automation/cloud.py** — contains Cloud Library login and file upload.
5. **src/crm_cloud_demo/config.py** — gathers the settings used by the applications and the automation.

While reading, follow this sequence:

**run_automation → browser_session → CRM login → Excel download → Cloud Library login → upload → confirmation.**

Pay attention to these Playwright operations:

- **page.goto()**: navigates to a page.
- **page.locator()**: locates interface elements.
- **fill()**: fills in a field.
- **click()**: activates an element.
- **page.expect_download()**: waits for a download.
- **set_input_files()**: selects a file for upload.

These are Playwright operations called from Python. In the main workflow, the robot interacts with the web interfaces instead of directly calling the internal APIs of the two applications.

### Step 4 — Understand how the CRM creates the Excel report

Read:

- **src/crm_cloud_demo/apps/crm/routes.py** — routes that receive browser requests.
- **src/crm_cloud_demo/apps/crm/services.py** — fictional data, filters, and spreadsheet creation.

Look for the **get_deals** and **create_excel_report** functions.

Questions to guide your reading:

- Where do the deal records come from?
- How is the date range applied?
- Which worksheets are created?
- How are values and dates formatted?
- Why does the function return an in-memory file before the application makes it available for download?

### Step 5 — Understand how the Cloud Library receives and stores the file

Read:

- **src/crm_cloud_demo/apps/cloud/routes.py** — login, dashboard, and upload routes.
- **src/crm_cloud_demo/apps/cloud/storage.py** — validation, storage, and database records.

Pay attention to these functions and concepts:

- **_safe_filename**: handles the received filename.
- **_validate_xlsx**: checks whether the content has the expected characteristics of an XLSX workbook.
- **save_document**: writes the file and records its metadata.
- **list_documents**: retrieves registered documents.
- **SQLite:** stores information about the document, such as its name, size, hash, version, and upload date.

An important distinction: the Excel file is stored in the local file system; SQLite stores its metadata and history. The database is not, by itself, the Excel file.

### Step 6 — Understand how to verify the workflow

A success message alone is not enough. Think about evidence for each step:

- Did login reach the expected page?
- Was the report downloaded?
- Does the file exist and is it non-empty?
- Was the upload accepted?
- Did the Cloud Library display a confirmation?
- Does the document appear in the history with the expected version and metadata?

**Test status in the repository:** the currently published version declares pytest as a development dependency, but does not yet contain the automated test directory. Do not confuse an installed dependency with a published test suite. Check project updates for the tests and their corresponding code.

### Step 7 — Think about adapting the solution

Once you understand the simulation, consider how it might change in another context:

- Could the source system have different fields or filters?
- Could the report contain different columns?
- Could the destination require different validation?
- How should login, download, or upload failures be handled?
- What additional controls would be needed before any use with real systems?

Never use third-party credentials, data, or systems without authorization. The current implementation is a local demonstration and must not be deployed directly to production.

## 5. Quick glossary

| Term | Meaning in this project |
|---|---|
| Automation | Performing tasks through programmed instructions |
| CRM | Demo system that provides the data and report |
| Cloud Library | Demo system that receives and stores the file |
| Browser | Application that opens and displays web pages |
| Playwright | Tool that allows a browser to be controlled through code |
| FastAPI | Python framework used to build the web applications |
| Uvicorn | Server used to run ASGI applications |
| Excel / XLSX | Format of the transferred report |
| SQLite | Local database used for metadata and versions |
| Route | Address and operation exposed by a web application |
| Upload | Sending a file to another application |
| Download | Transferring a file to the local computer |

## 6. How to use this material

You do not need to understand everything at once. Study one stage at a time, run the example, open the referenced file, and try to explain what it does in your own words.

By the end, you should be able to:

- Describe the problem the automation solves.
- Explain the responsibility of each component.
- Explain why the technologies were selected.
- Follow the workflow in the code.
- Identify what is implemented and what still needs improvement.
- Adapt the idea safely to a similar scenario.

This project was independently developed in Brazil and documented in Portuguese and English to share knowledge with a wider community.
