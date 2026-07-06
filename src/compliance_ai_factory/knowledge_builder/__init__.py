"""
Module 1: Compliance Knowledge Builder

Converts compliance documents (PDF, Markdown, DOCX, HTML, XML, JSON)
into structured machine-readable Knowledge Packs.

Knowledge Builder NEVER generates datasets.
Knowledge Builder ONLY extracts knowledge.
"""

from abc import ABC, abstractmethod
from pathlib import Path

from compliance_ai_factory.knowledge_pack.models import KnowledgePack


class DocumentParser(ABC):
    @abstractmethod
    def parse(self, path: Path) -> str:
        ...


class KnowledgeBuilder(ABC):
    @abstractmethod
    def build(self, source: Path, output: Path) -> KnowledgePack:
        ...


__all__ = [
    "DocumentParser",
    "KnowledgeBuilder",
]
