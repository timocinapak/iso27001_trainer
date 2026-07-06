from compliance_ai_factory.common.models.base import DatasetSample, Difficulty
from compliance_ai_factory.dataset_generator import SampleGenerator


class PoorAnswerGenerator(SampleGenerator):
    generator_name = "poor_answer"

    def __init__(self, difficulty: str = "intermediate"):
        self.difficulty = Difficulty(difficulty)

    def generate(self, scenario, knowledge_pack):
        samples = []
        org = scenario.organization
        for control in knowledge_pack.controls:
            outcomes = control.expected_outcomes or ["Control outcome unspecified"]
            content = {
                "answer": f"{org.name} has partially addressed {control.title}. "
                         f"Documentation exists but is incomplete. "
                         f"Only {len(outcomes)//2 + 1} of {len(outcomes)} expected outcomes are evidenced.",
                "issues": [
                    "Incomplete documentation",
                    "Missing evidence for key requirements",
                    "Lack of regular review process",
                ],
                "missing_elements": [o for o in outcomes[:2]],
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
