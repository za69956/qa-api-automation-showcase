# Fake API Contract

This project uses an in-memory fake API client.

## GET /accounts/{account_id}/nav

Returns account NAV and asset price movement for a fake account.

Expected fields:

- account_id
- market
- account_nav_start_usdt
- account_nav_end_usdt
- asset_price_start_usdt
- asset_price_end_usdt

## GET /accounts/{account_id}/trades

Returns fake trades for a fake account.

Expected fields:

- account_id
- trades

Each trade contains:

- trade_id
- side
- price
- amount

## POST /audit/hodl-benchmark

Calculates account return, asset HODL return, excess vs HODL, and decision label.

Expected decision labels:

- HODL_PASS
- HODL_FAIL

## POST /audit/risk-label

Returns a simplified risk label based on HODL result and inventory percentage.

Expected risk labels:

- LIVE_SAFE
- HODL_FAIL
- INVENTORY_RISK
- NOT_PROMOTABLE
