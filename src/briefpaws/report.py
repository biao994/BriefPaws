"""从 Jinja2 模板渲染 report.md。"""

from __future__ import annotations

from jinja2 import Environment, FileSystemLoader, select_autoescape

from briefpaws.brief_logic import analyst_sections
from briefpaws.config import TEMPLATES_DIR
from briefpaws.schemas.run import RunDocument


def render_report(doc: RunDocument, *, sections: dict | None = None) -> str:
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(disabled_extensions=()),
    )
    template_name = "report_pre_market.md.j2"
    if doc.meta.profile == "quant":
        template_name = "report_quant.md.j2"
    elif doc.meta.profile == "pm" and doc.meta.plan_variant == "pm_memo":
        template_name = "report_pm.md.j2"
    if sections is None:
        sections, _ = analyst_sections(doc)
    tpl = env.get_template(template_name)
    ctx = {
        "meta": doc.meta.model_dump(),
        "sections": sections,
        "hypothesis": doc.hypothesis.model_dump() if doc.hypothesis else None,
        "reflection": doc.reflection.model_dump() if doc.reflection else None,
    }
    body = tpl.render(**ctx)
    if doc.meta.status == "degraded" and doc.meta.degraded_reason:
        banner = f"<!-- DEGRADED: {doc.meta.degraded_reason} -->\n\n"
        return banner + body
    return body
