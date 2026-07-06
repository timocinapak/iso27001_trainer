from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import datetime

from compliance_ai_factory.scenario_generator.generator import ConcreteScenarioGenerator
from compliance_ai_factory.knowledge_pack.loader import KnowledgePackLoader
from compliance_ai_factory.dataset_generator.pipeline import ConcreteDatasetGeneratorPipeline
from compliance_ai_factory.dataset_exporter.exporters import (
    JsonlExporter,
    JsonExporter,
    CsvExporter,
    MarkdownExporter,
)
from compliance_ai_factory.dataset_exporter.export_manager import ExportManager
from compliance_ai_factory.common.models.base import ExportMetadata


KNOWLEDGE_DIR = Path(__file__).parents[2] / "knowledge" / "iso27001"


class TestExporters:
    def setup_method(self):
        self.generator = ConcreteScenarioGenerator()
        self.scenario = self.generator.generate(seed=42)
        loader = KnowledgePackLoader(KNOWLEDGE_DIR)
        self.pack = loader.load()
        pipeline = ConcreteDatasetGeneratorPipeline()
        self.samples = pipeline.run(self.scenario, self.pack)
        self.metadata = ExportMetadata(
            version="1.0",
            generated_at=datetime.utcnow(),
            generator="test",
            standard="ISO/IEC 27001",
            sample_count=len(self.samples),
            fields=["sample_id", "scenario_id", "generator", "industry", "content"],
        )

    def test_jsonl_exporter(self):
        with TemporaryDirectory() as tmp:
            exporter = JsonlExporter()
            out = exporter.export(self.samples[:3], Path(tmp) / "test.jsonl", self.metadata)
            assert out.exists()
            content = out.read_text()
            assert content.count("\n") == 3

    def test_json_exporter(self):
        with TemporaryDirectory() as tmp:
            exporter = JsonExporter()
            out = exporter.export(self.samples[:3], Path(tmp) / "test.json", self.metadata)
            assert out.exists()
            import json
            data = json.loads(out.read_text())
            assert "metadata" in data
            assert "samples" in data
            assert len(data["samples"]) == 3

    def test_csv_exporter(self):
        with TemporaryDirectory() as tmp:
            exporter = CsvExporter()
            out = exporter.export(self.samples[:3], Path(tmp) / "test.csv", self.metadata)
            assert out.exists()
            content = out.read_text()
            assert "sample_id" in content
            assert content.count("\n") == 4

    def test_markdown_exporter(self):
        with TemporaryDirectory() as tmp:
            exporter = MarkdownExporter()
            out = exporter.export(self.samples[:2], Path(tmp) / "test.md", self.metadata)
            assert out.exists()
            content = out.read_text()
            assert "# Dataset Export" in content
            assert "SMP-" in content


class TestExportManager:
    def setup_method(self):
        self.generator = ConcreteScenarioGenerator()
        self.scenario = self.generator.generate(seed=42)
        loader = KnowledgePackLoader(KNOWLEDGE_DIR)
        self.pack = loader.load()
        pipeline = ConcreteDatasetGeneratorPipeline()
        self.samples = pipeline.run(self.scenario, self.pack)

    def test_export_manager(self):
        with TemporaryDirectory() as tmp:
            manager = ExportManager()
            result = manager.export(
                self.samples[:5],
                "jsonl",
                Path(tmp),
                run_validation=False,
            )
            assert result["format"] == "jsonl"
            assert result["sample_count"] == 5
            assert "export_id" in result

    def test_list_exporters(self):
        manager = ExportManager()
        exporters = manager.list_exporters()
        assert "jsonl" in exporters
        assert "json" in exporters
        assert "csv" in exporters
        assert "markdown" in exporters

    def test_export_history(self):
        manager = ExportManager()
        with TemporaryDirectory() as tmp:
            manager.export(self.samples[:3], "jsonl", Path(tmp), run_validation=False)
            manager.export(self.samples[:3], "csv", Path(tmp), run_validation=False)
            history = manager.get_history()
            assert len(history) == 2
