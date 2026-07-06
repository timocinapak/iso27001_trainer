from pathlib import Path

from compliance_ai_factory.scenario_generator.generator import ConcreteScenarioGenerator
from compliance_ai_factory.knowledge_pack.loader import KnowledgePackLoader
from compliance_ai_factory.dataset_generator.pipeline import ConcreteDatasetGeneratorPipeline
from compliance_ai_factory.dataset_generator.generators.control_explanation import ControlExplanationGenerator
from compliance_ai_factory.dataset_generator.generators.audit_question import AuditQuestionGenerator
from compliance_ai_factory.dataset_generator.generators.good_answer import GoodAnswerGenerator
from compliance_ai_factory.dataset_generator.generators.finding import FindingGenerator
from compliance_ai_factory.common.models.base import DatasetSample, Difficulty


KNOWLEDGE_DIR = Path(__file__).parents[2] / "knowledge" / "iso27001"


class TestSampleGenerators:
    def setup_method(self):
        self.generator = ConcreteScenarioGenerator()
        self.scenario = self.generator.generate(seed=42)
        loader = KnowledgePackLoader(KNOWLEDGE_DIR)
        self.pack = loader.load()

    def test_control_explanation_generator(self):
        gen = ControlExplanationGenerator()
        samples = gen.generate(self.scenario, self.pack)
        assert len(samples) > 0
        sample = samples[0]
        assert isinstance(sample, DatasetSample)
        assert sample.generator == "control_explanation"
        assert "explanation" in sample.content
        assert sample.control_id is not None

    def test_audit_question_generator(self):
        gen = AuditQuestionGenerator()
        samples = gen.generate(self.scenario, self.pack)
        assert len(samples) > 0
        assert "question" in samples[0].content

    def test_good_answer_generator(self):
        gen = GoodAnswerGenerator()
        samples = gen.generate(self.scenario, self.pack)
        assert len(samples) > 0
        assert "answer" in samples[0].content

    def test_finding_generator(self):
        gen = FindingGenerator()
        samples = gen.generate(self.scenario, self.pack)
        assert len(samples) > 0
        assert "finding_id" in samples[0].content
        assert "severity" in samples[0].content


class TestDatasetGeneratorPipeline:
    def setup_method(self):
        self.generator = ConcreteScenarioGenerator()
        self.scenario = self.generator.generate(seed=42)
        loader = KnowledgePackLoader(KNOWLEDGE_DIR)
        self.pack = loader.load()

    def test_pipeline_runs_all_generators(self):
        pipeline = ConcreteDatasetGeneratorPipeline()
        samples = pipeline.run(self.scenario, self.pack)
        assert len(samples) > 0
        for sample in samples:
            assert sample.sample_id.startswith("SMP-")
            assert sample.scenario_id == self.scenario.id
            assert sample.dataset_version == "1.0"
            assert sample.language == "en"
            assert sample.standard == "ISO/IEC 27001"

    def test_pipeline_includes_all_generator_types(self):
        pipeline = ConcreteDatasetGeneratorPipeline()
        samples = pipeline.run(self.scenario, self.pack)
        generator_names = {s.generator for s in samples}
        expected = {
            "control_explanation", "audit_question", "good_answer",
            "poor_answer", "partial_answer", "evidence", "finding",
            "recommendation", "risk", "corrective_action", "preventive_action",
            "decision", "followup_question", "executive_summary",
            "audit_conversation", "reasoning",
        }
        assert generator_names == expected, f"Missing: {expected - generator_names}"

    def test_pipeline_assigns_unique_ids(self):
        pipeline = ConcreteDatasetGeneratorPipeline()
        samples = pipeline.run(self.scenario, self.pack)
        ids = [s.sample_id for s in samples]
        assert len(ids) == len(set(ids))
