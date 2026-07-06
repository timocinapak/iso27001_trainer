from compliance_ai_factory.common.models.base import DatasetSample, Difficulty
from compliance_ai_factory.dataset_generator import SampleGenerator


class EvidenceGenerator(SampleGenerator):
    generator_name = "evidence"

    def __init__(self, difficulty: str = "intermediate"):
        self.difficulty = Difficulty(difficulty)

    def generate(self, scenario, knowledge_pack):
        samples = []
        org = scenario.organization
        for control in knowledge_pack.controls[:15]:
            evidence_reqs = knowledge_pack.get_evidence_for_control(control.control_id)
            if not evidence_reqs:
                continue
            for ev in evidence_reqs:
                content = {
                    "evidence_id": ev.evidence_id,
                    "description": f"{ev.title}: {ev.description} at {org.name}",
                    "location": f"{org.departments[0] if org.departments else 'Admin'} shared drive / compliance folder",
                    "verification_method": f"Review {ev.evidence_id} document and verify against {control.control_id} requirements.",
                    "category": ev.category,
                    "mandatory": ev.mandatory,
                }
                samples.append(DatasetSample(
                    generator=self.generator_name,
                    difficulty=self.difficulty.value,
                    control_id=control.control_id,
                    control_title=control.title,
                    content=content,
                    sample_id="", scenario_id="", dataset_version="",
                    industry="", company_size="", maturity="",
                    language="en", standard="",
                ))
        return samples
