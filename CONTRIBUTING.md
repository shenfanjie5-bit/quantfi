# Contributing Guide

## 1) Branch Strategy（简单可控）

- `main`：永远保持可运行、可回测、可复现（只通过 PR 合并）。
- `dev`：集成分支（可选；若流程更简单可省略，直接 `feat/* -> main`）。
- `feat/m0-skeleton`、`feat/m1-client` ...：每个里程碑一个 feature 分支。
- `hotfix/*`：线上/主干紧急修复。

### Merge Rules

- 只允许 `feat/* -> main`（或 `feat/* -> dev -> main`）。
- 禁止直接 push 到 `main`。
- 每个 PR 必须绑定一个里程碑（`M0`~`M6`）。

## 2) Milestones = Version Tags（可追溯）

每完成一个里程碑，在 `main` 打 tag：

- `v0.0.0-m0`：工程骨架 + DB schema + 空跑通
- `v0.0.0-m1`：TuShare Client + Raw/ODS + 去重
- `v0.0.0-m2`：行情主干 + 复权价
- `v0.0.0-m3`：Universe 快照
- `v0.0.0-m4`：Feature + PIT 框架
- `v0.0.0-m5`：Decision + 日报
- `v0.0.0-m6`：Backtest

任何结果都应可追溯到：`tag / commit / config`。

## 3) Commit Message Convention

统一使用 Conventional Commits：

```text
type(scope): message
```

示例：

- `feat(ingest): add daily + adj_factor loader`
- `fix(decision): enforce suspend hard rule`
- `test(pit): add as-of selection tests`
- `chore(ci): add ruff and pytest workflow`

建议 `type`：`feat | fix | test | refactor | chore | docs`。

## 4) PR Template（必须逐条勾选）

每个 PR 描述必须包含：

- `4.1 目标`：里程碑 + 3~10 条任务列表
- `4.2 验收（DoD）`：run_daily、DB 变更、pytest、降级可触发、README 更新
- `4.3 证据`：运行日志（含 `run_id`）、关键表查询 SQL/截图、回测指标（如适用）

## 5) CI Gates（最低配置）

PR 必须通过：

- `ruff`（lint）
- `black --check`（格式）
- `pytest -q`（单测）

## 6) Artifacts & Logging（验收/复盘）

### 6.1 run_log required fields

- `run_id`（UUID）
- `trade_date`
- `code_version`（git commit hash）
- `config_version`（config hash 或 commit hash）
- `data_version`（ingest 时间戳或版本号）
- `status`（`SUCCESS` / `DEGRADED` / `FAILED`）
- `degrade_reasons`（数组）
- `datasets_ok` / `datasets_failed`（数组）

### 6.2 Report artifacts（文件或 DB 二选一）

- `reports/YYYYMMDD/daily_report.md`
- `reports/YYYYMMDD/decision.json`

## 7) 显式降级策略（禁止异常吞掉）

每个可选数据域必须声明：

- `required: true/false`
- `on_missing: skip_module | fallback_data | abort`
- `impact: confidence_penalty`

示例：

- `daily_basic`：`required=false`；缺失 -> 跳过估值因子；`confidence -0.15`；记录 `NO_DAILY_BASIC_PERMISSION`

## 8) 里程碑拆分交付清单（每个 PR 只做一段）

- **M0**：repo 结构、config example、DB schema、`init_db`、`run_daily` 空跑、`run_log` 表
- **M1**：`tushare_client`（限流/重试/失败分类）、raw 落库、ODS 去重、`test_ingest_dedup`
- **M2**：`daily/adj/suspend/limit/index` 入库、复权价工具、不可交易标记
- **M3**：`universe_snapshot` 生成 + 兜底策略 + `fallback_reason`
- **M4**：`feature_daily`、completeness、PIT as-of 工具 + `test_point_in_time`
- **M5**：决策引擎、硬风控覆盖、日报、`test_decision_reproducible`
- **M6**：backtest CLI、成本与约束、不可交易处理、`test_backtest_no_future`

## 9) Working Instruction（一句话）

一次只做一个里程碑 PR；PR 必须带 DoD 勾选、日志证据、对应 pytest；允许缺权限降级，但必须可解释、可记录、可复现。
