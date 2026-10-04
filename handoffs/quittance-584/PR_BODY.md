## Problem

Sellers currently have to poll the dashboard for invoice changes. Cancellation and expiry also lack payment audit events, so an external accounting or fulfillment system cannot reliably follow the invoice lifecycle.

## Change

Adds signed, at-least-once seller webhooks for `invoice.created`, `invoice.paid`, `invoice.cancelled`, `invoice.expired`, and `payment.rejected`.

- PostgreSQL triggers enqueue in the same transaction as invoice changes and rejection audit writes, including the existing settlement CTE. Cancel/expiry now record audit events. Memory storage prepares fallible outbox work before mutating invoices, audit state, or payment claims.
- Workers claim due delivery and endpoint rows with `FOR UPDATE SKIP LOCKED`, hold claims through a bounded attempt, and reuse the monitor's backoff with jitter. Retries preserve event IDs; attempt limits produce dead letters and repeated endpoint failures disable delivery.
- HMAC-SHA256 covers the timestamp and raw body. Secrets are shown once, hashed and encrypted at rest; rotation retains the old signature for a 24-hour overlap.
- Registration and each send validate public HTTPS destinations, recheck all DNS answers, pin the approved address while retaining TLS hostname checks, and refuse redirects. Payloads use an explicit privacy whitelist.
- Wallet proofs bind each management action, seller, endpoint, filters, timestamp, and single-use nonce. The dashboard adds registration, removal, rotation, test delivery, and recent history, with stale wallet/network responses discarded.
- Verification records rejection audit/outbox data before caching its verdict. A failed write returns a retryable 503 instead of silently losing the event.
- All three server entrypoints start and stop the worker with the server. `docs/WEBHOOKS.md` documents deployment, receiver verification, the signature vector, deduplication, and operational limits.

## Validation

Source: `77b18245e9d694a3b0a09900e36b2ecd3618b1c1`. Normal lockfile-based installs; Node 24.21.0 / npm 11.19.0.

- **16/16 webhook acceptance tests**, including real PostgreSQL 16.15 rollback, two separate worker processes, SIGKILL/restart recovery, an actual HTTP receiver returning 500/500/200, SSRF checks, signature rotation, signed API management, and the rejection/outbox cache boundary.
- **904/904 backend catalog tests** and backend typecheck.
- **760/760 frontend catalog tests**, frontend lint and typecheck.
- **41/41 shared contract tests**.

[Webhook/PostgreSQL, frontend, and shared run](https://github.com/woahwhattheheck/bounty-concierge/actions/runs/37204455112) tested `977da14c`. Its sole backend failure was an existing test expecting HTTP 404 from an unavailable Horizon endpoint. The only subsequent change supplies a real local HTTP 404 fixture; it retains the same assertion and changes no production code. [The final backend run](https://github.com/woahwhattheheck/bounty-concierge/actions/runs/37204940133) passes the complete catalog at `77b18245`.

Delivery is at least once, so receivers must atomically deduplicate the stable event ID. Memory mode is process-local; durable deployment requires PostgreSQL and a stable server-only encryption key.

Closes #584.
