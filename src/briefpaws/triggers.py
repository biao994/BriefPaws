"""规则触发器 — 不含交易指令。"""

from __future__ import annotations

from briefpaws.schemas.run import Indicators, NewsItem, Trigger


def build_triggers(ind: Indicators | None, news: list[NewsItem]) -> list[Trigger]:
    out: list[Trigger] = []
    if ind is None:
        return out

    if ind.overnight_gap is not None and ind.overnight_gap_significant:
        direction = "上行" if ind.overnight_gap > 0 else "下行"
        out.append(
            Trigger(
                text=(
                    f"若 |隔夜跳空|>2σ（{direction}）且需核对事件真伪与流动性 "
                    f"→ 则盘前重点核实新闻/公告并纳入风险清单"
                ),
                evidence="overnight_gap / vol_20d_ann",
            )
        )
    elif ind.volume_flag == "spike" and ind.volume_ratio_20d:
        out.append(
            Trigger(
                text=(
                    f"若 成交量/20日均量>{ind.volume_ratio_20d:.1f}x "
                    f"→ 则关注放量是否由已知事件驱动并核实来源"
                ),
                evidence="volume_ratio_20d",
            )
        )

    official = [n for n in news if n.evidence_level in ("filing", "official")]
    if len(out) < 2 and official:
        n = official[0]
        out.append(
            Trigger(
                text=f"若 官方披露「{n.title[:40]}…」被证实 → 则更新假设并纳入今日关注清单",
                evidence=n.url,
            )
        )
    return out[:2]
