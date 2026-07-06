from compliance_ai_factory.common.models.base import DatasetSample, Difficulty
from compliance_ai_factory.dataset_generator import SampleGenerator


class FindingGenerator(SampleGenerator):
    generator_name = "finding"

    def __init__(self, difficulty: str = "intermediate"):
        self.difficulty = Difficulty(difficulty)

    def generate(self, scenario, knowledge_pack):
        samples = []
        org = scenario.organization
        for i, control in enumerate(knowledge_pack.controls):
            severity = "high" if i % 3 == 0 else ("medium" if i % 3 == 1 else "low")
            content = {
                "finding_id": f"FND-{control.control_id.replace('.', '-')}",
                "severity": severity,
                "description": f"Control {control.control_id} ({control.title}) at {org.name}: "
                              f"Partial implementation observed in {org.departments[i % len(org.departments)]}. "
                              f"{'Evidence missing' if severity == 'high' else 'Documentation needs improvement'}.",
                "impact": f"Potential {severity} risk to information security posture.",
                "recommendation": f"Implement {control.title} fully across all departments.",
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
