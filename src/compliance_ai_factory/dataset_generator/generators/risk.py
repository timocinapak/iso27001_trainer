from compliance_ai_factory.common.models.base import DatasetSample, Difficulty
from compliance_ai_factory.dataset_generator import SampleGenerator


class RiskGenerator(SampleGenerator):
    generator_name = "risk"

    def __init__(self, difficulty: str = "intermediate"):
        self.difficulty = Difficulty(difficulty)

    def generate(self, scenario, knowledge_pack):
        samples = []
        org = scenario.organization
        for i, control in enumerate(knowledge_pack.controls):
            org_risks = org.risks or ["General compliance risk"]
            risk = org_risks[i % len(org_risks)]
            content = {
                "risk_id": f"RSK-{control.control_id.replace('.', '-')}",
                "description": f"Risk related to {control.title}: {risk}. "
                              f"Affects {org.name} across {', '.join(org.departments[:2])}.",
                "likelihood": "medium" if i % 2 == 0 else "high",
                "impact": "high" if len(control.required_evidence) > 1 else "medium",
                "mitigation": f"Implement and maintain {control.title} per ISO 27001 requirements.",
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
