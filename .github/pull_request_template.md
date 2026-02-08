# PR 标题规范
建议：`Mx: <short summary>` 例如 `M2: ingest daily + adj_factor`

---

## 目标 / Scope
- 里程碑（必填）：M0 / M1 / M2 / M3 / M4 / M5 / M6
- 本 PR 完成了什么（3-10 条）：
  1.
  2.
  3.

## 变更类型
- [ ] feat
- [ ] fix
- [ ] refactor
- [ ] test
- [ ] chore/docs

## DoD 验收清单（必须勾选）
- [ ] `poetry run python scripts/run_daily.py --date YYYYMMDD` 可运行（或明确说明尚未要求该里程碑）
- [ ] 关键数据写入 DB（列出表名）：
  - [ ] run_log
  - [ ] raw_tushare
  - [ ] ODS: ____________________
  - [ ] feature_daily / decision_daily / universe_snapshot（如适用）
- [ ] 降级路径可触发且会写入 run_log（说明触发方式）：
  - 触发方式：
  - degrade_reasons：
- [ ] 已新增/更新测试（列出用例）：
  - [ ] tests/____________________
- [ ] CI 通过：ruff / black / pytest
- [ ] README 或 docs 已更新（如适用）

## 证据（必须贴）
### 运行日志（至少 10 行，包含 run_id）
```text
<贴日志>
```

### DB 验证（SQL 或截图，至少 1 条）
```sql
-- 例如：当天 decision 条数
SELECT COUNT(*) FROM decision_daily WHERE trade_date='YYYYMMDD';
```

## 风险评估 / 回滚
- 可能影响：
- 回滚方式：revert commit / 回滚 tag

## 关联 Issue
- Closes #<id>
