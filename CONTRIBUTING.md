# Contributing Guide

## Branch Strategy

- `main` must always stay runnable, backtestable, and reproducible.
- Use milestone-scoped feature branches such as:
  - `feat/m0-skeleton`
  - `feat/m1-client`
  - ...
- Emergency fixes use `hotfix/*`.
- Merge policy:
  - only `feature/* -> main` (or `feature/* -> dev -> main` if `dev` is used)
  - no direct pushes to `main`
  - each PR must bind to one milestone (`M0`~`M6`)

## Milestones and Tags

Each completed milestone is tagged on `main`:

- `v0.0.0-m0`: skeleton + DB schema + dry-run
- `v0.0.0-m1`: TuShare client + Raw/ODS + dedup
- `v0.0.0-m2`: market ingestion + adjusted price
- `v0.0.0-m3`: universe snapshot
- `v0.0.0-m4`: features + PIT framework
- `v0.0.0-m5`: decision + daily report
- `v0.0.0-m6`: backtest

## Commit Message Convention

Use Conventional Commits format:

```text
type(scope): message
```

Recommended `type`: `feat | fix | test | refactor | chore | docs`.

Examples:

- `feat(ingest): add daily + adj_factor loader`
- `fix(decision): enforce suspend hard rule`
- `test(pit): add as-of selection tests`
- `chore(ci): add ruff and pytest workflow`

## CI Gates

Every PR must pass:

- `ruff`
- `black --check`
- `pytest -q`

## Logging and Reproducibility Requirements

`run_log` must include:

- `run_id` (UUID)
- `trade_date`
- `code_version` (git commit hash)
- `config_version` (config hash/commit)
- `data_version` (ingest timestamp/version)
- `status` (`SUCCESS | DEGRADED | FAILED`)
- `degrade_reasons` (array)
- `datasets_ok` / `datasets_failed` (array)

## Degradation Policy

Optional data domains must declare explicit strategies:

- `required: true/false`
- `on_missing: skip_module | fallback_data | abort`
- `impact: confidence_penalty`

Example:

- `daily_basic`: `required=false`, on missing -> skip valuation features, confidence `-0.15`, log `NO_DAILY_BASIC_PERMISSION`.

## Milestone-by-Milestone PR Scope

One PR must only deliver one milestone slice:

- M0: skeleton, config example, DB schema, init_db, run_daily dry-run, run_log table
- M1: client with rate-limit/retry/error classes, raw ingest, ODS dedup, `test_ingest_dedup`
- M2: daily/adj/suspend/limit/index ingestion, adjusted price utility, non-tradable flags
- M3: `universe_snapshot` generation + fallback reason
- M4: `feature_daily`, completeness, PIT as-of utility + `test_point_in_time`
- M5: decision engine, hard risk rules, report + `test_decision_reproducible`
- M6: backtest CLI, cost/constraints, non-tradable handling + `test_backtest_no_future`
