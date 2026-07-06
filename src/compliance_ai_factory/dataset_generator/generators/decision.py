from compliance_ai_factory.common.models.base import DatasetSample, Difficulty
from compliance_ai_factory.dataset_generator import SampleGenerator


class DecisionGenerator(SampleGenerator):
    generator_name = "decision"

    def __init__(self, difficulty: str = "intermediate"):
        self.difficulty = Difficulty(difficulty)

    def generate(self, scenario, knowledge_pack):
        samples = []
        org = scenario.organization
        for control in knowledge_pack.controls:
            rules = knowledge_pack.get_reasoning_rules(control.control_id)
            applicable_rules = [r.rule_id for r in rules] if rules else ["RR-GEN-001"]
            content = {
                "decision": f"Control {control.control_id} ({control.title}) at {org.name} is assessed as COMPLIANT",
                "rationale": f"All {len(control.expected_outcomes)} expected outcomes demonstrated. "
                            f"Evidence reviewed and verified. "
                            f"Implementation covers {', '.join(org.departments[:2])}.",
                "applicable_rules": applicable_rules,
                "risk_level": "low" if len(applicable_rules) > 1 else "medium",
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
