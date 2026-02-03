from __future__ import annotations

from typing import Any


def unwrap_call_tool_result(result: Any) -> Any:
    sc = getattr(result, "structured_content", None)
    if isinstance(sc, dict):
        if "result" in sc:
            return sc["result"]
        return sc
    return result
