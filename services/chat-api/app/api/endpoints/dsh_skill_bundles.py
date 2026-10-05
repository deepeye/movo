"""Private, streamed Skill archive delivery to the MOVO DSH host adapter."""

from __future__ import annotations

import hmac
import re

from fastapi import APIRouter, Header, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from starlette.responses import StreamingResponse

from app.core.config import get_settings
from app.core.db import get_db
from app.services.skill_packages.archive_store import BUCKET_NAME, MAX_ARCHIVE_BYTES


router = APIRouter(prefix="/internal/dsh/skill-bundles", tags=["dsh-internal"])
FILE_ID = re.compile(r"^[0-9a-f]{32}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")


@router.get("/{file_id}")
async def download(file_id: str, request: Request, digest: str, authorization: str = Header(default="")):
    secret = str(get_settings().DSH_RUNTIME_HOST_TOKEN or "")
    if secret:
        if not hmac.compare_digest(authorization, f"Bearer {secret}"):
            raise HTTPException(status_code=401, detail="Invalid DSH host credential")
    elif not request.client or request.client.host not in {"127.0.0.1", "::1"}:
        raise HTTPException(status_code=401, detail="DSH host credential is required")
    if not FILE_ID.fullmatch(file_id) or not DIGEST.fullmatch(digest):
        raise HTTPException(status_code=404, detail="Skill archive not found")

    db = get_db()
    record = await db[f"{BUCKET_NAME}.files"].find_one({"_id": file_id})
    if not record or int(record.get("length") or 0) > MAX_ARCHIVE_BYTES:
        raise HTTPException(status_code=404, detail="Skill archive not found")
    if (record.get("metadata") or {}).get("digest") != digest:
        raise HTTPException(status_code=404, detail="Skill archive not found")
    stream = await AsyncIOMotorGridFSBucket(db, bucket_name=BUCKET_NAME).open_download_stream(file_id)

    async def chunks():
        while chunk := await stream.read(1024 * 1024):
            yield chunk

    return StreamingResponse(chunks(), media_type="application/zip")
