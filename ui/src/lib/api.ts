import type {
  ControlDefinition,
  EvidenceRequirement,
  ReasoningRule,
  CrossReference,
  MaturityMapping,
  IndustryMapping,
} from "../types";

export interface PackStats {
  total_controls: number;
  total_evidence: number;
  total_reasoning_rules: number;
  total_cross_references: number;
  total_terminology: number;
  controls_by_clause: Record<string, number>;
  evidence_by_category: Record<string, number>;
}

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function fetchJson<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) {
    throw new ApiError(res.status, `API ${res.status}: ${res.statusText}`);
  }
  return res.json();
}

export function fetchPacks(): Promise<{ packs: string[] }> {
  return fetchJson("/api/knowledge");
}

export function fetchStats(standard: string): Promise<PackStats> {
  return fetchJson(`/api/knowledge/${standard}/stats`);
}

export function fetchControls(standard: string): Promise<ControlDefinition[]> {
  return fetchJson(`/api/knowledge/${standard}/controls`);
}

export function fetchControl(
  standard: string,
  controlId: string
): Promise<ControlDefinition> {
  return fetchJson(`/api/knowledge/${standard}/controls/${controlId}`);
}

export function fetchEvidence(standard: string): Promise<EvidenceRequirement[]> {
  return fetchJson(`/api/knowledge/${standard}/evidence`);
}

export function fetchReasoning(standard: string): Promise<ReasoningRule[]> {
  return fetchJson(`/api/knowledge/${standard}/reasoning`);
}

export function fetchCrossReferences(standard: string): Promise<CrossReference[]> {
  return fetchJson(`/api/knowledge/${standard}/cross-references`);
}

export function fetchMaturity(standard: string): Promise<MaturityMapping[]> {
  return fetchJson(`/api/knowledge/${standard}/maturity`);
}

export function fetchIndustries(standard: string): Promise<IndustryMapping[]> {
  return fetchJson(`/api/knowledge/${standard}/industries`);
}
