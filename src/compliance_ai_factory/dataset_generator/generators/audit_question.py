from compliance_ai_factory.common.models.base import DatasetSample, Difficulty
from compliance_ai_factory.dataset_generator import SampleGenerator


class AuditQuestionGenerator(SampleGenerator):
    generator_name = "audit_question"

    def __init__(self, difficulty: str = "intermediate"):
        self.difficulty = Difficulty(difficulty)

    def generate(self, scenario, knowledge_pack):
        samples = []
        org = scenario.organization
        for control in knowledge_pack.controls:
            audit_intent = control.audit_intent or f"Verify compliance with {control.title}"
            content = {
                "question": f"Can {org.name} demonstrate that {control.title} "
                           f"is effectively implemented across {', '.join(org.departments[:3])}?",
                "context": f"During the audit of {org.name}, the auditor reviews "
                          f"{audit_intent.lower()}.",
                "what_to_look_for": control.expected_outcomes,
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
