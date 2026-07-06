import re

from typing import Any

from compliance_ai_factory.common.models.base import DatasetSample
from compliance_ai_factory.dataset_validator import Validator


class ReasoningValidator(Validator):
    def __init__(self, knowledge_pack: Any = None) -> None:
        self.knowledge_pack = knowledge_pack

    def validate(self, sample: DatasetSample) -> list[str]:
        errors: list[str] = []
        rules_applied = sample.content.get("rules_applied", [])
        step_by_step = sample.content.get("step_by_step_reasoning", [])
        if isinstance(rules_applied, list) and rules_applied:
            if self.knowledge_pack is None:
                return errors
            known_rules = {r.rule_id for r in self.knowledge_pack.reasoning}
            for rid in rules_applied:
                if rid not in known_rules and not rid.startswith("RR-GEN"):
                    errors.append(f"Reasoning rule {rid} not found in knowledge pack")
        if isinstance(step_by_step, list) and step_by_step:
            for i, step in enumerate(step_by_step):
                if not isinstance(step, str) or len(step.strip()) < 10:
                    errors.append(f"Reasoning step {i+1} is too short or invalid")
            step_pattern = re.compile(r'^Step \d+:', re.IGNORECASE)
            for step in step_by_step:
                if isinstance(step, str) and not step_pattern.match(step.strip()):
                    errors.append(f"Reasoning step does not follow expected format: '{step[:50]}'")
                    break
        return errors
