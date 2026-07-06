import { useState } from "react";
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ChevronDown,
  ChevronRight,
  Search,
} from "lucide-react";
import Badge from "../ui/Badge";
import { sampleValidation } from "../../data/knowledge";
import { cn } from "../../lib/utils";
import type { ValidationResult } from "../../types";

function ValidationCard({
  result,
  expanded,
  onToggle,
}: {
  result: ValidationResult;
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

  const filtered = sampleValidation.filter((r) => {
    const matchesFilter = filter === "all" || r.status === filter;
    const matchesSearch = r.sample_id.toLowerCase().includes(search.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const passed = sampleValidation.filter((r) => r.status === "passed").length;
  const failed = sampleValidation.filter((r) => r.status === "failed").length;
  const warnings = sampleValidation.filter((r) => r.status === "warning").length;

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
            {passed}
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
            {warnings}
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
            {failed}
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
        {filtered.map((result) => (
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
        ))}
      </div>
    </div>
  );
}
