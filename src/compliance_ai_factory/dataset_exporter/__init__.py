"""
Module 6: Dataset Exporter

Supported formats: JSONL, JSON, CSV, Markdown, Parquet

Every exported sample includes:
  sample_id, scenario_id, dataset_version, generator, industry,
  company_size, maturity, difficulty, language, standard, control_id,
  control_title, quality_score, validation_status, timestamp
"""

from abc import ABC, abstractmethod
from pathlib import Path

from compliance_ai_factory.common.models.base import DatasetSample, ExportMetadata


class Exporter(ABC):
    format_name: str

    @abstractmethod
    def export(
        self,
        samples: list[DatasetSample],
        path: Path,
        metadata: ExportMetadata,
    ) -> Path:
        ...


__all__ = [
    "Exporter",
]
