import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  Search,
  ChevronDown,
  ChevronRight,
  FileText,
  Brain,
  CheckCircle2,
  AlertTriangle,
  Loader2,
} from "lucide-react";
import Badge from "../ui/Badge";
import { cn } from "../../lib/utils";
import { fetchControls, fetchEvidence, fetchReasoning } from "../../lib/api";
import type { ControlDefinition, EvidenceRequirement, ReasoningRule } from "../../types";

const clauseColors: Record<string, string> = {
  "5": "border-l-emerald-500/50",
  "6": "border-l-blue-500/50",
  "7": "border-l-amber-500/50",
  "8": "border-l-purple-500/50",
};

const clauseBadges: Record<string, { label: string; variant: "success" | "info" | "warning" | "danger" }> = {
  "5": { label: "Organizational", variant: "success" },
  "6": { label: "People", variant: "info" },
  "7": { label: "Physical", variant: "warning" },
  "8": { label: "Technological", variant: "danger" },
};

const implementationColors: Record<string, string> = {
  foundational: "bg-emerald-500/10 text-emerald-400 ring-emerald-500/20",
  intermediate: "bg-amber-500/10 text-amber-400 ring-amber-500/20",
  advanced: "bg-purple-500/10 text-purple-400 ring-purple-500/20",
};

