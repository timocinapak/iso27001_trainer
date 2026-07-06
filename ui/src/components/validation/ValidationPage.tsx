import { useState, useEffect } from "react";
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ChevronDown,
  ChevronRight,
  Search,
  Loader2,
  Play,
  FileText,
} from "lucide-react";
import Badge from "../ui/Badge";
import { cn } from "../../lib/utils";
import { getGenerationHistory, startValidation, getValidationStatus } from "../../lib/api";
import type { JobStatus } from "../../lib/api";

interface ValidationCheck {
  name: string;
  status: "passed" | "failed" | "warning";
  message?: string;
}

function ValidationCard({
  result,
  expanded,
  onToggle,
}: {
  result: { sample_id: string; status: string; checks: ValidationCheck[] };
  expanded: boolean;
  onToggle: () => void;
}) {
  const passed = result.checks.filter((c) => c.status === "passed").length;
  const total = result.checks.length;

  return (
    <div className="rounded-xl border border-surface-700/60 bg-surface-800/30 backdrop-blur transition-all hover:border-surface-600/60">
      <button
        onClick={onToggle}
        className="flex w-full items-center gap-4 px-5 py-3.5 text-left"
      >
        <div
          className={cn(
            "flex h-8 w-8 items-center justify-center rounded-lg",
            result.status === "passed" && "bg-emerald-500/10",
            result.status === "failed" && "bg-red-500/10",
            result.status === "warning" && "bg-amber-500/10"
          )}
        >
          {result.status === "passed" && (
            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
          )}
          {result.status === "failed" && (
            <XCircle className="h-4 w-4 text-red-400" />
          )}
          {result.status === "warning" && (
            <AlertTriangle className="h-4 w-4 text-amber-400" />
          )}
        </div>

        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="font-mono text-[11px] text-surface-500">
              {result.sample_id}
            </span>
            <Badge
              variant={
                result.status === "passed"
                  ? "success"
                  : result.status === "failed"
                    ? "danger"
                    : "warning"
              }
            >
              {result.status}
            </Badge>
          </div>
          <p className="mt-0.5 text-[13px] text-surface-400">
            {passed}/{total} checks passed
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex gap-1">
            {result.checks.map((check, i) => (
              <div
                key={i}
                className={cn(
                  "h-1.5 w-4 rounded-full",
                  check.status === "passed" && "bg-emerald-500/50",
                  check.status === "failed" && "bg-red-500/50",
                  check.status === "warning" && "bg-amber-500/50"
                )}
              />
            ))}
          </div>
          {expanded ? (
            <ChevronDown className="h-3.5 w-3.5 text-surface-500" />
          ) : (
            <ChevronRight className="h-3.5 w-3.5 text-surface-500" />
          )}
        </div>
      </button>

      {expanded && (
        <div className="animate-slide-up border-t border-surface-700/40 px-5 py-4">
          <div className="space-y-2">
            {result.checks.map((check, i) => (
              <div
                key={i}
                className="flex items-center justify-between rounded-lg bg-surface-900/30 px-3 py-2"
              >
                <div className="flex items-center gap-2">
                  {check.status === "passed" && (
                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                  )}
                  {check.status === "failed" && (
                    <XCircle className="h-3.5 w-3.5 text-red-400" />
                  )}
                  {check.status === "warning" && (
                    <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />
                  )}
                  <span className="text-[13px] text-surface-300">{check.name}</span>
                </div>
                <Badge
                  variant={
                    check.status === "passed"
                      ? "success"
                      : check.status === "failed"
                        ? "danger"
                        : "warning"
                  }
                >
                  {check.status}
                </Badge>
              </div>
            ))}
            {result.checks.filter((c) => c.message).length > 0 && (
              <div className="mt-2 space-y-1">
                {result.checks.filter((c) => c.message).map((c, i) => (
                  <p key={i} className="text-[12px] text-surface-500 italic">
                    {c.message}
                  </p>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default function ValidationPage() {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [filter, setFilter] = useState<"all" | "passed" | "failed" | "warning">("all");
  const [search, setSearch] = useState("");
  const [datasetIds, setDatasetIds] = useState<string[]>([]);
  const [selectedDataset, setSelectedDataset] = useState<string>("");
  const [validationResults, setValidationResults] = useState<JobStatus | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);

  useEffect(() => {
    getGenerationHistory().then((jobs) => {
      const ids = jobs
        .filter((j) => j.status === "completed" && j.result?.dataset_id)
        .map((j) => j.result!.dataset_id as string);
      setDatasetIds(ids);
      if (ids.length > 0) setSelectedDataset(ids[0] ?? "");
    }).catch(() => {});
  }, []);

  useEffect(() => {
    if (!currentJobId) return;
    const interval = setInterval(async () => {
      try {
        const job = await getValidationStatus(currentJobId);
        if (job.status === "completed") {
          setValidationResults(job);
          setIsValidating(false);
          setCurrentJobId(null);
          clearInterval(interval);
        } else if (job.status === "failed") {
          setIsValidating(false);
          setCurrentJobId(null);
          clearInterval(interval);
        }
      } catch {
        setIsValidating(false);
        setCurrentJobId(null);
        clearInterval(interval);
      }
    }, 500);
    return () => clearInterval(interval);
  }, [currentJobId]);

  const handleValidate = async () => {
    if (!selectedDataset) return;
    setIsValidating(true);
    try {
      const result = await startValidation(selectedDataset);
      setCurrentJobId(result.job_id);
    } catch {
      setIsValidating(false);
    }
  };

  const summary = validationResults?.result?.summary as Record<string, unknown> | undefined;
  const samples = (validationResults?.result as Record<string, unknown>)?.samples as
    | { sample_id: string; status: string; checks: ValidationCheck[] }[] | undefined;

  const displayResults = samples || [];
  const passedCount = summary?.passed as number || 0;
  const failedCount = summary?.failed as number || 0;

  const filtered = displayResults.filter((r) => {
    const matchesFilter = filter === "all" || r.status === filter;
    const matchesSearch = r.sample_id.toLowerCase().includes(search.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  return (
    <div className="animate-fade-in p-6">
      <div className="mb-8">
        <h1 className="font-display text-2xl font-bold text-surface-50">
          Validation
        </h1>
        <p className="mt-1 text-sm text-surface-400">
          Review dataset quality and compliance validation results
        </p>
      </div>

      <div className="mb-6 grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
            <span className="text-[11px] font-medium uppercase tracking-wider text-emerald-400">
              Passed
            </span>
          </div>
          <p className="mt-1 font-display text-2xl font-bold text-emerald-300">
            {passedCount || "—"}
          </p>
        </div>
        <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-amber-400" />
            <span className="text-[11px] font-medium uppercase tracking-wider text-amber-400">
              Warnings
            </span>
          </div>
          <p className="mt-1 font-display text-2xl font-bold text-amber-300">
            {summary ? (summary.passed as number) - (summary.failed as number) || "—" : "—"}
          </p>
        </div>
        <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-4">
          <div className="flex items-center gap-2">
            <XCircle className="h-4 w-4 text-red-400" />
            <span className="text-[11px] font-medium uppercase tracking-wider text-red-400">
              Failed
            </span>
          </div>
          <p className="mt-1 font-display text-2xl font-bold text-red-300">
            {failedCount || "—"}
          </p>
        </div>
      </div>

      <div className="mb-4 flex items-center gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-surface-500" />
          <input
            type="text"
            placeholder="Search samples..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-lg border border-surface-700/60 bg-surface-800/50 py-2.5 pl-9 pr-4 text-sm text-surface-200 placeholder-surface-500 backdrop-blur transition-colors focus:border-emerald-500/30 focus:outline-none focus:ring-1 focus:ring-emerald-500/20"
          />
        </div>

        <div className="flex items-center gap-2">
          <select
            value={selectedDataset}
            onChange={(e) => setSelectedDataset(e.target.value)}
            className="rounded-lg border border-surface-700/60 bg-surface-800/50 px-3 py-2.5 text-[13px] text-surface-200 backdrop-blur"
          >
            {datasetIds.length === 0 && <option value="">No datasets</option>}
            {datasetIds.map((id) => (
              <option key={id} value={id}>{id}</option>
            ))}
          </select>

          <button
            onClick={handleValidate}
            disabled={isValidating || !selectedDataset}
            className={cn(
              "flex items-center gap-2 rounded-lg px-4 py-2.5 text-[13px] font-medium transition-all",
              isValidating || !selectedDataset
                ? "cursor-not-allowed bg-surface-700 text-surface-500"
                : "bg-amber-500 text-white hover:bg-amber-600"
            )}
          >
            {isValidating ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Play className="h-3.5 w-3.5" />
            )}
            {isValidating ? "Validating..." : "Validate"}
          </button>
        </div>

        <div className="flex gap-1">
          {(["all", "passed", "failed", "warning"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={cn(
                "rounded-lg px-3 py-2 text-[13px] font-medium transition-all",
                filter === f
                  ? "bg-surface-700/50 text-surface-200 ring-1 ring-surface-600/50"
                  : "text-surface-500 hover:text-surface-300"
              )}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-3">
        {validationResults === null ? (
          <div className="flex flex-col items-center justify-center py-16 text-surface-500">
            <FileText className="mb-3 h-8 w-8" />
            <p className="text-sm">Select a dataset and click Validate to see results</p>
          </div>
        ) : filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-surface-500">
            <CheckCircle2 className="mb-3 h-8 w-8" />
            <p className="text-sm">No matching validation results</p>
          </div>
        ) : (
          filtered.map((result) => (
            <ValidationCard
              key={result.sample_id}
              result={result}
              expanded={expandedId === result.sample_id}
              onToggle={() =>
                setExpandedId(
                  expandedId === result.sample_id ? null : result.sample_id
                )
              }
            />
          ))
        )}
      </div>
    </div>
  );
}
