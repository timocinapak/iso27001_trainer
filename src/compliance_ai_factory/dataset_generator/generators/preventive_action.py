from compliance_ai_factory.common.models.base import DatasetSample, Difficulty
from compliance_ai_factory.dataset_generator import SampleGenerator


class PreventiveActionGenerator(SampleGenerator):
    generator_name = "preventive_action"

    def __init__(self, difficulty: str = "intermediate"):
        self.difficulty = Difficulty(difficulty)

    def generate(self, scenario, knowledge_pack):
        samples = []
        org = scenario.organization
        for control in knowledge_pack.controls:
            threats = org.threats or ["Security incidents"]
            content = {
                "action": f"Proactively strengthen {control.title} at {org.name} to prevent "
                         f"risks related to {', '.join(threats[:2])}.",
                "trigger": f"Risk assessment identified potential gaps in {control.control_id} implementation.",
                "monitoring_approach": f"Quarterly reviews of {control.control_id} control effectiveness "
                                      f"with automated evidence collection.",
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
