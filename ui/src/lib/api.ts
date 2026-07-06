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

export interface JobStatus {
  job_id: string;
  type: string;
  status: "running" | "completed" | "failed";
  progress: number;
  created_at: string;
  result?: Record<string, unknown>;
  error?: string;
}

export interface GenerateResponse {
  job_id: string;
  status: string;
  scenario_id: string;
  total_samples: number;
}

export interface ValidateResponse {
  job_id: string;
  status: string;
  dataset_id: string;
  total_samples: number;
}

export interface ExportResult {
  export_id: string;
  format: string;
  sample_count: number;
  path: string;
  metadata: Record<string, unknown>;
}

export interface ScenarioResponse {
  scenario: {
    id: string;
    organization: {
      name: string;
      industry: string;
      size: string;
      maturity: string;
      description: string;
      departments: string[];
    };
  };
  path: string;
}

export interface ConfigData {
  industries: string[];
  difficulties: string[];
  maturity_levels: string[];
  sample_sizes: number[];
  controls: { control_id: string; title: string }[];
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

async function postJson<T>(url: string, body: unknown): Promise<T> {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, err.detail || `API ${res.status}`);
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

export function fetchConfig(): Promise<ConfigData> {
  return fetchJson("/api/config");
}

export function generateScenario(): Promise<ScenarioResponse> {
  return postJson("/api/scenario/generate", {});
}

export function startGeneration(config: {
  standard: string;
  industry: string;
  maturity: string;
  difficulty: string;
  controls: string[];
  samples_per_control: number;
}): Promise<GenerateResponse> {
  return postJson("/api/generate", config);
}

export function getGenerationStatus(jobId: string): Promise<JobStatus> {
  return fetchJson(`/api/generate/${jobId}`);
}

export function getGenerationHistory(): Promise<JobStatus[]> {
  return fetchJson("/api/generate/history");
}

export function startValidation(datasetId: string): Promise<ValidateResponse> {
  return postJson("/api/validate", { dataset_id: datasetId, standard: "iso27001" });
}

export function getValidationStatus(jobId: string): Promise<JobStatus> {
  return fetchJson(`/api/validate/${jobId}`);
}

export function getValidationHistory(): Promise<JobStatus[]> {
  return fetchJson("/api/validate/history");
}

export function startExport(datasetId: string, format: string): Promise<ExportResult> {
  return postJson("/api/export", { dataset_id: datasetId, format });
}

export function getExportHistory(): Promise<ExportResult[]> {
  return fetchJson("/api/export/history");
}
