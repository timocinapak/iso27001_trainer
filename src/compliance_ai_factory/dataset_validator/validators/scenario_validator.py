from typing import Any

from compliance_ai_factory.common.models.base import (
    CompanySize,
    DatasetSample,
    Industry,
    MaturityLevel,
)
from compliance_ai_factory.dataset_validator import Validator


class ScenarioValidator(Validator):
    def __init__(self, knowledge_pack: Any = None, scenario: Any = None) -> None:
        self.knowledge_pack = knowledge_pack
        self.scenario = scenario

    def set_scenario(self, scenario: Any) -> None:
        self.scenario = scenario

    def validate(self, sample: DatasetSample) -> list[str]:
        errors: list[str] = []
        if self.scenario is None:
            return errors
        org = self.scenario.organization
        try:
            ind = Industry(sample.industry)
            if ind != org.industry:
                errors.append(f"Industry mismatch: sample={sample.industry}, scenario={org.industry.value}")
        except ValueError:
            errors.append(f"Invalid industry: {sample.industry}")
        try:
            size = CompanySize(sample.company_size)
            if size != org.size:
                errors.append(f"Company size mismatch: sample={sample.company_size}, scenario={org.size.value}")
        except ValueError:
            errors.append(f"Invalid company_size: {sample.company_size}")
        try:
            mat = MaturityLevel(sample.maturity)
            if mat != org.maturity:
                errors.append(f"Maturity mismatch: sample={sample.maturity}, scenario={org.maturity.value}")
        except ValueError:
            errors.append(f"Invalid maturity: {sample.maturity}")
        return errors
