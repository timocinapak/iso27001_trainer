from compliance_ai_factory.common.models.base import DatasetSample, Difficulty
from compliance_ai_factory.dataset_generator import SampleGenerator


class GoodAnswerGenerator(SampleGenerator):
    generator_name = "good_answer"

    def __init__(self, difficulty: str = "intermediate"):
        self.difficulty = Difficulty(difficulty)

    def generate(self, scenario, knowledge_pack):
        samples = []
        org = scenario.organization
        for control in knowledge_pack.controls:
            evidence_ids = control.required_evidence or ["EVID-GEN-001"]
            content = {
                "answer": f"{org.name} has implemented {control.title} by establishing "
                         f"{len(control.implementation_guidance)} key procedures. "
                         f"The {org.departments[0]} team leads implementation with "
                         f"support from {org.departments[1] if len(org.departments) > 1 else 'IT'}.",
                "evidence_referenced": evidence_ids,
                "compliance_determination": "Compliant — all expected outcomes are met with supporting evidence.",
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
