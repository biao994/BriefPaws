"""OpenAI 兼容 LLM 客户端；可选，无 API key 时规则回退。"""

from __future__ import annotations

import json
import os
import re

from briefpaws.config import DEFAULT_LLM_MODEL, LLM_TEMPERATURE, LLM_TIMEOUT_S


def llm_enabled() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY", "").strip())


def _model_id() -> str:
    raw = (os.environ.get("OPENAI_MODEL", "") or DEFAULT_LLM_MODEL).strip()
    if raw.startswith("openai:"):
        return raw.split(":", 1)[1]
    return raw


def chat_text(*, system: str, user: str) -> tuple[str | None, str | None]:
    """返回 (text, error)；成功时 error 为 None。"""
    if not llm_enabled():
        return None, "LLM_DISABLED"

    try:
        from openai import OpenAI

        kwargs: dict = {"timeout": LLM_TIMEOUT_S}
        base_url = os.environ.get("OPENAI_BASE_URL", "").strip()
        if base_url:
            kwargs["base_url"] = base_url
        client = OpenAI(**kwargs)
        resp = client.chat.completions.create(
            model=_model_id(),
            temperature=LLM_TEMPERATURE,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        text = (resp.choices[0].message.content or "").strip()
        return text or None, None
    except Exception as exc:
        return None, str(exc)[:200]


def chat_json(*, system: str, user: str) -> tuple[dict | None, str | None]:
    text, err = chat_text(system=system, user=user)
    if err:
        return None, err
    if not text:
        return None, "EMPTY_RESPONSE"
    # 去掉 markdown 代码围栏（若有）
    cleaned = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", cleaned, re.DOTALL)
    if fence:
        cleaned = fence.group(1).strip()
    try:
        return json.loads(cleaned), None
    except json.JSONDecodeError:
        return None, "INVALID_JSON"
