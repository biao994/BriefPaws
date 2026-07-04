# BriefPaws

可审计的盘前研究简报：输入美股标的 → LangGraph 四节点编排 → 工具拉行情、算指标、读 mock 新闻 → 输出 `report.md` + `run.json`（数字与证据可回溯）。

## 核心能力

- **CLI**：`briefpaws --symbols AAPL,MSFT --profile pm`
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
| `--profile` | `pm`（盘前简报） |
| `--out` | 输出目录，默认 `runs/` |

## 架构

LangGraph 四节点：`Supervisor → Data → Analyst → Report`（`src/briefpaws/graph/`）

- `run.json` 含 `plan.steps`，4 步 `status=done`
- Langfuse span 可选（无 key 时 no-op）

## 常用命令

| 目录 | 命令 | 说明 |
|------|------|------|
| 根目录 | `conda activate briefpaws` | 进入项目环境 |
| 根目录 | `pytest tests/ -q` | 全量测试（7 passed） |
| 根目录 | `pytest tests/test_eval_dataset.py -v` | eval 4 case 硬断言 |
| 根目录 | `pip install -e ".[dev]"` | 可编辑安装 + pytest |

## 仓库结构

```
BriefPaws/
  run.py
  eval/                  # dataset.yaml + assertions.py
  src/briefpaws/
    cli.py
    pipeline.py          # LangGraph 入口
    graph/               # 四节点编排
    brief_logic.py       # 工具与章节逻辑
    tools/
    schemas/
    storage/
    observability/       # Langfuse stub
  templates/
  data/news_mock.jsonl
  tests/
```

## 许可证

本项目采用 [MIT License](LICENSE)。
