from compliance_ai_factory.common.models.base import DatasetSample, Difficulty
from compliance_ai_factory.dataset_generator import SampleGenerator


class ExecutiveSummaryGenerator(SampleGenerator):
    generator_name = "executive_summary"

    def __init__(self, difficulty: str = "intermediate"):
        self.difficulty = Difficulty(difficulty)

    def generate(self, scenario, knowledge_pack):
        samples = []
        org = scenario.organization
        total = len(knowledge_pack.controls)
        compliant_count = total * 3 // 4
        content = {
            "summary": f"ISO 27001:2022 audit of {org.name} ({org.industry.value}, "
                      f"{org.size.value} size). Overall assessment: {org.maturity.value} maturity. "
                      f"Reviewed {total} controls across {', '.join(org.departments[:3])}.",
            "key_findings_count": total - compliant_count,
            "overall_risk_level": "medium",
            "strategic_recommendations": [
                "Strengthen evidence collection automation",
                "Enhance security awareness training",
                "Implement continuous compliance monitoring",
            ],
        }
        samples.append(DatasetSample(
            generator=self.generator_name,
            difficulty=self.difficulty.value,
            control_id="OVERALL",
            control_title="Executive Summary",
            content=content,
            sample_id="", scenario_id="", dataset_version="",
            industry="", company_size="", maturity="",
            language="en", standard="",
        ))
        return samples
