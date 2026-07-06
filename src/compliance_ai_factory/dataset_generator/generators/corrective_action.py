from compliance_ai_factory.common.models.base import DatasetSample, Difficulty
from compliance_ai_factory.dataset_generator import SampleGenerator


class CorrectiveActionGenerator(SampleGenerator):
    generator_name = "corrective_action"

    def __init__(self, difficulty: str = "intermediate"):
        self.difficulty = Difficulty(difficulty)

    def generate(self, scenario, knowledge_pack):
        samples = []
        org = scenario.organization
        for i, control in enumerate(knowledge_pack.controls):
            dept = org.departments[i % len(org.departments)]
            content = {
                "action": f"Remediate {control.title} non-compliance in {dept}. "
                         f"Re-implement {len(control.implementation_guidance)} missing procedures.",
                "root_cause": f"Incomplete implementation of {control.control_id} during initial deployment.",
                "deadline": "30 days",
                "owner": f"Head of {dept}",
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
