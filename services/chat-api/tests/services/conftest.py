"""In-memory GridFS stand-in for Skill service tests with fake Mongo collections."""

from __future__ import annotations

import io

import pytest


class _Stream:
    def __init__(self, content: bytes, metadata: dict):
        self._content = io.BytesIO(content)
        self.metadata = metadata

    async def read(self, size: int) -> bytes:
        return self._content.read(size)


class FakeGridFSBucket:
    def __init__(self, db, *, bucket_name: str):
        assert bucket_name == 'skill_archives'
        if not hasattr(db, '_skill_archive_files'):
            db._skill_archive_files = {}
        self._files = db._skill_archive_files

    async def upload_from_stream_with_id(self, file_id, filename, source, *, metadata):
        self._files[file_id] = (source.read(), metadata)

    async def open_download_stream(self, file_id):
        content, metadata = self._files[file_id]
        return _Stream(content, metadata)

    async def delete(self, file_id):
        del self._files[file_id]


@pytest.fixture
def skill_gridfs(monkeypatch):
    from app.services.skill_packages import archive_store

    monkeypatch.setattr(archive_store, 'AsyncIOMotorGridFSBucket', FakeGridFSBucket)
