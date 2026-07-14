# PM 演示脚本（约 1 分钟）

## 1. 安装

```powershell
cd briefpaws
pip install -e ".[dev]"
```

## 2. 投委会备忘录（带研究问题）

```powershell
python run.py --symbols AAPL,MSFT,NVDA --profile pm --question "隔夜是否有影响开盘的披露？" --out runs/
```

检查输出目录：

- `runs/<run_id>/run.json` → `meta.question`、`plan.steps`、`symbols[].news`
- `runs/<run_id>/report.md` → 章节 **核心观点 / 催化剂 / 异动与归因 / 证据与局限**

## 3. 盘前晨会（无 question，轻量模板）

```powershell
python run.py --symbols AAPL,MSFT --profile pm --out runs/
```

使用 `report_pre_market.md.j2`（总览 + 分标的快照）。

## 4. 固定样例（可离线展示）

```powershell
python examples/pm_memo/generate_sample.py
```

产出：`examples/pm_memo/sample/<run_id>/`

## 5. 回归

```powershell
pytest tests/ -q
```
