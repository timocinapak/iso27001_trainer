export interface StandardMetadata {
  standard_name: string;
  version: string;
  release_date: string;
  publisher: string;
  supported_languages: string[];
  description?: string;
}

export interface ControlDefinition {
  control_id: string;
  clause: string;
  title: string;
  objective: string;
  description: string;
  implementation_guidance: string[];
  expected_outcomes: string[];
  attributes: { name: string; value: string }[];
  related_controls: string[];
  required_evidence: string[];
  audit_intent: string;
}

export interface Terminology {
  term: string;
  definition: string;
  synonyms: string[];
  abbreviations: string[];
}

export interface EvidenceRequirement {
  evidence_id: string;
  title: string;
  description: string;
  category: string;
  control_ids: string[];
  typical_documents: string[];
  system_evidence: string[];
  management_evidence: string[];
  mandatory: boolean;
}

export interface ReasoningRule {
  rule_id: string;
  rule_type: string;
  description: string;
  logic: string;
  control_ids: string[];
  severity: string;
}

export interface CrossReference {
  source_control_id: string;
  target_control_id: string;
  relationship_type: string;
  description?: string;
}

export interface MaturityMapping {
  maturity_level: string;
  description: string;
  expected_controls: string[];
  typical_gaps: string[];
}

export interface IndustryMapping {
  industry: string;
  description: string;
  focus_controls: string[];
  typical_risks: string[];
}

export interface KnowledgePack {
  metadata: StandardMetadata;
  controls: ControlDefinition[];
  terminology: Terminology[];
  evidence: EvidenceRequirement[];
  reasoning: ReasoningRule[];
  cross_references: CrossReference[];
  maturity: MaturityMapping[];
  industries: IndustryMapping[];
}

export type PipelineStage =
  | "knowledge_pack"
  | "scenario"
  | "control"
  | "question"
  | "answer"
  | "evidence"
  | "decision"
  | "finding"
  | "recommendation"
  | "reasoning"
  | "validation"
  | "export";

export interface PipelineStep {
  id: PipelineStage;
  label: string;
  icon: string;
  description: string;
}

export interface GenerationRun {
  id: string;
  standard: string;
  control_count: number;
  sample_count: number;
  difficulty: string;
  industry: string;
  status: "running" | "completed" | "failed";
  progress: number;
  started_at: string;
  completed_at?: string;
}

export interface ValidationResult {
  sample_id: string;
  status: "passed" | "failed" | "warning";
  checks: {
    name: string;
    status: "passed" | "failed" | "warning";
    message?: string;
  }[];
}
