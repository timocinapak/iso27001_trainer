import json
from pathlib import Path

from compliance_ai_factory.common.models.base import DatasetSample, ExportMetadata
from compliance_ai_factory.dataset_exporter import Exporter


class JsonlExporter(Exporter):
    format_name = "jsonl"

    def export(
        self,
        samples: list[DatasetSample],
        path: Path,
        metadata: ExportMetadata,
    ) -> Path:
        output_path = path.with_suffix(".jsonl") if not path.suffix else path
        with open(output_path, "w") as f:
            for sample in samples:
                line = sample.model_dump(mode="json")
                line["_export_metadata"] = metadata.model_dump(mode="json")
                f.write(json.dumps(line) + "\n")
        return output_path
