# QuantFi (TuShare Pro Only) A股日频决策系统

本项目从零实现了一个**仅使用 TuShare Pro** 的 A 股日频决策 MVP，支持：
- 每日输出 Buy/Hold/Sell；
- PostgreSQL 全链路落库（Raw/ODS/Feature/Decision/Universe/RunLog）；
- 可回测、可复现、可追溯（版本+降级原因+run_log）。

## 1. 设计原则
1. **数据源仅 TuShare Pro**：`quantfi/core/tushare_client.py` 中统一访问 TuShare。
2. **权限/额度不足可降级**：接口失败不直接退出，记录 `degradation_reasons` + `confidence_penalty`。
3. **Point-in-time**：特征仅使用 `trade_date` 当日及以前数据。
4. **可复现**：同一 trade_date + versions（code/config/feature/data）输出稳定。
5. **CLI**：`init_db` / `run_daily` / `backtest`。
6. **Pytest**：覆盖去重、point-in-time、可复现、回测无未来函数。

## 2. 工程结构
- `quantfi/core`：配置、版本、TuShare 客户端
- `quantfi/ingest`：TuShare 拉取 + Raw/ODS 落库
- `quantfi/warehouse`：PostgreSQL schema + repository
- `quantfi/features`：Universe 与 Feature v1
- `quantfi/decision`：Decision v1
- `quantfi/backtest`：Backtest v1
- `quantfi/report`：日报
- `quantfi/ops`：日批编排
- `quantfi/scripts`：CLI
- `quantfi/tests`：pytest

## 3. 环境准备
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
export TUSHARE_TOKEN=你的token
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/quantfi
```

## 4. CLI 使用
### 4.1 初始化数据库
```bash
quantfi init_db
```

### 4.2 日批运行
```bash
quantfi run_daily --trade-date 20250103
```
运行顺序：
1) ingest（daily/adj/suspend/limit/index/sw/daily_basic）；
2) 生成 universe_snapshot（优先 `sw_daily`，失败则静态白名单）；
3) 计算 feature_daily；
4) 生成 decision_daily；
5) 输出日报到 `reports/`。

### 4.3 回测
```bash
quantfi backtest --decision-json samples/decisions.json --returns-json samples/returns.json
```

## 5. 可追溯输出
`decision_daily.payload` 字段包含：
- action
- score
- confidence
- top_factors
- top_risks
- evidence_links（MVP 为空）
- evidence_reason（为空原因）

`run_log` 记录每次任务状态、版本、降级原因和置信度折损。

## 6. 里程碑状态
- M0 工程骨架 + DB schema + 空跑通 ✅
- M1 TuShare client + Raw/ODS 落库 + 去重 ✅
- M2 行情主干 + 复权价 ✅
- M3 Universe 生成 + 兜底 ✅
- M4 Feature v1 + PIT 框架 ✅
- M5 Decision v1 + 风控覆盖 + 日报 ✅
- M6 Backtest v1 ✅
- pytest + README ✅
