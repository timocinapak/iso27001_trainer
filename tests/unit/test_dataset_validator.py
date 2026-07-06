from pathlib import Path

from compliance_ai_factory.scenario_generator.generator import ConcreteScenarioGenerator
from compliance_ai_factory.knowledge_pack.loader import KnowledgePackLoader
from compliance_ai_factory.dataset_generator.pipeline import ConcreteDatasetGeneratorPipeline
from compliance_ai_factory.dataset_validator.pipeline import ConcreteValidationPipeline
from compliance_ai_factory.dataset_validator.validators import (
    IsoValidator,
    KnowledgeValidator,
    ConsistencyValidator,
    GrammarValidator,
    HallucinationDetector,
    DuplicateDetector,
    MetadataValidator,
    ReasoningValidator,
)
from compliance_ai_factory.common.models.base import DatasetSample, ValidationStatus


KNOWLEDGE_DIR = Path(__file__).parents[2] / "knowledge" / "iso27001"


class TestValidators:
    def setup_method(self):
        self.generator = ConcreteScenarioGenerator()
        self.scenario = self.generator.generate(seed=42)
        loader = KnowledgePackLoader(KNOWLEDGE_DIR)
        self.pack = loader.load()
        pipeline = ConcreteDatasetGeneratorPipeline()
        self.samples = pipeline.run(self.scenario, self.pack)

    def test_iso_validator(self):
        validator = IsoValidator(self.pack)
        errors = validator.validate(self.samples[0])
        assert isinstance(errors, list)

    def test_knowledge_validator(self):
        validator = KnowledgeValidator(self.pack)
        errors = validator.validate(self.samples[0])
        assert isinstance(errors, list)

    def test_consistency_validator(self):
        validator = ConsistencyValidator(self.pack)
        errors = validator.validate(self.samples[0])
        assert isinstance(errors, list)

    def test_grammar_validator(self):
        validator = GrammarValidator(self.pack)
        errors = validator.validate(self.samples[0])
        assert isinstance(errors, list)

    def test_hallucination_detector(self):
        validator = HallucinationDetector(self.pack)
        errors = validator.validate(self.samples[0])
        assert isinstance(errors, list)

    def test_metadata_validator(self):
        validator = MetadataValidator(self.pack)
        errors = validator.validate(self.samples[0])
        assert isinstance(errors, list)

    def test_duplicate_detector(self):
        validator = DuplicateDetector(self.pack, all_samples=self.samples)
        errors = validator.validate(self.samples[0])
        assert isinstance(errors, list)

    def test_reasoning_validator(self):
        validator = ReasoningValidator(self.pack)
        errors = validator.validate(self.samples[0])
        assert isinstance(errors, list)


class TestValidationPipeline:
    def setup_method(self):
        self.generator = ConcreteScenarioGenerator()
        self.scenario = self.generator.generate(seed=42)
        loader = KnowledgePackLoader(KNOWLEDGE_DIR)
        self.pack = loader.load()
        pipeline = ConcreteDatasetGeneratorPipeline()
        self.samples = pipeline.run(self.scenario, self.pack)

    def test_validate_all_updates_status(self):
        v_pipeline = ConcreteValidationPipeline(knowledge_pack=self.pack)
        validated = v_pipeline.validate_all(self.samples)
        for sample in validated:
            assert sample.validation_status in (ValidationStatus.PASSED, ValidationStatus.FAILED)
            assert sample.quality_score is not None

    def test_get_summary(self):
        v_pipeline = ConcreteValidationPipeline(knowledge_pack=self.pack)
        validated = v_pipeline.validate_all(self.samples)
        summary = v_pipeline.get_summary(validated)
        assert summary["total_samples"] == len(validated)
        assert summary["passed"] + summary["failed"] == summary["total_samples"]
        assert 0 <= summary["pass_rate"] <= 100
