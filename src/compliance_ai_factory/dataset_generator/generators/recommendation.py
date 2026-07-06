from compliance_ai_factory.common.models.base import DatasetSample, Difficulty
from compliance_ai_factory.dataset_generator import SampleGenerator


class RecommendationGenerator(SampleGenerator):
    generator_name = "recommendation"

    def __init__(self, difficulty: str = "intermediate"):
        self.difficulty = Difficulty(difficulty)

    def generate(self, scenario, knowledge_pack):
        samples = []
        org = scenario.organization
        for control in knowledge_pack.controls:
            priority = "high" if len(control.required_evidence) > 2 else "medium"
            content = {
                "recommendation": f"Strengthen {control.title} at {org.name} by automating "
                                 f"evidence collection and implementing regular review cycles.",
                "priority": priority,
                "timeline": "3-6 months" if priority == "high" else "6-12 months",
                "effort": "High" if priority == "high" else "Medium",
                "owner": f"{org.departments[0] if org.departments else 'CISO'}",
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
