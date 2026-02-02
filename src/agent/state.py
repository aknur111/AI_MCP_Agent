from __future__ import annotations

from typing import Any, Optional
from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    query: str
    intent: str
    args: dict[str, Any]
    answer: str
    error: Optional[str]
