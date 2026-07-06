from typing import Any

from compliance_ai_factory.common.models.base import DatasetSample
from compliance_ai_factory.dataset_validator import Validator


class KnowledgeValidator(Validator):
    def __init__(self, knowledge_pack: Any = None) -> None:
        self.knowledge_pack = knowledge_pack

    def validate(self, sample: DatasetSample) -> list[str]:
        errors: list[str] = []
        if self.knowledge_pack is None:
            return errors
        known_ids = {c.control_id for c in self.knowledge_pack.controls}
        known_evidence = {e.evidence_id for e in self.knowledge_pack.evidence}
        content_str = str(sample.content)
        for cid in known_ids:
            if cid.lower() in content_str.lower():
                break
        else:
            if sample.control_id not in known_ids:
                errors.append(f"Control {sample.control_id} referenced but not in knowledge pack")
        ev = sample.content.get("evidence_referenced", [])
        if isinstance(ev, list):
            for eid in ev:
                if eid not in known_evidence:
                    errors.append(f"Evidence {eid} referenced but not in knowledge pack")
        return errors
