from compliance_ai_factory.common.models.base import DatasetSample, Difficulty
from compliance_ai_factory.dataset_generator import SampleGenerator


class AuditConversationGenerator(SampleGenerator):
    generator_name = "audit_conversation"

    def __init__(self, difficulty: str = "intermediate"):
        self.difficulty = Difficulty(difficulty)

    def generate(self, scenario, knowledge_pack):
        samples = []
        org = scenario.organization
        for control in knowledge_pack.controls:
            content = {
                "dialog": [
                    {
                        "speaker": "Auditor",
                        "text": f"Can you describe how {org.name} implements {control.title}?"
                    },
                    {
                        "speaker": "Auditee",
                        "text": f"We have implemented {control.title} through "
                               f"{len(control.implementation_guidance)} procedures managed by "
                               f"the {org.departments[0] if org.departments else 'security'} team."
                    },
                    {
                        "speaker": "Auditor",
                        "text": f"What evidence can you provide for {control.control_id}?"
                    },
                    {
                        "speaker": "Auditee",
                        "text": f"We maintain documentation including {', '.join(control.required_evidence[:2])}."
                    },
                ],
                "topics_covered": [control.title, control.objective],
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
