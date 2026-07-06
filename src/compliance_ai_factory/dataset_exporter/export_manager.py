from datetime import datetime
from pathlib import Path
from typing import Any

from compliance_ai_factory.common.exceptions import ExportError
from compliance_ai_factory.common.models.base import ExportMetadata
from compliance_ai_factory.dataset_exporter import Exporter
from compliance_ai_factory.dataset_exporter.exporters import (
    CsvExporter,
    JsonExporter,
    JsonlExporter,
    MarkdownExporter,
    ParquetExporter,
)


class ExportManager:
    def __init__(self, exporters: dict[str, Exporter] | None = None):
        self.exporters = exporters or {
            "jsonl": JsonlExporter(),
            "json": JsonExporter(),
            "csv": CsvExporter(),
            "markdown": MarkdownExporter(),
            "parquet": ParquetExporter(),
        }
        self._export_history: list[dict[str, Any]] = []

    def export(
        self,
        samples: list,
        format_name: str,
        output_dir: str | Path,
        metadata: ExportMetadata | None = None,
        run_validation: bool = True,
    ) -> dict[str, Any]:
        if format_name not in self.exporters:
            raise ExportError(f"Unsupported format: {format_name}. Available: {', '.join(self.list_exporters())}")

        if run_validation:
            failed = [s for s in samples if s.validation_status.value == "failed"]
            if failed:
                raise ExportError(
                    f"Cannot export: {len(failed)} samples failed validation. "
                    f"Run validation first or set run_validation=False."
                )

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        fields = list(samples[0].model_dump(mode="json").keys()) if samples else []
        export_meta = metadata or ExportMetadata(
            version="1.0",
            generated_at=datetime.utcnow(),
            generator="export_manager",
            standard=samples[0].standard if samples else "unknown",
            sample_count=len(samples),
            fields=fields,
        )

        exporter = self.exporters[format_name]
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"export_{timestamp}_{format_name}"
        output_path = output_dir / filename
        result_path = exporter.export(samples, output_path, export_meta)

        history_entry = {
            "id": f"EXP-{len(self._export_history) + 1:04d}",
            "format": format_name,
            "samples": len(samples),
            "status": "completed",
            "date": datetime.utcnow().isoformat(),
            "path": str(result_path),
        }
        self._export_history.append(history_entry)

        return {
            "export_id": history_entry["id"],
            "format": format_name,
            "sample_count": len(samples),
            "path": str(result_path),
            "metadata": export_meta.model_dump(mode="json"),
        }

    def list_exporters(self) -> list[str]:
        return list(self.exporters.keys())

    def get_history(self) -> list[dict[str, Any]]:
        return list(self._export_history)
