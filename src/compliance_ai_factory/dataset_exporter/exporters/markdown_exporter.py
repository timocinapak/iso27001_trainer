from pathlib import Path

from compliance_ai_factory.common.models.base import DatasetSample, ExportMetadata
from compliance_ai_factory.dataset_exporter import Exporter


class MarkdownExporter(Exporter):
    format_name = "markdown"

    def export(
        self,
        samples: list[DatasetSample],
        path: Path,
        metadata: ExportMetadata,
    ) -> Path:
        output_path = path.with_suffix(".md") if not path.suffix else path
        lines: list[str] = []
        lines.append(f"# Dataset Export: {metadata.standard}")
        lines.append("")
        lines.append(f"**Generated:** {metadata.generated_at.isoformat()}")
        lines.append(f"**Version:** {metadata.version}")
        lines.append(f"**Generator:** {metadata.generator}")
        lines.append(f"**Sample Count:** {metadata.sample_count}")
        lines.append(f"**Fields:** {', '.join(metadata.fields)}")
        lines.append("")
        lines.append("---")
        lines.append("")

        for i, sample in enumerate(samples, 1):
            lines.append(f"## Sample {i}: {sample.sample_id}")
            lines.append("")
            lines.append(f"- **Control:** {sample.control_id} — {sample.control_title}")
            lines.append(f"- **Generator:** {sample.generator}")
            lines.append(f"- **Industry:** {sample.industry} | **Size:** {sample.company_size}")
            lines.append(f"- **Maturity:** {sample.maturity} | **Difficulty:** {sample.difficulty}")
            lines.append(f"- **Validation:** {sample.validation_status.value}")
            if sample.quality_score is not None:
                lines.append(f"- **Quality Score:** {sample.quality_score}")
            lines.append("")
            lines.append("### Content")
            lines.append("")
            for key, value in sample.content.items():
                if isinstance(value, str):
                    lines.append(f"**{key}:** {value}")
                    lines.append("")
                elif isinstance(value, list):
                    lines.append(f"**{key}:**")
                    for item in value:
                        if isinstance(item, dict):
                            for k, v in item.items():
                                lines.append(f"- *{k}:* {v}")
                        else:
                            lines.append(f"- {item}")
                    lines.append("")
                else:
                    lines.append(f"**{key}:** {value}")
                    lines.append("")
            lines.append("---")
            lines.append("")

        with open(output_path, "w") as f:
            f.write("\n".join(lines))
        return output_path
