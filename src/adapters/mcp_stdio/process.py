from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
import os

from fastmcp.client.transports import StdioTransport


@dataclass(frozen=True)
class MCPStdioConfig:
    server_path: Path
    keep_alive: bool = True
    cwd: Path | None = None
    env: dict[str, str] | None = None

    def to_transport(self) -> StdioTransport:
        server_path = self.server_path.resolve()
        project_root = (self.cwd or Path.cwd()).resolve()

        env = dict(self.env or {})
        env.setdefault("PYTHONPATH", str(project_root))

        return StdioTransport(
            command=sys.executable,
            args=[str(server_path)],
            env=env,
            cwd=str(project_root),
            keep_alive=self.keep_alive,
        )