function ControlCard({
  control,
  expanded,
  onToggle,
}: {
  control: ControlDefinition;
  expanded: boolean;
  onToggle: () => void;
}) {
  const clauseInfo = clauseBadges[control.clause] ?? {
    label: "Unknown",
    variant: "default" as const,
  };
  const implLevel = control.attributes.find((a) => a.name === "implementation_level")
    ?.value ?? "foundational";

  return (
    <div
      className={cn(
        "border-l-2 transition-all",
        clauseColors[control.clause] ?? "border-l-surface-600/50"
      )}
    >
      <button
        onClick={onToggle}
        className="flex w-full items-center gap-3 px-5 py-3.5 text-left transition-colors hover:bg-surface-800/40"
      >
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-surface-700/50">
          <span className="font-mono text-[11px] font-medium text-surface-300">
            {control.control_id.replace("A.", "")}
          </span>
        </div>
        <div className="flex-1 min-w-0">
          <p className="truncate text-sm font-medium text-surface-200">
            {control.title}
          </p>
          <p className="truncate text-[11px] text-surface-500">
            {control.objective}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={cn(
              "rounded-full px-2 py-0.5 text-[10px] font-medium ring-1 ring-inset",
              implementationColors[implLevel] ?? implementationColors.foundational
            )}
          >
            {implLevel}
          </span>
          <Badge variant={clauseInfo.variant}>{clauseInfo.label}</Badge>
          {expanded ? (
            <ChevronDown className="h-3.5 w-3.5 text-surface-500" />
          ) : (
            <ChevronRight className="h-3.5 w-3.5 text-surface-500" />
          )}
        </div>
      </button>

      {expanded && (
        <div className="animate-slide-up border-t border-surface-700/40 px-5 py-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <h4 className="mb-1 text-[11px] font-medium uppercase tracking-wider text-surface-500">
                Description
              </h4>
              <p className="text-[13px] leading-relaxed text-surface-300">
                {control.description}
              </p>
            </div>
            <div>
              <h4 className="mb-1 text-[11px] font-medium uppercase tracking-wider text-surface-500">
                Audit Intent
              </h4>
              <p className="text-[13px] leading-relaxed text-surface-300">
                {control.audit_intent}
              </p>
            </div>
          </div>

          {control.implementation_guidance.length > 0 && (
            <div className="mt-4">
              <h4 className="mb-2 text-[11px] font-medium uppercase tracking-wider text-surface-500">
                Implementation Guidance
              </h4>
              <ul className="space-y-1">
                {control.implementation_guidance.map((item, i) => (
                  <li
                    key={i}
                    className="flex items-start gap-2 text-[13px] text-surface-400"
                  >
                    <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-surface-600" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {control.expected_outcomes.length > 0 && (
            <div className="mt-4">
              <h4 className="mb-2 text-[11px] font-medium uppercase tracking-wider text-surface-500">
                Expected Outcomes
              </h4>
              <div className="flex flex-wrap gap-2">
                {control.expected_outcomes.map((outcome, i) => (
                  <span
                    key={i}
                    className="inline-flex items-center gap-1 rounded-full bg-emerald-500/5 px-2.5 py-1 text-[11px] text-emerald-400 ring-1 ring-emerald-500/10"
                  >
                    <CheckCircle2 className="h-3 w-3" />
                    {outcome}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function PackDetail() {
  const { standard } = useParams();
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"controls" | "evidence" | "reasoning">(
    "controls"
  );
  const [controls, setControls] = useState<ControlDefinition[]>([]);
  const [evidence, setEvidence] = useState<EvidenceRequirement[]>([]);
  const [reasoning, setReasoning] = useState<ReasoningRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const standardName = standard ?? "iso27001";

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [c, e, r] = await Promise.all([
          fetchControls(standardName),
          fetchEvidence(standardName),
          fetchReasoning(standardName),
        ]);
        if (cancelled) return;
        setControls(c);
        setEvidence(e);
        setReasoning(r);
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Failed to load data");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [standardName]);

  const filteredControls = controls.filter(
    (c) =>
      c.control_id.toLowerCase().includes(search.toLowerCase()) ||
      c.title.toLowerCase().includes(search.toLowerCase()) ||
      c.objective.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center p-6">
        <Loader2 className="h-6 w-6 animate-spin text-surface-400" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 p-6">
        <AlertTriangle className="h-8 w-8 text-red-400" />
        <p className="text-sm text-surface-400">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="rounded-lg bg-emerald-500/10 px-3 py-1.5 text-sm text-emerald-400 ring-1 ring-emerald-500/20"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="animate-fade-in p-6">
      <div className="mb-6">
        <button
          onClick={() => navigate("/knowledge")}
          className="mb-3 flex items-center gap-1.5 text-[13px] text-surface-500 transition-colors hover:text-surface-300"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          Back to Knowledge Packs
        </button>
        <h1 className="font-display text-2xl font-bold text-surface-50">
          ISO/IEC 27001
        </h1>
        <p className="mt-1 text-sm text-surface-400">
          Version 2022 · {controls.length} controls
        </p>
      </div>

      <div className="mb-6 flex gap-2">
        {(["controls", "evidence", "reasoning"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={cn(
              "rounded-lg px-4 py-2 text-sm font-medium transition-all",
              activeTab === tab
                ? "bg-emerald-500/10 text-emerald-400 ring-1 ring-emerald-500/20"
                : "text-surface-400 hover:bg-surface-800/60 hover:text-surface-300"
            )}
          >
            {tab === "controls" && `Controls (${controls.length})`}
            {tab === "evidence" && `Evidence (${evidence.length})`}
            {tab === "reasoning" && `Reasoning (${reasoning.length})`}
          </button>
        ))}
      </div>

      {activeTab === "controls" && (
        <>
          <div className="relative mb-4">
            <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-surface-500" />
            <input
              type="text"
              placeholder="Search controls by ID, title, or objective..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-lg border border-surface-700/60 bg-surface-800/50 py-2.5 pl-9 pr-4 text-sm text-surface-200 placeholder-surface-500 backdrop-blur transition-colors focus:border-emerald-500/30 focus:outline-none focus:ring-1 focus:ring-emerald-500/20"
            />
          </div>

          <div className="overflow-hidden rounded-xl border border-surface-700/60 bg-surface-800/30 backdrop-blur">
            {filteredControls.length === 0 ? (
              <div className="flex flex-col items-center py-12 text-surface-500">
                <Search className="mb-2 h-8 w-8" />
                <p className="text-sm">No controls match your search</p>
              </div>
            ) : (
              filteredControls.map((control) => (
                <ControlCard
                  key={control.control_id}
                  control={control}
                  expanded={expandedId === control.control_id}
                  onToggle={() =>
                    setExpandedId(
                      expandedId === control.control_id ? null : control.control_id
                    )
                  }
                />
              ))
            )}
          </div>
        </>
      )}

      {activeTab === "evidence" && (
        <div className="space-y-3">
          {evidence.map((ev) => (
            <div
              key={ev.evidence_id}
              className="rounded-xl border border-surface-700/60 bg-surface-800/30 p-5 backdrop-blur"
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4 text-blue-400" />
                    <h3 className="font-display text-sm font-semibold text-surface-200">
                      {ev.title}
                    </h3>
                    {ev.mandatory && (
                      <Badge variant="danger">Mandatory</Badge>
                    )}
                  </div>
                  <p className="mt-1 text-[13px] text-surface-400">
                    {ev.description}
                  </p>
                </div>
                <Badge variant="info">{ev.category}</Badge>
              </div>

              {ev.typical_documents.length > 0 && (
                <div className="mt-3">
                  <p className="mb-1.5 text-[11px] font-medium uppercase tracking-wider text-surface-500">
                    Typical Documents
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {ev.typical_documents.map((doc, i) => (
                      <span
                        key={i}
                        className="rounded-md bg-surface-700/40 px-2 py-0.5 text-[11px] text-surface-400"
                      >
                        {doc}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {activeTab === "reasoning" && (
        <div className="space-y-3">
          {reasoning.map((rule) => (
            <div
              key={rule.rule_id}
              className="rounded-xl border border-surface-700/60 bg-surface-800/30 p-5 backdrop-blur"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <Brain className="mt-0.5 h-4 w-4 text-amber-400" />
                  <div>
                    <h3 className="font-display text-sm font-semibold text-surface-200">
                      {rule.rule_id} — {rule.description}
                    </h3>
                    <p className="mt-1 font-mono text-[12px] leading-relaxed text-surface-400">
                      {rule.logic}
                    </p>
                  </div>
                </div>
                <Badge
                  variant={
                    rule.severity === "high"
                      ? "danger"
                      : rule.severity === "medium"
                        ? "warning"
                        : "default"
                  }
                >
                  {rule.severity}
                </Badge>
              </div>
              <div className="mt-2 flex items-center gap-2">
                <Badge variant="info">{rule.rule_type}</Badge>
                {rule.control_ids.length > 0 && (
                  <span className="text-[11px] text-surface-500">
                    Applies to: {rule.control_ids.join(", ")}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
