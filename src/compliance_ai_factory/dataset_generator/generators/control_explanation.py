from compliance_ai_factory.common.models.base import DatasetSample, Difficulty
from compliance_ai_factory.dataset_generator import SampleGenerator


class ControlExplanationGenerator(SampleGenerator):
    generator_name = "control_explanation"

    def __init__(self, difficulty: str = "intermediate"):
        self.difficulty = Difficulty(difficulty)

    def generate(self, scenario, knowledge_pack):
        samples = []
        org = scenario.organization
        for control in knowledge_pack.controls:
            content = {
                "explanation": f"{control.title}: {control.description} "
                              f"For {org.name}, this control requires {len(control.implementation_guidance)} "
                              f"implementation steps tailored to their {org.industry.value} environment.",
                "key_requirements": [g for g in control.implementation_guidance],
                "implementation_approach": (
                    f"Implement across {', '.join(org.departments[:3])}. "
                    f"Priority based on {org.maturity.value} maturity level."
                ),
            }
            samples.append(DatasetSample(
                generator=self.generator_name,
                difficulty=self.difficulty.value,
                control_id=control.control_id,
                control_title=control.title,
                content=content,
                sample_id="",
                scenario_id="",
                dataset_version="",
                industry="",
                company_size="",
                maturity="",
                language="en",
                standard="",
            ))
        return samples
