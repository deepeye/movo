"""Deterministic, pre-model topic admission for organization chat turns."""

from __future__ import annotations

from typing import Any

from app.core.db import get_db
from app.product.extensions import get_product_extension
from app.utils.topic_matcher import matching_rule


COLLECTION = "topic_admission_policies"


class TopicAdmissionDenied(PermissionError):
    """The organization's current topic mode rejects this turn."""


async def require_topic(*, main_id: str, user_id: str, text: str) -> None:
    allowed, _matched_rule_id = await evaluate_topic(main_id=main_id, user_id=user_id, text=text)
    if not allowed:
        raise TopicAdmissionDenied("当前任务被准入规则拦截，请联系管理员。")


async def evaluate_topic(*, main_id: str, user_id: str, text: str) -> tuple[bool, str | None]:
    policy = await get_db()[COLLECTION].find_one({"main_id": main_id}, {"mode": 1, "rules": 1})
    mode = str((policy or {}).get("mode") or "off")
    if mode == "off":
        return True, None
    rules = [rule for rule in (policy or {}).get("rules") or [] if rule.get("enabled", True)]
    audience_policy = get_product_extension().topic_rule_audience_policy
    if audience_policy is not None:
        rules = await audience_policy.filter_rules(main_id=main_id, user_id=user_id, rules=rules)
    matched = matching_rule(text, rules)
    if mode == "denylist":
        return matched is None, str(matched.get("id")) if matched else None
    if mode == "allowlist":
        return matched is not None, str(matched.get("id")) if matched else None
    return False, None
