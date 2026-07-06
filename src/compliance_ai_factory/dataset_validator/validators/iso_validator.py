from typing import Any

from compliance_ai_factory.common.models.base import DatasetSample
from compliance_ai_factory.dataset_validator import Validator


class IsoValidator(Validator):
    def __init__(self, knowledge_pack: Any = None) -> None:
        self.knowledge_pack = knowledge_pack

    def validate(self, sample: DatasetSample) -> list[str]:
        errors: list[str] = []
        if self.knowledge_pack is None:
            return errors
        control = self.knowledge_pack.get_control(sample.control_id)
        if control is None:
            errors.append(f"Control {sample.control_id} not found in knowledge pack")
            return errors
        content = sample.content
        expected = set(control.expected_outcomes)
        if not expected:
            return errors
        found = any(
            any(outcome.lower() in str(v).lower() for outcome in expected)
            for v in content.values() if isinstance(v, str)
        )
        if not found:
            errors.append(f"No expected outcome referenced for control {sample.control_id}")
        return errors
