"""User-facing review comment content, separate from DOCX source anchoring."""

from __future__ import annotations

from datetime import datetime, timezone

from lxml import etree

from .source import qn


REQUIRED_COMMENT_FIELDS = ("finding", "suggested_revision", "criterion_text")


def missing_comment_fields(finding: dict) -> list[str]:
    return [key for key in REQUIRED_COMMENT_FIELDS if not str(finding.get(key) or "").strip()]


def comment_lines(finding: dict) -> list[str]:
    """Put the actionable issue first; a rule ID is never the explanation."""
    lines = [
        f"问题：{str(finding['finding']).strip()}",
        f"修改建议：{str(finding['suggested_revision']).strip()}",
        f"审核依据：{str(finding['criterion_text']).strip()}",
    ]
    reference = str(finding.get("criterion_ref") or "").strip()
    if reference:
        lines.append(f"规则编号：{reference}")
    return lines


def append_comment(comments: etree._Element, comment_id: int, finding: dict) -> None:
    comment = etree.SubElement(comments, qn("comment"))
    comment.set(qn("id"), str(comment_id))
    comment.set(qn("author"), "MOVO AI")
    comment.set(qn("date"), datetime.now(timezone.utc).isoformat(timespec="seconds"))
    paragraph = etree.SubElement(comment, qn("p"))
    for index, line in enumerate(comment_lines(finding)):
        if index:
            etree.SubElement(etree.SubElement(paragraph, qn("r")), qn("br"))
        run = etree.SubElement(paragraph, qn("r"))
        etree.SubElement(run, qn("t")).text = line[:2000]
