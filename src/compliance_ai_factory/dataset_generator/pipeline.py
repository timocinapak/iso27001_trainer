from typing import Any

from compliance_ai_factory.common.models.base import DatasetSample, ValidationStatus
from compliance_ai_factory.dataset_generator import DatasetGeneratorPipeline
from compliance_ai_factory.dataset_generator.generators.audit_conversation import (
    AuditConversationGenerator,
)
from compliance_ai_factory.dataset_generator.generators.audit_question import AuditQuestionGenerator
from compliance_ai_factory.dataset_generator.generators.control_explanation import (
    ControlExplanationGenerator,
)
from compliance_ai_factory.dataset_generator.generators.corrective_action import (
    CorrectiveActionGenerator,
)
from compliance_ai_factory.dataset_generator.generators.decision import DecisionGenerator
from compliance_ai_factory.dataset_generator.generators.evidence import EvidenceGenerator
from compliance_ai_factory.dataset_generator.generators.executive_summary import (
    ExecutiveSummaryGenerator,
)
from compliance_ai_factory.dataset_generator.generators.finding import FindingGenerator
from compliance_ai_factory.dataset_generator.generators.followup_question import (
    FollowUpQuestionGenerator,
)
from compliance_ai_factory.dataset_generator.generators.good_answer import GoodAnswerGenerator
from compliance_ai_factory.dataset_generator.generators.partial_answer import PartialAnswerGenerator
from compliance_ai_factory.dataset_generator.generators.poor_answer import PoorAnswerGenerator
from compliance_ai_factory.dataset_generator.generators.preventive_action import (
    PreventiveActionGenerator,
)
from compliance_ai_factory.dataset_generator.generators.reasoning import ReasoningGenerator
from compliance_ai_factory.dataset_generator.generators.recommendation import (
    RecommendationGenerator,
)
from compliance_ai_factory.dataset_generator.generators.risk import RiskGenerator


class ConcreteDatasetGeneratorPipeline(DatasetGeneratorPipeline):
    version = "1.0"
    dataset_version = "1.0"

    def __init__(self, generators: list[Any] | None = None) -> None:
        self.generators = generators or [
            ControlExplanationGenerator(),
            AuditQuestionGenerator(),
            GoodAnswerGenerator(),
            PoorAnswerGenerator(),
            PartialAnswerGenerator(),
            EvidenceGenerator(),
            FollowUpQuestionGenerator(),
            DecisionGenerator(),
            FindingGenerator(),
            RecommendationGenerator(),
            RiskGenerator(),
            CorrectiveActionGenerator(),
            PreventiveActionGenerator(),
            ExecutiveSummaryGenerator(),
            AuditConversationGenerator(),
            ReasoningGenerator(),
        ]

    def run(self, scenario: Any, knowledge_pack: Any) -> list[DatasetSample]:
        samples: list[DatasetSample] = []
        sample_counter = 0

        for gen in self.generators:
            gen_samples = gen.generate(scenario, knowledge_pack)
            for sample in gen_samples:
                sample_counter += 1
                sample.sample_id = f"SMP-{sample_counter:05d}"
                sample.scenario_id = scenario.id
                sample.dataset_version = self.dataset_version
                sample.industry = scenario.organization.industry.value
                sample.company_size = scenario.organization.size.value
                sample.maturity = scenario.organization.maturity.value
                sample.language = "en"
                sample.standard = knowledge_pack.metadata.standard_name
                sample.validation_status = ValidationStatus.PENDING
                samples.append(sample)

        return samples
