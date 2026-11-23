# Project Security Policy

**Português:** [Leia a versão em português](security.md).

## 1. Purpose

This document describes the security measures implemented and the improvements planned for the `automacao-crm-excel-cloud` project.

The project is an independent web automation demonstration built with Python, Playwright, and FastAPI.

All applications use synthetic data and run locally.

This document distinguishes implemented controls from measures that still need to be developed.

## 2. Project isolation

**Status: Implemented**

The project uses fictional and independent applications.

Measures adopted:

- Demo CRM developed exclusively for this project.
- Document library developed exclusively for this project.
- Synthetic business data.
- No integration with real corporate systems.
- No reuse of external credentials, cookies, or sessions.
- Local application execution.
- Use of `127.0.0.1` in the documented startup commands.

The project does not use real company infrastructure or information.

## 3. Credential and secret management

**Status: Partially implemented**

Credentials are loaded through environment variables using `python-dotenv`.

Implemented measures:

- Separation of configuration and source code.
- `.env` file protected by `.gitignore`.
- `.env.example` file containing fictional values.
- Independent credentials for the CRM and Cloud Library.
- Independent session secrets for both applications.
- Credential comparison using `secrets.compare_digest`.

Notes:

- Default credentials are predictable and intended exclusively for local demonstration.
- Session secrets can be generated randomly when they are not defined in the environment.
- Changing these secrets invalidates existing sessions.

Planned improvements:

- Implement a policy for changing demonstration credentials.
- Add authentication-attempt controls.
- Evaluate secure secret management for environments outside local development.

## 4. Git repository protection

**Status: Implemented and partially verified**

The `.gitignore` file contains rules intended to prevent local and sensitive files from being committed.

Protected files and directories include:

- `.env` and private configuration files.
- `.venv/` and other virtual environments.
- `logs/` and log files.
- `storage/` and local databases.
- Generated reports and spreadsheets.
- Download directories.
- Browser profiles and sessions.
- Private keys and sensitive certificates.
- Temporary files.

The rules were checked using `git check-ignore`.

Before publication, the files staged for the commit should be reviewed.

## 5. Log security

**Status: Partially implemented**

The project has a logging configuration module in `logging_config.py`.

However, integration of this module into the main automation workflow is still pending.

Logging guidelines:

- Do not store passwords.
- Do not store authentication tokens.
- Do not store cookies or session identifiers.
- Do not log private keys.
- Do not log personal data or confidential information.
- Do not log the full contents of reports.

Planned improvements:

- Integrate the logging module with the orchestrator.
- Standardize workflow log entries.
- Record errors without exposing sensitive information.
- Implement rotation and storage limits for log files.

## 6. Browser automation security

**Status: Implemented**

Playwright uses an independent browser context during execution.

Implemented measures:

- Chromium is launched through Playwright.
- An isolated browser context is created.
- Downloads are enabled.
- Operation timeouts are configured.
- The browser context and browser are closed at the end of execution.
- Personal and corporate browser profiles are not reused.
- Credentials are loaded from local configuration.

The project does not import cookies or sessions from external browsers.

## 7. File upload security

**Status: Implemented**

The document library validates files before storing them.

Implemented controls:

- Only `.xlsx` files are accepted.
- File extension and signature are checked.
- The internal ZIP structure is checked.
- Expected Excel file components are checked.
- File integrity and spreadsheet readability are checked.
- Maximum upload size of 10 MB.
- Maximum uncompressed content size of 50 MB.
- Maximum of 250 entries in the ZIP archive.
- Original filenames are sanitized.
- Unique identifiers are used for stored files.

The `.xlsx` extension alone is not considered sufficient to determine whether a document is valid.

These checks are intended for demonstration purposes and do not guarantee protection against every type of malicious file.

## 8. Database and storage

**Status: Implemented**

The project uses SQLite and local storage.

Implemented measures:

- Storage kept separate from source code.
- Unique internal filenames.
- Document metadata records.
- SHA-256 hash calculation.
- Version control.
- Recording of file size and upload time.
- Database transactions for metadata registration.
- Cleanup of the created file when a failure occurs during the storage operation.

The database and uploaded files remain outside version control through `.gitignore`.

The storage system was not designed for shared use in production environments.

## 9. Authentication and sessions

**Status: Partially implemented**

Both applications use independent authentication.

Implemented measures:

- Fictional credentials.
- Secure credential comparison.
- Independent sessions.
- Different session secrets.
- Different cookie names.
- Session termination through logout.

Current limitations:

- CSRF protection has not been implemented in the forms.
- Login attempts are not rate-limited.
- Cookie settings are appropriate for the local HTTP environment, not for a public deployment.

These points must be addressed before any adaptation for real-world use.

## 10. Error handling

**Status: Partially implemented**

The current implementation includes checks for:

- Invalid credentials.
- Missing files.
- Unsupported extensions.
- Empty files.
- Files exceeding the defined limits.
- Invalid Excel structures.
- Navigation and download failures.
- Missing upload confirmation.

Planned improvements:

- Standardize automation exceptions.
- Improve handling of application unavailability.
- Integrate failure records with the logging system.
- Add tests for failure scenarios.

## 11. Dependencies and maintenance

**Status: Partially implemented**

Dependencies are centralized in `pyproject.toml`.

The project uses its own virtual environment.

Guidelines:

- Install dependencies inside the project virtual environment.
- Avoid unnecessary libraries.
- Keep dependencies documented.
- Review relevant updates.
- Check for vulnerabilities before important upgrades.

Automated dependency vulnerability auditing is still pending.

### External exchange-rate lookup

The English interface calls the public endpoint `https://api.frankfurter.dev/v2/rate/brl/usd` to retrieve the BRL/USD reference rate. The request contains only the currency pair; it does not send CRM deal records, names, files, or credentials. The API does not require an authentication key. The application sets a five-second timeout and caches the rate for six hours. If no valid rate is available, USD amounts and the corresponding export are unavailable rather than being calculated with a hard-coded value.

Frankfurter publishes reference rates, not real-time trading quotes. The Portuguese interface does not depend on this request and continues to display the original BRL amounts.

## 12. Usage limitations

This project is intended exclusively for educational and demonstration purposes.

It was not designed to:

- Process real company information.
- Operate corporate systems.
- Store confidential documents.
- Receive files from unknown users over the internet.
- Provide enterprise-grade authentication or storage.

The implemented measures do not constitute a security certification and do not guarantee production suitability.

## 13. Security checklist

### Implemented controls

- [x] Synthetic data.
- [x] Fictional credentials.
- [x] Separation of configuration and source code.
- [x] Protection of `.env` through `.gitignore`.
- [x] Protection of local databases and reports.
- [x] Independent sessions.
- [x] Isolated Playwright context.
- [x] Excel file validation.
- [x] File size and structure limits.
- [x] Storage with unique identifiers.
- [x] Version and hash records.
- [x] External request limited to the BRL/USD rate, with no business data or credentials sent.

### Pending improvements

- [ ] CSRF protection in forms.
- [ ] Authentication-attempt rate limiting.
- [ ] Full logging integration.
- [ ] Log rotation.
- [x] Initial unit tests for localization and Excel report exports.
- [ ] Expanded test coverage and integration tests.
- [ ] Automated dependency auditing.
- [ ] Final review of files staged for publication.

## 14. Security commitment

Security is part of the project's ongoing development.

New features should follow the principles of isolation, data protection, input validation, and access control.

The project will remain independent from corporate systems and will use only fictional environments and data.
