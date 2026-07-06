from datetime import date
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ControlAttribute(BaseModel):
    name: str
    value: str


class DecisionRule(BaseModel):
    condition: str
    outcome: str
    reasoning: str
    severity: str


class AuditPattern(BaseModel):
    pattern_type: str
    description: str
    questions: list[str]
    evidence_to_look_for: list[str]
    common_findings: list[str]


class StandardMetadata(BaseModel):
    standard_name: str
    version: str
    release_date: date
    publisher: str
    supported_languages: list[str] = ["en"]
    description: str | None = None
    category: str | None = None


class ControlDefinition(BaseModel):
    control_id: str
    clause: str
    title: str
    objective: str
    description: str
    implementation_guidance: list[str] = []
    expected_outcomes: list[str] = []
    attributes: list[ControlAttribute] = []
    related_controls: list[str] = []
    required_evidence: list[str] = []
    audit_intent: str | None = None
    decision_rules: list[DecisionRule] = []


class Terminology(BaseModel):
    term: str
    definition: str
    synonyms: list[str] = []
    abbreviations: list[str] = []
    source: str | None = None


class GlossaryEntry(BaseModel):
    term: str
    definition: str
    context: str | None = None
    see_also: list[str] = []


class EvidenceRequirement(BaseModel):
    evidence_id: str
    title: str
    description: str
    category: str
    control_ids: list[str] = []
    typical_documents: list[str] = []
    system_evidence: list[str] = []
    technical_evidence: list[str] = []
    management_evidence: list[str] = []
    mandatory: bool = False


class ReasoningRule(BaseModel):
    rule_id: str
    rule_type: str
    description: str
    logic: str
    control_ids: list[str] = []
    severity: str = "medium"


class CrossReference(BaseModel):
    source_control_id: str
    target_control_id: str
    relationship_type: str
    description: str | None = None


class MaturityMapping(BaseModel):
    maturity_level: str
    description: str
    expected_controls: list[str]
    typical_gaps: list[str] = []


class IndustryMapping(BaseModel):
    industry: str
    description: str
    focus_controls: list[str]
    typical_risks: list[str] = []


class KnowledgePack(BaseModel):
    metadata: StandardMetadata
    controls: list[ControlDefinition]
    terminology: list[Terminology] = []
    evidence: list[EvidenceRequirement] = []
    reasoning: list[ReasoningRule] = []
    cross_references: list[CrossReference] = []
    glossary: list[GlossaryEntry] = []
    maturity: list[MaturityMapping] = []
    industries: list[IndustryMapping] = []
    audit_patterns: list[AuditPattern] = []

    def get_control(self, control_id: str) -> ControlDefinition | None:
        for c in self.controls:
            if c.control_id == control_id:
                return c
        return None

    def get_evidence_for_control(self, control_id: str) -> list[EvidenceRequirement]:
        return [e for e in self.evidence if control_id in e.control_ids]

    def get_related_controls(self, control_id: str) -> list[ControlDefinition]:
        control = self.get_control(control_id)
        if not control:
            return []
        return [c for c in self.controls if c.control_id in control.related_controls]

    def get_reasoning_rules(self, control_id: str | None = None) -> list[ReasoningRule]:
        if control_id:
            return [r for r in self.reasoning if control_id in r.control_ids]
        return self.reasoning

    def model_dump_for_export(self) -> dict[str, Any]:
        return self.model_dump(mode="json")
