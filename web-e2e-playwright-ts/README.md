# Web E2E + API tests with Playwright (TypeScript)

A small invoice app (Node, no dependencies) and a Playwright TypeScript suite that tests it through the UI, through the REST API, and checks that both agree.

The app runs locally from `app/server.js`, so the suite needs no external site, no accounts and no secrets. All data is fictional.

## What is tested

| Spec | What it checks |
|---|---|
| `ui.spec.ts` | Add invoice, VAT and gross per row, running totals, field validation, duplicate number, delete updates totals. Runs on desktop Chrome and a Pixel 7 mobile viewport. |
| `api.spec.ts` | 201 with calculated VAT, 400 with per-field errors, malformed JSON, 409 on duplicate (original unchanged), 404 on unknown id, summary equals the sum of stored invoices to the cent. |
| `consistency.spec.ts` | What the user sees is what was saved: UI → API record matches exactly once, API → UI after reload, double-click on Add does not create a duplicate. |

19 tests, each starting from an empty backend (auto fixture), so they never depend on each other.

## Structure

```
app/server.js            invoice service: JSON API + static UI, in-memory storage
app/public/              UI (plain HTML/JS)
tests/pages/             Page Object for the invoices screen
tests/fixtures.ts        auto reset of the backend, API helper
tests/*.spec.ts          UI, API and consistency suites
playwright.config.ts     desktop + mobile projects, traces/screenshots on failure
```

## Run

```bash
cd web-e2e-playwright-ts
npm ci
npx playwright install chromium
npx playwright test
npx playwright show-report
```

CI: `.github/workflows/e2e-playwright.yml` type-checks, runs the suite on every push and uploads the HTML report as an artifact.

## A real bug this suite caught

While writing it, `rounds VAT to cents on awkward amounts` failed: a valid net amount of `19.99` was rejected with "Max 2 decimals". The validation compared `Math.round(net * 100) !== net * 100`, and in floating point `19.99 * 100` is `1998.9999999999998`. Fixed by comparing in cents with a tolerance (see `app/server.js`). The test stays in the suite as a regression check.
