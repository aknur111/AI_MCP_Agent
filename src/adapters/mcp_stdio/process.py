from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict


@dataclass(frozen=True)
class MCPStdioConfig:
    server_path: Path
    keep_alive: bool = True
    cwd: Optional[Path] = None
    env: Optional[Dict[str, str]] = None

    def _project_root(self) -> Path:
        return (self.cwd or Path.cwd()).resolve()

    def _build_env(self, project_root: Path) -> Dict[str, str]:
        merged = os.environ.copy()
        if self.env:
            merged.update(self.env)

        existing_pp = merged.get("PYTHONPATH", "")
        parts = [p for p in existing_pp.split(os.pathsep) if p]

        root_str = str(project_root)
        if root_str not in parts:
            parts.insert(0, root_str)

        merged["PYTHONPATH"] = os.pathsep.join(parts)
        return merged

    def to_transport(self):
        from fastmcp.client.transports import StdioTransport

        server_path = self.server_path.resolve()
        project_root = self._project_root()

        if not server_path.exists():
            raise FileNotFoundError(f"MCP server script not found: {server_path}")

        env = self._build_env(project_root)

        return StdioTransport(
            command=sys.executable,
            args=[str(server_path)],
            env=env,
            cwd=str(project_root),
            keep_alive=self.keep_alive,
        )
