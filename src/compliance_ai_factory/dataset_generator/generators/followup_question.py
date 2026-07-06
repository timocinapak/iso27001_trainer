from compliance_ai_factory.common.models.base import DatasetSample, Difficulty
from compliance_ai_factory.dataset_generator import SampleGenerator


class FollowUpQuestionGenerator(SampleGenerator):
    generator_name = "followup_question"

    def __init__(self, difficulty: str = "intermediate"):
        self.difficulty = Difficulty(difficulty)

    def generate(self, scenario, knowledge_pack):
        samples = []
        org = scenario.organization
        for control in knowledge_pack.controls:
            content = {
                "question": f"Regarding {control.title}, can you provide the specific "
                           f"evidence for how {org.departments[0] if org.departments else 'the team'} "
                           f"measures the effectiveness of this control?",
                "trigger": "Previous answer mentioned implementation but lacked specific metrics or evidence.",
                "probes_deeper": "Asks for measurable outcomes rather than process descriptions.",
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
