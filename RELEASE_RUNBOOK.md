# Release Runbook

## Pre-Release
1. Confirm plan and scope freeze.
2. Confirm env vars and external dependencies.
3. Run quality gates and acceptance checks.

## Deploy
1. Deploy release candidate.
2. Verify domain, SSL, and service health.

## Smoke Tests
1. Validate critical user journeys.
2. Validate logs and error rates.

## Rollback
- Trigger rollback on critical journey failure, severe regressions, or security issues.
