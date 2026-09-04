# Conduit E2E Test Automation

Playwright (Python) end-to-end test suite for the [Conduit](https://conduit.bondaracademy.com/) demo app, covering:

- Create New Article
- Edit Article (created via API as a pre-condition)
- Delete Article (created via API as a pre-condition)
- Filter Articles by Tag
- Update User Settings

Each scenario has one positive and one negative test (10 tests total).

## Project structure

```
config/       Runtime configuration (base URLs, auth storage key)
api/          Thin API client used for test pre-conditions (register user, create article)
pages/        Page Object Model (one class per page/component)
utils/        Dynamic/randomized test data generation (Faker)
tests/        One file per scenario
conftest.py   Session-scoped authentication fixture (see below)
```

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (manages the Python interpreter and dependencies -- no separate Python install needed)

## Setup

```bash
uv sync
uv run playwright install --with-deps   # downloads the browser binaries
```

## Running the tests

```bash
# Default: chromium, sequential
uv run pytest

# A specific browser
uv run pytest --browser firefox
uv run pytest --browser webkit

# All three browsers in one run
uv run pytest --browser chromium --browser firefox --browser webkit

# In parallel (auto-detects CPU count)
uv run pytest -n auto

# Combine both
uv run pytest --browser firefox -n auto
```

Every run writes:
- Allure results to `reports/allure-results/`
- Playwright traces/screenshots/videos **only for failed tests** to `reports/test-results/` (`--tracing=retain-on-failure`, `--screenshot=only-on-failure`, `--video=retain-on-failure`, configured in `pyproject.toml`)

## Viewing the Allure report

Generating the HTML report locally requires the [Allure commandline](https://allurereport.org/docs/install/), which in turn requires a JRE. If you have it installed:

```bash
allure serve reports/allure-results
```

If you don't want to install Java locally, every CI run publishes a ready-made `allure-report` artifact (see below) -- download it from the workflow run and open `index.html`.

## Session management (authentication)

Rather than logging in through the UI before every test, `conftest.py` registers one throwaway, randomly-generated user via the Conduit API **once per test process** (`registered_user`, session-scoped) and seeds that user's JWT into `localStorage` via Playwright's `storage_state` mechanism (`browser_context_args`). Every test therefore starts already authenticated, with no repeated logins. Running with `pytest-xdist` (`-n auto`) is safe: each worker is a separate process with its own session-scoped fixture, so each worker gets its own isolated user -- no collisions.

## Dynamic test data

`utils/data_generator.py` uses [Faker](https://faker.readthedocs.io/) (plus short unique suffixes for anything with uniqueness constraints, like usernames) to generate users, articles, bios and image URLs. No test hard-codes an input value.

## A known app bug worth flagging

The Settings page's form never re-populates its own fields on load or reload (reproducible via direct API calls, independent of this test suite -- see `test_update_settings_success`'s comment). Because of this, that test verifies the update persisted by checking the **public profile page** (`/profile/<username>`), which does correctly reflect saved changes, rather than reloading the Settings form itself.

## CI/CD

`.github/workflows/tests.yml` runs on every push/PR:
- A matrix job runs the full suite in parallel (`-n auto`) across Chromium, Firefox and WebKit
- Playwright traces/screenshots/videos are uploaded as workflow artifacts whenever a browser's job fails
- Raw Allure results from all three browsers are merged and turned into a single HTML report, uploaded as the `allure-report` artifact on every run (pass or fail)
