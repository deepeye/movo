"""Real-Mongo coverage for the opt-in, stopped-writer sequence repair."""

from __future__ import annotations

from datetime import datetime, timedelta

from bson import ObjectId
from pymongo import MongoClient

from app.migrations.sequence_repair import _affected_sessions, _repair_session, main


def test_direct_repair_requires_stopped_writer_flag(monkeypatch):
    monkeypatch.delenv("MOVO_SESSION_FIX_WRITES_STOPPED", raising=False)
    assert main() == 2


def test_repair_preserves_messages_and_remaps_references(real_mongo_db):
    harness = real_mongo_db
    session_id = ObjectId()
    now = datetime.utcnow()
    client = MongoClient(harness.uri)
    db = client[harness.name]
    try:
        db.chat_sessions.insert_one({"_id": session_id, "main_id": "tenant", "next_message_seq": 2})
        db.chat_messages.insert_many([
            {"main_id": "tenant", "session_id": session_id, "seq": 1, "content": "first", "created_at": now},
            {"main_id": "tenant", "session_id": session_id, "seq": 1, "content": "second", "created_at": now + timedelta(seconds=1)},
            {"main_id": "tenant", "session_id": session_id, "seq": 2, "content": "summary", "created_at": now + timedelta(seconds=2), "covers": {"start_seq": 1, "end_seq": 1}},
        ])
        db.session_participants.insert_one({
            "main_id": "tenant", "conversation_id": str(session_id),
            "user_id": "reader", "last_read_seq": 1,
        })
        original_ids = {row["_id"] for row in db.chat_messages.find({})}
        assert len(_affected_sessions(db)) == 1

        assert _repair_session(db, main_id="tenant", session_id=session_id) == 3

        rows = list(db.chat_messages.find({"session_id": session_id}).sort("seq", 1))
        assert [row["content"] for row in rows] == ["first", "second", "summary"]
        assert [row["seq"] for row in rows] == [1, 2, 3]
        assert {row["_id"] for row in rows} == original_ids
        assert rows[2]["covers"] == {"start_seq": 1, "end_seq": 2}
        assert db.chat_sessions.find_one({"_id": session_id})["next_message_seq"] == 3
        assert db.session_participants.find_one({"user_id": "reader"})["last_read_seq"] == 2
        assert not _affected_sessions(db)
    finally:
        client.close()
