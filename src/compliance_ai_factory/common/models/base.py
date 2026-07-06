from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Industry(str, Enum):
    TECHNOLOGY = "technology"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    ENERGY = "energy"
    GOVERNMENT = "government"
    EDUCATION = "education"
    TELECOMMUNICATIONS = "telecommunications"
    TRANSPORTATION = "transportation"


class CompanySize(str, Enum):
    STARTUP = "startup"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"


class MaturityLevel(str, Enum):
    INITIAL = "initial"
    REPEATABLE = "repeatable"
    DEFINED = "defined"
    MANAGED = "managed"
    OPTIMIZING = "optimizing"


class Difficulty(str, Enum):
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ValidationStatus(str, Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"


class Employee(BaseModel):
    id: str
    name: str
    role: str
    department: str
    seniority: str


class Asset(BaseModel):
    id: str
    name: str
    type: str
    owner: str
    department: str
    classification: str


class Organization(BaseModel):
    name: str
    industry: Industry
    size: CompanySize
    maturity: MaturityLevel
    description: str
    departments: list[str]
    employees: list[Employee]
    assets: list[Asset]
    applications: list[str]
    infrastructure: list[str]
    cloud_services: list[str]
    suppliers: list[str]
    processes: list[str]
    threats: list[str]
    risks: list[str]
    regulations: list[str]


class Scenario(BaseModel):
    id: str
    version: str
    created_at: datetime
    organization: Organization


class DatasetSample(BaseModel):
    sample_id: str
    scenario_id: str
    dataset_version: str
    generator: str
    industry: str
    company_size: str
    maturity: str
    difficulty: str
    language: str
    standard: str
    control_id: str
    control_title: str
    quality_score: float | None = None
    validation_status: ValidationStatus = ValidationStatus.PENDING
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    content: dict[str, Any]


class ExportMetadata(BaseModel):
    version: str
    generated_at: datetime
    generator: str
    standard: str
    sample_count: int
    fields: list[str]
