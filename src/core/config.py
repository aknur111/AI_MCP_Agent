from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Application settings read from environment variables."""

    log_level: str
    products_json_path: Path
    mcp_products_server_path: Path

    @staticmethod
    def from_env() -> "Settings":
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        products_json_path = Path(
            os.getenv(
                "PRODUCTS_JSON_PATH",
                str(Path(__file__).resolve().parents[2] / "entrypoints/mcp_products_server/data/products.json"),
            )
        )
        mcp_products_server_path = Path(
            os.getenv(
                "MCP_PRODUCTS_SERVER_PATH",
                str(Path(__file__).resolve().parents[2] / "entrypoints/mcp_products_server/server.py"),
            )
        )
        return Settings(
            log_level=log_level,
            products_json_path=products_json_path,
            mcp_products_server_path=mcp_products_server_path,
        )
