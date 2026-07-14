# PM / 投委会场景示例

盘前 5 分钟晨会 / 投委会备忘录 — PM 视角。

## 两种 pm 模式

| 模式 | 命令 | 模板 |
|------|------|------|
| **投委会备忘录** | 加 `--question "..."` | `report_pm.md.j2` |
| **盘前晨会简报** | 不加 question | `report_pre_market.md.j2` |

## 推荐演示命令

```bash
python run.py --symbols AAPL,MSFT,NVDA --profile pm --question "隔夜是否有影响开盘的披露？" --out runs/
```

## 固定样例

```bash
python examples/pm_memo/generate_sample.py
# → examples/pm_memo/sample/<run_id>/
```

完整演示步骤见 [DEMO.md](./DEMO.md)。

## 预期产出

- `run.json` — `meta.question`、`plan.steps` 四步、`tools` 落盘
- `report.md` — 核心观点 / 催化剂 / 异动与归因 / 证据与局限
