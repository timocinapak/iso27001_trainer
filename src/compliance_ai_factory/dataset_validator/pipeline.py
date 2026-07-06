from typing import Any

from compliance_ai_factory.common.models.base import DatasetSample, ValidationStatus
from compliance_ai_factory.dataset_validator import ValidationPipeline
from compliance_ai_factory.dataset_validator.validators import (
    ConsistencyValidator,
    DuplicateDetector,
    GrammarValidator,
    HallucinationDetector,
    IsoValidator,
    KnowledgeValidator,
    MetadataValidator,
    ReasoningValidator,
    ScenarioValidator,
)


class ConcreteValidationPipeline(ValidationPipeline):
    def __init__(self, validators: list[Any] | None = None, knowledge_pack: Any = None, scenario: Any = None):
        self.knowledge_pack = knowledge_pack
        self.scenario = scenario
        all_validators = validators or [
            IsoValidator(knowledge_pack),
            KnowledgeValidator(knowledge_pack),
            ConsistencyValidator(knowledge_pack),
            GrammarValidator(knowledge_pack),
            HallucinationDetector(knowledge_pack),
            MetadataValidator(knowledge_pack),
            ScenarioValidator(knowledge_pack, scenario),
            ReasoningValidator(knowledge_pack),
        ]
        self.validators = all_validators

    def validate_all(self, samples: list[DatasetSample]) -> list[DatasetSample]:
        dup_detector = None
        for v in self.validators:
            if isinstance(v, DuplicateDetector):
                dup_detector = v
                dup_detector.set_all_samples(samples)
            if isinstance(v, ScenarioValidator) and self.scenario:
                v.set_scenario(self.scenario)

        for sample in samples:
            all_errors: list[str] = []
            for validator in self.validators:
                errors = validator.validate(sample)
                all_errors.extend(errors)
            if all_errors:
                sample.validation_status = ValidationStatus.FAILED
            else:
                sample.validation_status = ValidationStatus.PASSED
            total_validators = len(self.validators)
            passed = total_validators - len(
                [e for v in self.validators if v.validate(sample) for e in v.validate(sample)]
            )
            sample.quality_score = passed / total_validators if total_validators > 0 else 1.0

        return samples

    def get_summary(self, samples: list[DatasetSample]) -> dict[str, Any]:
        total = len(samples)
        passed = sum(1 for s in samples if s.validation_status == ValidationStatus.PASSED)
        failed = total - passed
        avg_quality = (
            sum(s.quality_score or 0 for s in samples) / total
            if total > 0 else 0.0
        )
        return {
            "total_samples": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": round(passed / total * 100, 1) if total > 0 else 0.0,
            "average_quality_score": round(avg_quality, 3),
        }
