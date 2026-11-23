# Quality Assurance and Testing Strategy

**Português:** [Leia a versão em português](quality-assurance.md).

## 1. Purpose

This document describes how the automacao-crm-excel-cloud project verifies the behavior of its applications, storage layer, and automation robot.

The strategy combines unit tests, HTTP integration tests, and an end-to-end test using real Chromium. The goal is to verify observable behavior and relevant failure paths, not merely to execute lines of code.

## 2. Test levels

### 2.1 Unit tests — tests/unit/

These verify isolated components, including:

- Configuration loading and validation.
- Language selection, translations, and safe return-path validation.
- BRL/USD conversion, rounding, caching, and invalid exchange-rate provider responses.
- Excel report generation in Portuguese and English.
- Filename sanitization, XLSX validation, persistence, hashes, versions, and storage rollback.
- Logging configuration and browser resource cleanup.
- Robot login, download, upload, and orchestration helpers.

### 2.2 Integration tests — tests/integration/

These use FastAPI's TestClient to send actual HTTP requests to the local demo applications.

Scenarios include:

- Valid and invalid login, logout, and protected routes.
- Independent language preferences.
- CRM dashboard in BRL and USD, including exchange-rate unavailability.
- Excel report exports in both languages.
- Date validation and error responses.
- Upload of valid files, unsupported extensions, and corrupted workbooks.
- File persistence, SHA-256 hashes, and SQLite version history.

### 2.3 End-to-end test — tests/e2e/

The E2E test starts both FastAPI servers on available local ports and uses real Chromium controlled by Playwright.

The robot completes the full sequence:

1. Opens and authenticates to the CRM.
2. Requests the report export.
3. Downloads the Excel workbook.
4. Opens and authenticates to the Cloud Library.
5. Uploads the file through the web interface.
6. Verifies the confirmation, stored file, SHA-256 hash, and SQLite version record.
7. Verifies the log file and confirms that demonstration passwords were not recorded.

This test uses fictional applications, test credentials, and temporary storage. It does not access corporate systems.

## 3. Continuous integration

The .github/workflows/ci.yml workflow runs automatically on pushes to main and on pull requests.

The pipeline:

1. Sets up Python 3.14.
2. Installs the project and development dependencies.
3. Installs Chromium through Playwright.
4. Runs unit, integration, and E2E tests.
5. Produces a coverage report for the crm_cloud_demo package.
6. Requires at least 100% line coverage for that package.
7. Runs Ruff to check code quality and static formatting.

Older runs for the same branch may be cancelled so the latest commit receives priority.

## 4. Running the tests locally

In PowerShell, with the virtual environment activated:

```powershell
$env:PLAYWRIGHT_BROWSERS_PATH = "$PWD\.playwright-browsers"
python -m playwright install chromium

python -m pytest tests -v --cov=crm_cloud_demo --cov-report=term-missing --cov-fail-under=100
python -m ruff check src tests
```

The E2E test requires Chromium to be installed in the directory configured by PLAYWRIGHT_BROWSERS_PATH.

## 5. Interpreting coverage

The 100% coverage requirement refers to executable statements in the crm_cloud_demo Python package as measured by Coverage.py during the test suite.

It does not mean that:

- Every possible behavior has been tested.
- Every combination of paths or conditions has been formally verified.
- Third-party dependencies or HTML templates have 100% coverage.
- The application has undergone a security audit or penetration test.
- The project is ready to operate real enterprise systems.

Coverage is useful evidence, but it must be considered alongside test scenarios, E2E checks, known limitations, and code review.

## 6. Limitations and scope

- Currency tests use controlled responses to keep results deterministic; external API availability depends on the network and provider.
- The E2E test proves the workflow in local fictional applications, not in real CRMs, document libraries, or corporate systems.
- CSRF protection and login-attempt rate limiting remain pending before any public exposure.
- The test suite is not a security certification and does not replace independent review.

The results should be presented as automated validation of an independent educational demonstration.


## 7. Evidence from the latest run

**Run verified on November 23, 2026:** [GitHub Actions — run 45234968343](https://github.com/PG-Lima/automacao-crm-excel-cloud/actions/runs/45234968343).

| Check | Result |
|---|---:|
| Unit, integration, and E2E tests | 111 passed |
| Executable statements in the package | 634 |
| Uncovered statements | 0 |
| Package line coverage | 100% |
| Ruff check | Passed |
| Real Chromium and Playwright workflow | Passed |

The CI environment used Python 3.14. The run verified authentication, download, upload, persistence, hashing, versioning, and logging, in addition to unit and integration scenarios.

This result is a snapshot of the referenced run. New commits continue to be validated automatically by the pipeline.
