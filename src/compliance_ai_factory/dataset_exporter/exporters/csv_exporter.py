import csv
import json
from pathlib import Path

from compliance_ai_factory.common.models.base import DatasetSample, ExportMetadata
from compliance_ai_factory.dataset_exporter import Exporter


class CsvExporter(Exporter):
    format_name = "csv"

    def export(
        self,
        samples: list[DatasetSample],
        path: Path,
        metadata: ExportMetadata,
    ) -> Path:
        output_path = path.with_suffix(".csv") if not path.suffix else path
        fieldnames = [
            "sample_id", "scenario_id", "dataset_version", "generator",
            "industry", "company_size", "maturity", "difficulty",
            "language", "standard", "control_id", "control_title",
            "quality_score", "validation_status", "timestamp", "content_json",
        ]
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for sample in samples:
                row = sample.model_dump(mode="json")
                row["content_json"] = json.dumps(row.pop("content", {}))
                writer.writerow(row)
        return output_path
