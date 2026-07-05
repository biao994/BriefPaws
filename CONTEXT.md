# BriefPaws MVP 决策摘要

## Q1 用户与场景

买方 PM/研究员；盘前 5 分钟晨会；输入行情+隔夜新闻→1 页 Markdown 简报；用于沟通与关注/风控。**简报不含交易指令、不构成投资建议**（见 Q6）。

## Q2 范围

- 市场：美股（yfinance）
- 数量：≤10 只 / run（`MAX_SYMBOLS`）
- 时区：**Asia/Shanghai**；隔夜窗 = 当地 **T-1 16:00 ~ T 09:00**（近似覆盖美股收盘后～盘前，非精确 ET 映射）
- 指标：行情技术 + 风险（6 条固定，见 Q5）

## Q3 新闻与证据
- 白名单：SEC / IR / PR Newswire / Finnhub（MVP mock）
- 证据粒度 A：URL + 标题 + 时间
- 冲突：filing/official > aggregator；**aggregator/unknown 不进事件与 trigger**；`run.json` 保留 `evidence_level` 供审计

## Q4 模板

- Markdown；总览 + 10 只合页（**目标：总览 ≤200 字、单只 ≤300 字**，盘前 5min 可读）
- 每只：结论1句、快照≤6、事件≤3、关注≤3、触发≤2、不足≤2

## Q5 指标口径
Adj Close 日频；3M收益、20D年化波动、3M MDD、隔夜跳空、成交量比、近20D最差单日。

## Q6 Triggers
规则+官方事件；禁止交易指令；格式「若…→则…（证据：…）」。

## 工程默认（Q7）

- 一次 run 多标的 merge；单只失败 skip，整体 **degraded 仍可交付**
- degraded：`run.json` → `meta.status=degraded`；报告首行展示 **状态**（见 `templates/report_pre_market.md.j2`）
- CLI：`--symbols` 逗号分隔；**`--profile pm`（MVP 仅 pm，CLI 锁死）**；可选 `--question` 触发 pm_memo
