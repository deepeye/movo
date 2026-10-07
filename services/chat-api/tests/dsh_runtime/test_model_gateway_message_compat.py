"""DSH message-version compatibility at the MOVO model gateway boundary."""

from app.dsh_runtime.model_gateway.service import ModelGatewayRequest, ModelGatewayService
from app.llm.types import Role


def _request(messages: list[dict]) -> ModelGatewayRequest:
    return ModelGatewayRequest(
        profileVersion="profile-a",
        modelInstanceId="model-a",
        provider="askai-model-gateway",
        model="deepseek-chat",
        messages=messages,
    )


def test_v4_native_tool_result_preserves_call_id() -> None:
    messages = ModelGatewayService._messages(_request([
        {"role": "assistant", "content": [{"type": "tool-call", "id": "call-a", "name": "skill", "arguments": "{}"}]},
        {"role": "tool", "toolCallId": "call-a", "content": [{"type": "text", "text": "skill answer"}]},
    ]))

    assert messages[0].tool_calls[0]["id"] == "call-a"
    assert messages[1].role == Role.TOOL
    assert messages[1].tool_call_id == "call-a"
    assert messages[1].content == "skill answer"


def test_legacy_wrapped_tool_result_still_maps() -> None:
    messages = ModelGatewayService._messages(_request([
        {"role": "user", "content": [{"type": "tool-result", "toolCallId": "call-old", "content": [{"type": "text", "text": "old answer"}]}]},
    ]))

    assert messages[0].role == Role.TOOL
    assert messages[0].tool_call_id == "call-old"
    assert messages[0].content == "old answer"
