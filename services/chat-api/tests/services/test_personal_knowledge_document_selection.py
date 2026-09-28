from __future__ import annotations

import asyncio

import pytest

from app.services.personal_knowledge import document_selection as selection


class AggregateCursor:
    def __init__(self, result):
        self.result = result

    async def to_list(self, *, length):
        assert length == 1
        return self.result


class Grants:
    def __init__(self, result):
        self.result = result
        self.pipeline = None

    def aggregate(self, pipeline):
        self.pipeline = pipeline
        return AggregateCursor(self.result)


class Db:
    def __init__(self, result):
        self.resource_grants = Grants(result)

    def __getitem__(self, name):
        return getattr(self, name)


def test_shared_selection_pages_without_a_grant_count_cap(monkeypatch):
    resource = {
        "_id": "document-1001", "main_id": "tenant", "owner_user_id": "owner",
        "name": "审核规则", "status": "indexed", "active_document_id": "parsed-1001",
        "deleted_at": None,
    }
    db = Db([{"items": [{"resource": resource, "status": "active"}], "count": [{"total": 1501}]}])
    monkeypatch.setattr(selection, "get_db", lambda: db)

    async def attach_people(self, main_id, items):
        assert main_id == "tenant"

    monkeypatch.setattr(selection.PersonalKnowledgeService, "_attach_people", attach_people)
    result = asyncio.run(selection.search_selectable_documents(
        main_id="tenant", user_id="recipient", view="shared", directory_id="all",
        keyword="合同.*", page=51, page_size=20,
    ))

    assert result["total"] == 1501
    assert result["items"][0]["id"] == "document-1001"
    assert result["items"][0]["activeDocumentId"] == "parsed-1001"
    assert db.resource_grants.pipeline[0]["$match"]["recipient_user_id"] == "recipient"
    assert db.resource_grants.pipeline[0]["$match"]["main_id"] == "tenant"
    keyword_match = db.resource_grants.pipeline[3]["$match"]["$or"]
    assert keyword_match[0]["resource.name"]["$regex"] == r"合同\.\*"
    assert db.resource_grants.pipeline[-1]["$facet"]["items"] == [{"$skip": 1000}, {"$limit": 20}]


def test_selection_rejects_unparsed_document(monkeypatch):
    class Access:
        resource = {"status": "pending_parse", "active_document_id": "", "deleted_at": None}
        grant = None

    async def require_view(self, **kwargs):
        return Access()

    monkeypatch.setattr(selection.PersonalKnowledgeAccessService, "require_view", require_view)
    with pytest.raises(LookupError, match="knowledge_document_not_ready"):
        asyncio.run(selection.selectable_document(
            main_id="tenant", user_id="user", resource_id="document",
        ))


def test_workflow_binding_requires_current_document_access(monkeypatch):
    checked = []

    async def selectable_document(**kwargs):
        checked.append(kwargs)
        raise PermissionError("knowledge_forbidden")

    monkeypatch.setattr(selection, "selectable_document", selectable_document)
    node = {"type": "read_material", "businessConfig": {
        "sourceType": "knowledge_document", "knowledgeScope": "personal",
        "knowledgeSourceId": "revoked-document",
    }}
    with pytest.raises(PermissionError, match="knowledge_forbidden"):
        asyncio.run(selection.validate_personal_workflow_documents(
            main_id="tenant", user_id="editor", nodes=[node],
        ))
    assert checked == [{
        "main_id": "tenant", "user_id": "editor", "resource_id": "revoked-document",
    }]
