# Guidelines for AI Coding Assistants (AGENTS.md)

Welcome! This file provides repository overview, architecture guidelines, developer environment setup, and styling/workflows standards for AI assistants contributing to this repository.

---

## 1. Project Overview & Architecture

This repository is a **Home Assistant Custom Integration** that retrieves utility rate structures from the **OpenEI API**.

### Core Directory Structure
- `custom_components/openei/`: Contains the integration code.
  - `__init__.py`: Component setup, setup entries, unloading, and coordinator.
  - `const.py`: Shared constants, domains, config keys.
  - `config_flow.py`: Setup flows and options flow handlers.
  - `sensor.py`: Home Assistant sensor entities representing rate structures.
  - `manifest.json`: Home Assistant custom component metadata.
- `tests/`: Pytest suite.
  - `conftest.py`: Shared testing fixtures.
  - `test_init.py`, `test_config_flow.py`, `test_sensors.py`: Unit tests.

---

## 2. Python Environment & Dependency Management

- **Target Python Version**: **3.14**
- **Environment Tooling**: **`uv`** is the standard tool for environment creation and dependency management.

### Setup and Testing
- Virtual environments are handled using `uv`.
- To install test dependencies:
  ```bash
  uv pip install -r requirements_tests.txt
  ```

---

## 3. Code Style, Linting & Type Checking

This codebase uses modern, fast Rust-based tooling for formatting and static analysis:
- **Linter & Formatter**: **Ruff** replaces `black`, `flake8`, `isort`, `pydocstyle`, and `pylint`.
- **Type Checker**: **mypy**.

### Configuration Locations
- Ruff configuration: Configured in `pyproject.toml`.
- Mypy configuration: Configured in `setup.cfg`.

### Local Execution Commands
- To run lint checks:
  ```bash
  ruff check .
  ```
- To run formatting checks:
  ```bash
  ruff format --check .
  ```
- To auto-format and fix autofixable lint errors:
  ```bash
  ruff check --fix . && ruff format .
  ```
- To run type checks:
  ```bash
  mypy custom_components/openei
  ```

---

## 4. Git Hooks (`prek`)

This project uses **`prek`** (a fast, Rust-based drop-in replacement for the `pre-commit` framework) to run git hooks.
- Hook definitions: [`.pre-commit-config.yaml`](file:///.pre-commit-config.yaml).
- Run all checks manually:
  ```bash
  prek run --all-files
  ```

---

## 5. Test Suite

Unit tests are written with `pytest` and orchestrated using `tox` and **`tox-uv`**.
- Test runner configuration: [`tox.ini`](file:///tox.ini).
- Running tests locally:
  ```bash
  tox
  ```

---

## 6. CI/CD & Security Hardening Guidelines

When modifying or introducing new GitHub Actions workflows, adhere to the following rules:

### A. Pin Actions to Commit SHAs
Do **NOT** use version tags (e.g., `@v4`, `@master`, `@main`) for Actions. Pin them to full-length 40-character commit SHAs. Use comment tags to document human-readable versions:
```yaml
uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2
```

### B. Use Step-Security Harden-Runner
Add `step-security/harden-runner` as the **first step** in every job running on hosted runners to monitor outbound traffic:
```yaml
- name: Harden Runner
  uses: step-security/harden-runner@5c7944e73c4c2a096b17a9cb74d65b6c2bbafbde # v2.9.1
  with:
    egress-policy: audit
```

### C. Restrict GITHUB_TOKEN Permissions
Specify minimal default permissions at the top level of each workflow:
```yaml
permissions:
  contents: read
```

### D. Conventional Commit PR Titles
All pull request titles must follow the Conventional Commits specification (e.g., `feat: ...`, `fix: ...`, `ci: ...`).
- Workflow checks: Managed via the `Semantic PR Check` action in `.github/workflows/semantic-pr.yaml`.
- Auto-labeling: Handled automatically by the built-in autolabeler in `.github/release-drafter.yml`.
