"""运行时配置的唯一来源。"""

from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
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
