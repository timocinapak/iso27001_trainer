import json
from pathlib import Path

from compliance_ai_factory.common.exceptions import ExportError
from compliance_ai_factory.common.models.base import DatasetSample, ExportMetadata
from compliance_ai_factory.dataset_exporter import Exporter


class ParquetExporter(Exporter):
    format_name = "parquet"

    def export(
        self,
        samples: list[DatasetSample],
        path: Path,
        metadata: ExportMetadata,
    ) -> Path:
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
        except ImportError:
            raise ExportError(
                "pyarrow is required for Parquet export. "
                "Install with: pip install compliance_ai_factory[parquet]"
            )

        output_path = path.with_suffix(".parquet") if not path.suffix else path
        rows = []
        for sample in samples:
            row = sample.model_dump(mode="json")
            row["content_json"] = json.dumps(row.pop("content", {}))
            rows.append(row)

        table = pa.Table.from_pylist(rows)
        pq.write_table(table, output_path)
        return output_path
