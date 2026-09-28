"""Render review-check guidance without introducing a fixed workflow executor."""

from __future__ import annotations

from typing import Any


def review_check_guidance(config: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    subject = str(config.get("reviewSubject") or "").strip()
    criteria = str(config.get("reviewCriteria") or "").strip()
    if subject:
        lines.append(f"检查对象：{subject}")
    if criteria:
        lines.append(f"判定依据：{criteria}")
    lines.append("先识别审核对象与依据材料的适用主体、交易角色和适用范围；若规则只覆盖某一角色而当前材料不匹配，先说明不匹配，不得机械套用该角色的规则或生成确定性批注。")
    lines.append("逐项审核并输出结论与简要依据；无法判断时写明无法确认，不得视为通过。")
    lines.append("审核结论、问题描述和修改建议使用当前用户请求的语言；引用原文与规则时保留来源文字，不要擅自翻译引文。")
    output_mode = str(config.get("outputMode") or "report")
    if output_mode in {"annotated_docx", "both"}:
        lines.extend([
            "输出方式包含原文批注：仅对可读取的 DOCX 原件使用批注；其他格式生成独立审核报告，并明确说明未生成批注。",
            "对 DOCX 先调用 document_review_source 读取所有原文块，按 next_offset 续读到 has_more=false。审核结论须包含原文块 ID 和逐字短引，不得编造引文或位置。",
            "审核后调用 document_annotate，传入同一用户上传文件、读取工具返回的 source_sha256 和逐项问题；每项必须填写原文块 ID、逐字短引、具体问题、可执行的修改建议和适用规则的实际要求（criterion_text）。规则编号或标题只可作为 criterion_ref 辅助标识，不能代替规则内容。不得编造规则文字。",
            "交付 document_annotate 返回的原文批注副本 artifact；不得把解析所得 Markdown 重新生成 Word 作为批注文件。",
            "批注工具只会写入经原文件验证且唯一定位的引文；将 unlocated 中的意见单独告知用户，不得声称其已批注。若没有任何可定位意见，改为审核报告。",
        ])
    if output_mode == "annotated_docx":
        lines.append("已有批注副本时，后续内容生成或导出步骤不再另造一份审核报告；除非用户另行要求。")
    if output_mode == "both":
        lines.append("除原文批注副本外，还应交付完整独立审核报告；两份结果必须使用同一批审核结论。")
    return lines
