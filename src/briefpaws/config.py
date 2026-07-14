"""运行时配置的唯一来源。"""

from pathlib import Path

DEFAULT_LLM_MODEL = "deepseek-v4-pro"
LLM_TIMEOUT_S = 60
LLM_TEMPERATURE = 0.2

PACKAGE_ROOT = Path(__file__).resolve().parents[2]

def load_env(*, override: bool = False) -> None:
    """从仓库根 `.env` 灌入 os.environ；无文件或未装 python-dotenv 则跳过。"""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    env_path = PACKAGE_ROOT / ".env"
    if env_path.is_file():
        load_dotenv(env_path, override=override)


load_env()

DATA_DIR = PACKAGE_ROOT / "data"
TEMPLATES_DIR = PACKAGE_ROOT / "templates"
DEFAULT_OUT_DIR = PACKAGE_ROOT / "runs"

MAX_SYMBOLS = 10
DEFAULT_RANGE = "3M"
DEFAULT_PROFILE = "pm"
DEFAULT_TIMEZONE = "Asia/Shanghai"

GAP_SIGMA_MULT = 2.0
VOLUME_SPIKE_MULT = 3.0
VOLUME_DRY_MULT = 0.3

EVIDENCE_INSUFFICIENT_PM = (
    "当前检索范围内未发现足够新闻/公告证据，以下归因仅作假设性讨论，不构成投资结论。"
)
