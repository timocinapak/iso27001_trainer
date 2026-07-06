from compliance_ai_factory.common.models.base import DatasetSample, Difficulty
from compliance_ai_factory.dataset_generator import SampleGenerator


class PartialAnswerGenerator(SampleGenerator):
    generator_name = "partial_answer"

    def __init__(self, difficulty: str = "intermediate"):
        self.difficulty = Difficulty(difficulty)

    def generate(self, scenario, knowledge_pack):
        samples = []
        org = scenario.organization
        for control in knowledge_pack.controls:
            guidance = control.implementation_guidance or ["Implement control"]
            content = {
                "answer": f"{org.name} has made progress on {control.title}. "
                         f"Implemented {len(guidance)//2 + 1} of {len(guidance)} "
                         f"implementation steps in the {org.departments[0]} department.",
                "covered_aspects": [g for g in guidance[:len(guidance)//2 + 1]],
                "gaps": [f"Not yet implemented: {g}" for g in guidance[len(guidance)//2 + 1:]],
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
