from typing import Any

from compliance_ai_factory.common.models.base import DatasetSample
from compliance_ai_factory.dataset_validator import Validator


class DuplicateDetector(Validator):
    def __init__(self, knowledge_pack: Any = None, all_samples: list[DatasetSample] | None = None) -> None:
        self.knowledge_pack = knowledge_pack
        self.all_samples = all_samples or []

    def set_all_samples(self, samples: list[DatasetSample]) -> None:
        self.all_samples = samples

    def validate(self, sample: DatasetSample) -> list[str]:
        errors: list[str] = []
        if not self.all_samples:
            return errors
        sample_content_json = str(sorted(sample.content.items()))
        for other in self.all_samples:
            if other.sample_id == sample.sample_id:
                continue
            other_content_json = str(sorted(other.content.items()))
            if sample_content_json == other_content_json:
                errors.append(f"Duplicate content with sample {other.sample_id}")
                break
        return errors
