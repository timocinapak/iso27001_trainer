from compliance_ai_factory.common.models.base import DatasetSample, Difficulty
from compliance_ai_factory.dataset_generator import SampleGenerator


class ReasoningGenerator(SampleGenerator):
    generator_name = "reasoning"

    def __init__(self, difficulty: str = "intermediate"):
        self.difficulty = Difficulty(difficulty)

    def generate(self, scenario, knowledge_pack):
        samples = []
        org = scenario.organization
        for control in knowledge_pack.controls:
            rules = knowledge_pack.get_reasoning_rules(control.control_id)
            rule_ids = [r.rule_id for r in rules]
            content = {
                "step_by_step_reasoning": [
                    f"Step 1: Identify applicable control — {control.control_id} ({control.title})",
                    f"Step 2: Review {len(control.expected_outcomes)} expected outcomes",
                    "Step 3: Evaluate evidence against each outcome",
                    f"Step 4: Assess maturity level ({org.maturity.value}) against control requirements",
                    "Step 5: Determine compliance status based on evidence sufficiency",
                ],
                "rules_applied": rule_ids or ["RR-GEN-001"],
                "conclusion": f"Control {control.control_id} at {org.name} is "
                            f"{'compliant' if len(control.expected_outcomes) > 2 else 'partially compliant'}.",
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
