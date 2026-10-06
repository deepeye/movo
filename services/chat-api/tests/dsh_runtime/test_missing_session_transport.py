from __future__ import annotations

import asyncio

import httpx
import pytest

from app.dsh_runtime.errors import DshSessionMissingError, DshTransportError
from app.dsh_runtime.transport import HttpKernelHostTransport


def test_only_definitive_resume_miss_is_recoverable() -> None:
    async def run() -> None:
        def respond(request: httpx.Request) -> httpx.Response:
            return httpx.Response(400, json={
                "error": {"code": "kernel_request_failed", "message": 'session "dsh-lost" not found'}
            })

        transport = HttpKernelHostTransport("http://localhost")
        await transport.close()
        transport._client = httpx.AsyncClient(
            base_url="http://localhost", transport=httpx.MockTransport(respond)
        )
        try:
            with pytest.raises(DshSessionMissingError):
                await transport.request("POST", "/v1/runtimes/runtime/sessions/dsh-lost/resume")
            with pytest.raises(DshTransportError) as other:
                await transport.request("POST", "/v1/runtimes/runtime/sessions/dsh-lost/send")
            assert not isinstance(other.value, DshSessionMissingError)
        finally:
            await transport.close()

    asyncio.run(run())
