from typing import Any

from compliance_ai_factory.common.models.base import DatasetSample
from compliance_ai_factory.dataset_validator import Validator


class ConsistencyValidator(Validator):
    def __init__(self, knowledge_pack: Any = None) -> None:
        self.knowledge_pack = knowledge_pack

    def validate(self, sample: DatasetSample) -> list[str]:
        errors: list[str] = []
        content = sample.content
        for key, value in content.items():
            if isinstance(value, str) and not value.strip():
                errors.append(f"Content field '{key}' is empty")
            elif isinstance(value, list) and len(value) == 0:
                errors.append(f"Content field '{key}' is an empty list")
        text_values = [str(v) for v in content.values() if isinstance(v, str)]
        contradictions = [
            ("compliant", "non-compliant"),
            ("passed", "failed"),
            ("implemented", "not implemented"),
        ]
        for a, b in contradictions:
            has_a = any(a in tv.lower() for tv in text_values)
            has_b = any(b in tv.lower() for tv in text_values)
            if has_a and has_b:
                errors.append(f"Contradictory terms '{a}' and '{b}' found in sample content")
        return errors
