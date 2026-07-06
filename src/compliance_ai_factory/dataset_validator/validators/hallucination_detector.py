import re

from typing import Any

from compliance_ai_factory.common.models.base import DatasetSample
from compliance_ai_factory.dataset_validator import Validator


class HallucinationDetector(Validator):
    def __init__(self, knowledge_pack: Any = None) -> None:
        self.knowledge_pack = knowledge_pack

    def validate(self, sample: DatasetSample) -> list[str]:
        errors: list[str] = []
        if self.knowledge_pack is None:
            return errors
        known_ids = {c.control_id for c in self.knowledge_pack.controls}
        known_evidence = {e.evidence_id for e in self.knowledge_pack.evidence}
        known_reasoning = {r.rule_id for r in self.knowledge_pack.reasoning}
        content_str = str(sample.content)
        control_pattern = re.findall(r'[A-Z]\.\d+\.\d+', content_str)
        for cid in control_pattern:
            if cid not in known_ids:
                errors.append(f"Hallucinated control ID: {cid}")
        evidence_pattern = re.findall(r'EVID-\w+-\d+', content_str)
        for eid in evidence_pattern:
            if eid not in known_evidence:
                errors.append(f"Hallucinated evidence ID: {eid}")
        reasoning_pattern = re.findall(r'RR-\d+', content_str)
        for rid in reasoning_pattern:
            if rid not in known_reasoning:
                errors.append(f"Hallucinated reasoning rule ID: {rid}")
        return errors
