# BriefPaws

可审计的盘前研究简报：输入美股标的 → LangGraph 四节点编排 → 工具拉行情、算指标、读 mock 新闻 → 输出 `report.md` + `run.json`（数字与证据可回溯）。

## 核心能力

- **CLI**：`briefpaws --symbols AAPL,MSFT --profile pm`；加 `--question` 切投委会备忘录
- **LangGraph**：`Supervisor → Data → Analyst → Report` 四节点
- **工具链**：yfinance 日 K（失败回退 mock）→ 6 项指标 → 隔夜窗 mock 新闻
- **落盘**：`runs/<run_id>/run.json` + `report.md`，含 `plan.steps` 四步 `done`
- **评测**：`eval/dataset.yaml` 4 case 硬断言回归

## 环境要求

- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) 或 Anaconda（推荐 Conda 管理 Python 3.11）
- 离线演示可设 `BRIEFPAWS_DATA=mock`，跳过 yfinance 联网

## 快速启动

在 **Anaconda Prompt** 或已 `conda init` 的终端中，于项目根目录 `BriefPaws/` 操作：

```bash
conda create -n briefpaws python=3.11 -y   # 首次
conda activate briefpaws

pip install -e ".[dev]"
```

```powershell
$env:BRIEFPAWS_DATA = "mock"
briefpaws --symbols AAPL,MSFT --range 3M --profile pm --out runs/
```

输出目录示例：`runs/<run_id>/run.json`、`runs/<run_id>/report.md`

> 开发时可用 `python run.py ...`；安装包后等价于 `briefpaws ...`

## CLI

| 参数 | 说明 |
|------|------|
| `--symbols` | 逗号分隔，最多 10 只 |
| `--symbol` | 单只（兼容） |
| `--range` | 默认 `3M` |
| `--profile` | `pm`（盘前简报 / 投委会 memo） |
| `--question` | 研究问题；有则切 `pm_memo` 模板 |
| `--out` | 输出目录，默认 `runs/` |

## PM 演示

```powershell
# 投委会备忘录
briefpaws --symbols AAPL,MSFT,NVDA --profile pm --question "隔夜是否有影响开盘的披露？" --out runs/

# 固定样例
python examples/pm_memo/generate_sample.py
```

详见 [examples/pm_memo/DEMO.md](./examples/pm_memo/DEMO.md)。

## 架构

LangGraph 四节点：`Supervisor → Data → Analyst → Report`（`src/briefpaws/graph/`）

- 无 `--question`：`plan_variant=pre_market_brief` + `report_pre_market.md.j2`
- 有 `--question`：`plan_variant=pm_memo` + `report_pm.md.j2`
- `run.json` 含 `plan.steps`，4 步 `status=done`
- Langfuse span 可选（无 key 时 no-op）

## 常用命令

| 目录 | 命令 | 说明 |
|------|------|------|
| 根目录 | `conda activate briefpaws` | 进入项目环境 |
| 根目录 | `pytest tests/ -q` | 全量测试（8 passed） |
| 根目录 | `pytest tests/test_pm_memo.py -v` | pm_memo 回归 |
| 根目录 | `pytest tests/test_eval_dataset.py -v` | eval 4 case 硬断言 |
| 根目录 | `pip install -e ".[dev]"` | 可编辑安装 + pytest |
| 根目录 | `pip install -e ".[dev,obs]"` | 加上 Langfuse 观测（可选） |

## 仓库结构

```
BriefPaws/
  run.py
  eval/                  # dataset.yaml + assertions.py
  examples/pm_memo/      # 投委会 demo + 固定样例
  src/briefpaws/
    cli.py
    pipeline.py          # LangGraph 入口
    graph/               # 四节点编排
    brief_logic.py       # 工具与章节逻辑
    tools/
    schemas/
    storage/
    observability/       # langfuse_tracer（可选）
  templates/             # pre_market + pm_memo
  data/news_mock.jsonl
  tests/
```

## 许可证

本项目采用 [MIT License](LICENSE)。
