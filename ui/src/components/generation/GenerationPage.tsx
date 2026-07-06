import { useEffect, useState, useMemo } from "react";
import {
  Sparkles,
  Loader2,
  CheckCircle2,
  XCircle,
  ChevronDown,
  ChevronRight,
} from "lucide-react";
import Badge from "../ui/Badge";
import { cn } from "../../lib/utils";
import { fetchControls, startGeneration, getGenerationStatus, getGenerationHistory } from "../../lib/api";
import type { JobStatus } from "../../lib/api";

const industries = [
  "technology",
  "finance",
  "healthcare",
  "manufacturing",
  "retail",
  "energy",
  "government",
  "education",
];

const difficulties = ["basic", "intermediate", "advanced", "expert"];

const maturityLevels = ["initial", "repeatable", "defined", "managed", "optimizing"];

const sampleSizes = [50, 100, 250, 500, 1000];

const clauseLabels: Record<string, string> = {
  "5": "Clause 5 — Information Security Policies",
  "6": "Clause 6 — Organization of Information Security",
  "7": "Clause 7 — Human Resource Security",
  "8": "Clause 8 — Asset Management",
};

export default function GenerationPage() {
  const [controls, setControls] = useState<{ id: string; title: string; clause: string }[]>([]);
  const [selectedIndustry, setSelectedIndustry] = useState("technology");
  const [selectedDifficulty, setSelectedDifficulty] = useState("intermediate");
  const [selectedMaturity, setSelectedMaturity] = useState("defined");
  const [selectedControls, setSelectedControls] = useState<string[]>([
    "A.5.1",
    "A.8.8",
    "A.8.13",
  ]);
  const [sampleSize, setSampleSize] = useState(250);
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [recentJobs, setRecentJobs] = useState<JobStatus[]>([]);
  const [expandedClauses, setExpandedClauses] = useState<Set<string>>(new Set(["5", "6", "7", "8"]));

  const grouped = useMemo(() => {
    const map: Record<string, { id: string; title: string; clause: string }[]> = {};
    for (const c of controls) {
      const cls = c.clause;
      if (!map[cls]) map[cls] = [];
      map[cls].push(c);
    }
    const sorted = Object.entries(map).sort(([a], [b]) => a.localeCompare(b));
    return sorted.map(([clause, items]) => ({
      clause,
      label: clauseLabels[clause] || `Clause ${clause}`,
      items,
      selectedCount: items.filter((i) => selectedControls.includes(i.id)).length,
    }));
  }, [controls, selectedControls]);

  useEffect(() => {
    fetchControls("iso27001")
      .then((data) =>
        setControls(data.map((c) => ({ id: c.control_id, title: c.title, clause: c.clause })))
      )
      .catch(() => {});
    loadHistory();
  }, []);

  const loadHistory = () => {
    getGenerationHistory()
      .then(setRecentJobs)
      .catch(() => {});
  };

  useEffect(() => {
    if (!currentJobId) return;
    const interval = setInterval(async () => {
      try {
        const job = await getGenerationStatus(currentJobId);
        setProgress(job.progress);
        if (job.status === "completed") {
          setIsRunning(false);
          setCurrentJobId(null);
          setProgress(100);
          loadHistory();
          clearInterval(interval);
        } else if (job.status === "failed") {
          setIsRunning(false);
          setCurrentJobId(null);
          setError(job.error || "Generation failed");
          clearInterval(interval);
        }
      } catch {
        setIsRunning(false);
        setCurrentJobId(null);
        setError("Failed to poll job status");
        clearInterval(interval);
      }
    }, 500);
    return () => clearInterval(interval);
  }, [currentJobId]);

  const toggleControl = (id: string) => {
    setSelectedControls((prev) =>
      prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]
    );
  };

  const selectAll = () => {
    setSelectedControls(controls.map((c) => c.id));
  };

  const deselectAll = () => {
    setSelectedControls([]);
  };

  const selectClause = (clause: string) => {
    const ids = controls.filter((c) => c.clause === clause).map((c) => c.id);
    setSelectedControls((prev) => {
      const allSelected = ids.every((id) => prev.includes(id));
      if (allSelected) {
        return prev.filter((id) => !ids.includes(id));
      }
      const existing = new Set(prev);
      for (const id of ids) existing.add(id);
      return Array.from(existing);
    });
  };

  const toggleClause = (clause: string) => {
    setExpandedClauses((prev) => {
      const next = new Set(prev);
      if (next.has(clause)) next.delete(clause);
      else next.add(clause);
      return next;
    });
  };

  const handleGenerate = async () => {
    setError(null);
    setIsRunning(true);
    setProgress(0);
    try {
      const result = await startGeneration({
        standard: "iso27001",
        industry: selectedIndustry,
        maturity: selectedMaturity,
        difficulty: selectedDifficulty,
        controls: selectedControls,
        samples_per_control: sampleSize,
      });
      setCurrentJobId(result.job_id);
    } catch (e) {
      setIsRunning(false);
      setError(e instanceof Error ? e.message : "Failed to start generation");
    }
  };

  return (
    <div className="animate-fade-in p-6">
      <div className="mb-8">
        <h1 className="font-display text-2xl font-bold text-surface-50">
          Generate Dataset
        </h1>
        <p className="mt-1 text-sm text-surface-400">
          Configure and run the dataset generation pipeline
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <div className="rounded-xl border border-surface-700/60 bg-surface-800/50 backdrop-blur">
            <div className="flex items-center gap-3 border-b border-surface-700/60 px-5 py-3.5">
              <div className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-500/10 text-[11px] font-bold text-emerald-400">
                1
              </div>
              <h2 className="font-display text-sm font-semibold text-surface-200">
                Scenario Configuration
              </h2>
              <Badge variant="info">Organization Profile</Badge>
            </div>
            <div className="p-5 space-y-5">
              <div>
                <p className="mb-2 text-[11px] font-medium uppercase tracking-wider text-surface-500">
                  Industry
                </p>
                <div className="flex flex-wrap gap-2">
                  {industries.map((ind) => (
                    <button
                      key={ind}
                      onClick={() => setSelectedIndustry(ind)}
                      className={cn(
                        "rounded-lg px-3 py-1.5 text-[13px] font-medium transition-all",
                        selectedIndustry === ind
                          ? "bg-emerald-500/10 text-emerald-400 ring-1 ring-emerald-500/20"
                          : "bg-surface-700/30 text-surface-400 hover:bg-surface-700/50 hover:text-surface-300"
                      )}
                    >
                      {ind}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <p className="mb-2 text-[11px] font-medium uppercase tracking-wider text-surface-500">
                  Security Maturity
                </p>
                <div className="flex gap-2">
                  {maturityLevels.map((mat) => (
                    <button
                      key={mat}
                      onClick={() => setSelectedMaturity(mat)}
                      className={cn(
                        "rounded-lg px-3 py-1.5 text-[13px] font-medium transition-all",
                        selectedMaturity === mat
                          ? "bg-amber-500/10 text-amber-400 ring-1 ring-amber-500/20"
                          : "bg-surface-700/30 text-surface-400 hover:bg-surface-700/50 hover:text-surface-300"
                      )}
                    >
                      {mat}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <p className="mb-2 text-[11px] font-medium uppercase tracking-wider text-surface-500">
                  Difficulty
                </p>
                <div className="flex gap-2">
                  {difficulties.map((diff) => (
                    <button
                      key={diff}
                      onClick={() => setSelectedDifficulty(diff)}
                      className={cn(
                        "rounded-lg px-3 py-1.5 text-[13px] font-medium transition-all",
                        selectedDifficulty === diff
                          ? "bg-purple-500/10 text-purple-400 ring-1 ring-purple-500/20"
                          : "bg-surface-700/30 text-surface-400 hover:bg-surface-700/50 hover:text-surface-300"
                      )}
                    >
                      {diff}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-surface-700/60 bg-surface-800/50 backdrop-blur">
            <div className="flex items-center gap-3 border-b border-surface-700/60 px-5 py-3.5">
              <div className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-500/10 text-[11px] font-bold text-emerald-400">
                2
              </div>
              <h2 className="font-display text-sm font-semibold text-surface-200">
                Select Controls
              </h2>
              <Badge variant="success">{selectedControls.length} selected</Badge>
              <div className="ml-auto flex gap-1">
                <button
                  onClick={selectAll}
                  className="rounded px-2 py-1 text-[11px] font-medium text-emerald-400 hover:bg-emerald-500/10 transition-colors"
                >
                  Select All
                </button>
                <button
                  onClick={deselectAll}
                  className="rounded px-2 py-1 text-[11px] font-medium text-surface-500 hover:bg-surface-700/50 transition-colors"
                >
                  Clear
                </button>
              </div>
            </div>
            <div className="divide-y divide-surface-700/40">
              {grouped.map(({ clause, label, items, selectedCount }) => {
                const isExpanded = expandedClauses.has(clause);
                const isFullySelected = selectedCount === items.length;
                return (
                  <div key={clause}>
                    <div
                      className="flex cursor-pointer items-center gap-2 px-5 py-2.5 transition-colors hover:bg-surface-800/40"
                      onClick={() => toggleClause(clause)}
                    >
                      {isExpanded ? (
                        <ChevronDown className="h-3.5 w-3.5 text-surface-500" />
                      ) : (
                        <ChevronRight className="h-3.5 w-3.5 text-surface-500" />
                      )}
                      <span className="text-[13px] font-semibold text-surface-200">
                        {label}
                      </span>
                      <span className="text-[11px] text-surface-500">
                        ({selectedCount}/{items.length})
                      </span>
                      <input
                        type="checkbox"
                        checked={isFullySelected}
                        onChange={(e) => { e.stopPropagation(); selectClause(clause); }}
                        onClick={(e) => e.stopPropagation()}
                        className="ml-auto h-4 w-4 rounded border-surface-600 bg-surface-700 text-emerald-500 focus:ring-emerald-500/20"
                      />
                    </div>
                    {isExpanded && items.map((control) => (
                      <label
                        key={control.id}
                        className="flex cursor-pointer items-center gap-3 px-5 py-2 pl-12 transition-colors hover:bg-surface-800/40"
                      >
                        <input
                          type="checkbox"
                          checked={selectedControls.includes(control.id)}
                          onChange={() => toggleControl(control.id)}
                          className="h-4 w-4 rounded border-surface-600 bg-surface-700 text-emerald-500 focus:ring-emerald-500/20"
                        />
                        <span className="font-mono text-[11px] text-surface-500">
                          {control.id}
                        </span>
                        <span className="text-sm text-surface-300">{control.title}</span>
                      </label>
                    ))}
                  </div>
                );
              })}
            </div>
          </div>

          <div className="rounded-xl border border-surface-700/60 bg-surface-800/50 backdrop-blur">
            <div className="flex items-center gap-3 border-b border-surface-700/60 px-5 py-3.5">
              <div className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-500/10 text-[11px] font-bold text-emerald-400">
                3
              </div>
              <h2 className="font-display text-sm font-semibold text-surface-200">
                Sample Configuration
              </h2>
            </div>
            <div className="p-5">
              <p className="mb-3 text-[11px] font-medium uppercase tracking-wider text-surface-500">
                Samples per Control
              </p>
              <div className="flex gap-2">
                {sampleSizes.map((size) => (
                  <button
                    key={size}
                    onClick={() => setSampleSize(size)}
                    className={cn(
                      "rounded-lg px-4 py-2 text-sm font-medium transition-all",
                      sampleSize === size
                        ? "bg-emerald-500/10 text-emerald-400 ring-1 ring-emerald-500/20"
                        : "bg-surface-700/30 text-surface-400 hover:bg-surface-700/50 hover:text-surface-300"
                    )}
                  >
                    {size}
                  </button>
                ))}
              </div>
              <p className="mt-3 text-[13px] text-surface-500">
                Estimated total:{" "}
                <span className="font-medium text-surface-300">
                  {sampleSize * selectedControls.length}
                </span>{" "}
                samples
              </p>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="rounded-xl border border-surface-700/60 bg-surface-800/50 backdrop-blur">
            <div className="border-b border-surface-700/60 px-5 py-3.5">
              <h2 className="font-display text-sm font-semibold text-surface-200">
                Run Configuration
              </h2>
            </div>
            <div className="space-y-3 p-5">
              <div className="flex items-center justify-between text-[13px]">
                <span className="text-surface-400">Standard</span>
                <span className="font-medium text-surface-200">ISO/IEC 27001:2022</span>
              </div>
              <div className="flex items-center justify-between text-[13px]">
                <span className="text-surface-400">Industry</span>
                <span className="font-medium text-surface-200 capitalize">
                  {selectedIndustry}
                </span>
              </div>
              <div className="flex items-center justify-between text-[13px]">
                <span className="text-surface-400">Maturity</span>
                <span className="font-medium text-surface-200 capitalize">
                  {selectedMaturity}
                </span>
              </div>
              <div className="flex items-center justify-between text-[13px]">
                <span className="text-surface-400">Difficulty</span>
                <span className="font-medium text-surface-200 capitalize">
                  {selectedDifficulty}
                </span>
              </div>
              <div className="flex items-center justify-between text-[13px]">
                <span className="text-surface-400">Controls</span>
                <span className="font-medium text-surface-200">
                  {selectedControls.length}
                </span>
              </div>
              <div className="flex items-center justify-between text-[13px]">
                <span className="text-surface-400">Total Samples</span>
                <span className="font-display text-base font-bold text-emerald-400">
                  {sampleSize * selectedControls.length}
                </span>
              </div>
            </div>
          </div>

          <button
            onClick={handleGenerate}
            disabled={isRunning || selectedControls.length === 0}
            className={cn(
              "flex w-full items-center justify-center gap-2 rounded-lg px-4 py-3 font-medium transition-all",
              isRunning || selectedControls.length === 0
                ? "cursor-not-allowed bg-surface-700 text-surface-500"
                : "bg-emerald-500 text-white shadow-lg shadow-emerald-500/20 hover:bg-emerald-600"
            )}
          >
            {isRunning ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Generating... {progress}%
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                Generate Dataset
              </>
            )}
          </button>

          {isRunning && (
            <div className="h-1.5 overflow-hidden rounded-full bg-surface-700">
              <div
                className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-emerald-400 transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          )}

          {error && (
            <div className="flex items-center gap-2 rounded-lg border border-red-500/20 bg-red-500/5 px-4 py-3">
              <XCircle className="h-4 w-4 text-red-400" />
              <span className="text-[13px] font-medium text-red-400">{error}</span>
            </div>
          )}

          {progress === 100 && !error && (
            <div className="animate-slide-up flex items-center gap-2 rounded-lg border border-emerald-500/20 bg-emerald-500/5 px-4 py-3">
              <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              <span className="text-[13px] font-medium text-emerald-400">
                Dataset generated successfully
              </span>
            </div>
          )}

          {recentJobs.length > 0 && (
            <div className="rounded-xl border border-surface-700/60 bg-surface-800/30 backdrop-blur">
              <div className="border-b border-surface-700/60 px-5 py-3.5">
                <h2 className="font-display text-sm font-semibold text-surface-200">
                  Recent Runs
                </h2>
              </div>
              <div className="divide-y divide-surface-700/40">
                {recentJobs.slice(0, 5).map((job) => (
                  <div key={job.job_id} className="flex items-center justify-between px-5 py-3">
                    <span className="font-mono text-[11px] text-surface-400">{job.job_id}</span>
                    <Badge variant={job.status === "completed" ? "success" : job.status === "running" ? "info" : "danger"}>
                      {job.status}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
