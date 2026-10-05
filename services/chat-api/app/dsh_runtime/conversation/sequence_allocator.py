"""Reserve per-conversation message sequence numbers on MongoDB 4.0+."""

from __future__ import annotations

from typing import Any

from pymongo import ReturnDocument


async def reserve_message_sequence(sessions: Any, query: dict[str, Any], legacy_max_seq: int) -> dict[str, Any] | None:
    # A legacy writer may have advanced chat_messages.seq without updating the
    # session counter. $max seeds the floor; $inc then reserves one unique seq.
    # Both operators are atomic, and neither requires update pipelines (4.2+).
    await sessions.update_one(query, {"$max": {"next_message_seq": legacy_max_seq}})
    return await sessions.find_one_and_update(
        query,
        {"$inc": {"next_message_seq": 1}},
        return_document=ReturnDocument.AFTER,
    )
