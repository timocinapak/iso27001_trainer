import json
from pathlib import Path

from compliance_ai_factory.common.exceptions import (
    KnowledgePackNotFoundError,
    KnowledgePackValidationError,
)
from compliance_ai_factory.knowledge_pack.models import KnowledgePack


class KnowledgePackLoader:
    LOAD_ORDER = [
        "metadata",
        "controls",
        "terminology",
        "glossary",
        "evidence",
        "reasoning",
        "cross_references",
        "maturity",
        "industries",
    ]

    def __init__(self, base_path: str | Path) -> None:
        self.base_path = Path(base_path)

    def load(self) -> KnowledgePack:
        if not self.base_path.exists():
            raise KnowledgePackNotFoundError(
                f"Knowledge Pack not found at {self.base_path}"
            )

        self._validate_structure()

        data: dict = {}
        for name in self.LOAD_ORDER:
            file_path = self.base_path / f"{name}.json"
            if file_path.exists():
                with open(file_path) as f:
                    data[name] = json.load(f)

        return KnowledgePack(**data)

    def _validate_structure(self) -> None:
        required = {"metadata.json", "controls.json"}
        existing = {f.name for f in self.base_path.iterdir() if f.is_file()}
        missing = required - existing
        if missing:
            raise KnowledgePackValidationError(
                f"Knowledge Pack missing required files: {missing}"
            )

    def list_available(self) -> list[str]:
        knowledge_dir = self.base_path.parent
        if not knowledge_dir.exists():
            return []
        return sorted(
            d.name
            for d in knowledge_dir.iterdir()
            if d.is_dir() and (d / "metadata.json").exists()
        )
