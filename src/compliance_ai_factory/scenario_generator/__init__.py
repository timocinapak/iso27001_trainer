"""
Module 3: Scenario Generator

Creates a realistic organization before generating any sample.
Every downstream module MUST reuse this scenario.
No generator may invent a different company.
"""

from abc import ABC, abstractmethod

from compliance_ai_factory.common.models.base import Scenario


class ScenarioGenerator(ABC):
    @abstractmethod
    def generate(self, seed: int | None = None) -> Scenario:
        ...


class ScenarioRepository(ABC):
    @abstractmethod
    def save(self, scenario: Scenario) -> str:
        ...

    @abstractmethod
    def load(self, scenario_id: str) -> Scenario:
        ...


__all__ = [
    "ScenarioGenerator",
    "ScenarioRepository",
]
