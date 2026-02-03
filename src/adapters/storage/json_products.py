from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.domain.models import Product


class JsonProductsStorage:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> list[Product]:
        if not self.path.exists():
            return []
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return [Product.model_validate(item) for item in raw]

    def save(self, products: list[Product]) -> None:
        payload: list[dict[str, Any]] = [p.model_dump() for p in products]
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
