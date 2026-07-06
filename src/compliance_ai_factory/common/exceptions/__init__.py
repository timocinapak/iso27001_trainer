class ComplianceAIError(Exception):
    """Base exception for all Compliance AI Factory errors."""


class KnowledgePackError(ComplianceAIError):
    """Raised when a Knowledge Pack operation fails."""


class KnowledgePackNotFoundError(KnowledgePackError):
    """Raised when a Knowledge Pack is not found."""


class KnowledgePackValidationError(KnowledgePackError):
    """Raised when a Knowledge Pack fails validation."""


class ScenarioError(ComplianceAIError):
    """Raised when scenario generation fails."""


class DatasetGenerationError(ComplianceAIError):
    """Raised when dataset generation fails."""


class ValidationError(ComplianceAIError):
    """Raised when dataset validation fails."""


class ExportError(ComplianceAIError):
    """Raised when dataset export fails."""


class ConsistencyError(ValidationError):
    """Raised when a consistency check fails."""


class HallucinationError(ValidationError):
    """Raised when a hallucination is detected."""


__all__ = [
    "ComplianceAIError",
    "KnowledgePackError",
    "KnowledgePackNotFoundError",
    "KnowledgePackValidationError",
    "ScenarioError",
    "DatasetGenerationError",
    "ValidationError",
    "ExportError",
    "ConsistencyError",
    "HallucinationError",
]
