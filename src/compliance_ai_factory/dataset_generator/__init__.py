"""
Module 4: Dataset Generator

Consumes Scenario + Knowledge Pack and produces training samples.

Supported dataset families:
  Control Explanation, Audit Question, Good Answer, Poor Answer,
  Partial Answer, Evidence, Follow-up Question, Decision, Finding,
  Recommendation, Risk, Corrective Action, Preventive Action,
  Executive Summary, Audit Conversation, Reasoning
"""

from abc import ABC, abstractmethod

from compliance_ai_factory.common.models.base import DatasetSample, Scenario
from compliance_ai_factory.knowledge_pack.models import KnowledgePack


class SampleGenerator(ABC):
    generator_name: str

    @abstractmethod
    def generate(
        self,
        scenario: Scenario,
        knowledge_pack: KnowledgePack,
    ) -> list[DatasetSample]:
        ...


class DatasetGeneratorPipeline(ABC):
    @abstractmethod
    def run(
        self,
        scenario: Scenario,
        knowledge_pack: KnowledgePack,
    ) -> list[DatasetSample]:
        ...


__all__ = [
    "SampleGenerator",
    "DatasetGeneratorPipeline",
]
