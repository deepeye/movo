"""Upgrade contract: old data survives and unsafe upgrades stop before deploy."""

from __future__ import annotations

import pytest
from bson import ObjectId

from app.dsh_runtime.conversation.repository import MessageSequenceIndexConflict
from app.migrations.session_sharing import migrate


def test_migration_is_repeatable_and_preserves_legacy_messages(real_mongo_db):
    harness = real_mongo_db

    async def seed():
        await harness.db.chat_messages.insert_many([
            {"session_id": "legacy", "seq": 1, "content": "first"},
            {"session_id": "legacy", "seq": 1, "content": "second"},
        ])
        return await read_messages(harness.db)

    before = harness.run(seed())
    harness.run(migrate(harness.db))
    harness.run(migrate(harness.db))

    after = harness.run(read_messages(harness.db))
    assert after == before
    assert "unique_conversation_participant" in harness.run(
        harness.db.session_participants.index_information()
    )
    assert "unique_main_session_seq" in harness.run(
        harness.db.chat_messages.index_information()
    )


async def read_messages(db):
    return [row async for row in db.chat_messages.find({}).sort("_id", 1)]


def test_migration_never_rewrites_valid_duplicate_sequences(real_mongo_db):
    harness = real_mongo_db

    async def seed():
        session_id = ObjectId()
        await harness.db.chat_messages.insert_many([
            {"main_id": "tenant", "session_id": session_id, "seq": 1,
             "message_id": "one", "content": "first"},
            {"main_id": "tenant", "session_id": session_id, "seq": 1,
             "message_id": "two", "content": "second"},
        ])
        return await read_messages(harness.db)

    before = harness.run(seed())
    with pytest.raises(MessageSequenceIndexConflict):
        harness.run(migrate(harness.db))
    assert harness.run(read_messages(harness.db)) == before
