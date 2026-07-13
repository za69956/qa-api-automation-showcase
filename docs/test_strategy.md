# Test Strategy

This project demonstrates a compact QA automation workflow for a fake crypto audit API.

## Test scope

Covered:

- account NAV retrieval
- trade history retrieval
- HODL benchmark calculation
- risk label classification
- validation of bad input
- validation of unknown accounts

Not covered:

- real Binance API
- real Hummingbot runtime
- live trading
- authentication against production services
- private account reconciliation

## Test design

The tests combine:

- status-code checks
- response body assertions
- schema validation
- business-rule validation
- negative-path tests

## Risk focus

The most important product risk is a false positive trading conclusion.

Example:

- account NAV is positive
- asset HODL return is higher
- correct result must be HODL_FAIL

This is why tests validate the business label, not only HTTP status.
