# QA API Automation Showcase

A compact public-safe QA automation project for a fake fintech / crypto audit API.

The goal is to demonstrate practical API test automation without using real exchange data, secrets, or live services.

## What this project shows

- pytest-based API test structure
- reusable API client abstraction
- positive and negative API tests
- response schema validation
- business-rule assertions
- sample test report
- GitHub Actions CI workflow
- public-safe fake data only

## Test domain

The fake API represents a simplified audit service for crypto bot accounts.

Example endpoints:

- GET /accounts/{account_id}/nav
- GET /accounts/{account_id}/trades
- POST /audit/hodl-benchmark
- POST /audit/risk-label

Core product rule:

```text
Green PnL is not enough.
A bot can make money in USDT and still fail the HODL benchmark.
```

## Also in this repo: Playwright TypeScript E2E suite

`web-e2e-playwright-ts/` contains a UI + API + consistency test suite written in Playwright (TypeScript) against a small local invoice app, with its own GitHub Actions workflow. See its [README](web-e2e-playwright-ts/README.md).

## Quick start

```bash
python -m pytest -q
```

Expected result:

```text
11 passed
```

## Repository safety

```text
PUBLIC_SAFE = YES
LIVE_API_CALLS = NO
REAL_ACCOUNT_DATA = NO
EXCHANGE_KEYS = NO
SECRETS = NO
```

## Professional focus

This showcase is relevant to:

- QA Automation
- API testing
- fintech QA
- crypto operations QA
- backend test design
- CI-ready test suites
- risk-based testing
