import json
from pathlib import Path

from compliance_ai_factory.common.models.base import DatasetSample, ExportMetadata
from compliance_ai_factory.dataset_exporter import Exporter


class JsonExporter(Exporter):
    format_name = "json"

    def export(
        self,
        samples: list[DatasetSample],
        path: Path,
        metadata: ExportMetadata,
    ) -> Path:
        output_path = path.with_suffix(".json") if not path.suffix else path
        data = {
            "metadata": metadata.model_dump(mode="json"),
            "samples": [s.model_dump(mode="json") for s in samples],
            "sample_count": len(samples),
        }
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        return output_path
