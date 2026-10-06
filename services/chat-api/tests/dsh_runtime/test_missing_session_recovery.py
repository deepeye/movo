from __future__ import annotations

import asyncio
from types import SimpleNamespace

from app.dsh_runtime.errors import DshSessionMissingError
from app.dsh_runtime.turn_recovery import TurnTerminalRecovery


def test_restart_sweep_finalizes_claim_when_resume_reports_missing_session() -> None:
    async def run() -> None:
        recovery = TurnTerminalRecovery.__new__(TurnTerminalRecovery)
        calls = []

        async def missing(_binding):
            raise DshSessionMissingError('session "dsh-lost" not found')

        async def finalize(binding, message_id):
            calls.append((binding["binding_id"], message_id))
            return True

        recovery._coordinator = SimpleNamespace(restore=missing)
        recovery._finalize_orphaned_claim = finalize
        binding = {"binding_id": "old", "active_turn": {"message_id": "message-a"}}
        assert await recovery._reconcile_claim(binding) is True
        assert calls == [("old", "message-a")]

    asyncio.run(run())


def test_turn_boundary_clears_orphaned_claim_before_rebinding() -> None:
    async def run() -> None:
        recovery = TurnTerminalRecovery.__new__(TurnTerminalRecovery)
        binding = {
            "binding_id": "old", "tenant_id": "tenant-a", "user_id": "user-a",
            "conversation_id": "conversation-a", "active_turn": {"message_id": "message-a"},
        }
        calls = []

        async def no_terminal(**_kwargs):
            return False

        async def missing(_binding):
            raise DshSessionMissingError('session "dsh-lost" not found')

        async def finalize(_binding, message_id):
            calls.append(message_id)
            return True

        async def current(*_args, **_kwargs):
            return {**binding, "active_turn": {"message_id": "message-a", "status": "failed"}}

        recovery.finalize_persisted_terminal = no_terminal
        recovery._coordinator = SimpleNamespace(restore=missing)
        recovery._finalize_orphaned_claim = finalize
        recovery._bindings = SimpleNamespace(current=current)
        repaired = await recovery.recover(binding)
        assert repaired["active_turn"]["status"] == "failed"
        assert calls == ["message-a"]

    asyncio.run(run())
