"""
Module 5: Dataset Validator

Every sample must pass:
  ISO Validation, Knowledge Validation, Metadata Validation,
  Scenario Validation, Consistency Validation, Duplicate Detection,
  Semantic Duplicate Detection, Reasoning Validation, Grammar Validation,
  Hallucination Detection

Exports with failed validation are prohibited.
"""

from abc import ABC, abstractmethod

from compliance_ai_factory.common.models.base import DatasetSample


class Validator(ABC):
    @abstractmethod
    def validate(self, sample: DatasetSample) -> list[str]:
        ...


class ValidationPipeline(ABC):
    @abstractmethod
    def validate_all(self, samples: list[DatasetSample]) -> list[DatasetSample]:
        ...


__all__ = [
    "Validator",
    "ValidationPipeline",
]
