from typing import Any

from compliance_ai_factory.common.models.base import DatasetSample, Difficulty
from compliance_ai_factory.dataset_validator import Validator


class MetadataValidator(Validator):
    REQUIRED_FIELDS = [
        "sample_id", "scenario_id", "dataset_version", "generator",
        "industry", "company_size", "maturity", "difficulty",
        "language", "standard", "control_id", "control_title",
    ]

    def __init__(self, knowledge_pack: Any = None) -> None:
        self.knowledge_pack = knowledge_pack

    def validate(self, sample: DatasetSample) -> list[str]:
        errors: list[str] = []
        for field in self.REQUIRED_FIELDS:
            value = getattr(sample, field, None)
            if value is None or (isinstance(value, str) and not value.strip()):
                errors.append(f"Missing required metadata field: {field}")
        try:
            if sample.difficulty:
                Difficulty(sample.difficulty)
        except ValueError:
            errors.append(f"Invalid difficulty value: {sample.difficulty}")
        if sample.quality_score is not None and not (0.0 <= sample.quality_score <= 1.0):
            errors.append(f"quality_score out of range: {sample.quality_score}")
        return errors
