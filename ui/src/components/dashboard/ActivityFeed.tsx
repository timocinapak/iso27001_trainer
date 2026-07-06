import { useState, useEffect } from "react";
import { Clock, CheckCircle2, XCircle, Loader2 } from "lucide-react";
import Badge from "../ui/Badge";
import { cn } from "../../lib/utils";
import { getGenerationHistory } from "../../lib/api";

const statusConfig = {
  completed: { icon: CheckCircle2, variant: "success" as const, label: "Completed" },
  running: { icon: Loader2, variant: "info" as const, label: "Running" },
  failed: { icon: XCircle, variant: "danger" as const, label: "Failed" },
};

export default function ActivityFeed() {
  const [runs, setRuns] = useState<{ id: string; status: string; details?: string }[]>([]);

  useEffect(() => {
    getGenerationHistory()
      .then((jobs) =>
        setRuns(
          jobs.map((j) => ({
            id: j.job_id,
            status: j.status,
            details: j.type,
          }))
        )
      )
      .catch(() => {});
  }, []);

  if (runs.length === 0) {
    return (
      <div className="rounded-xl border border-surface-700/60 bg-surface-800/50 backdrop-blur">
        <div className="flex items-center justify-between border-b border-surface-700/60 px-5 py-3.5">
          <h2 className="font-display text-sm font-semibold text-surface-200">
            Recent Generation Runs
          </h2>
          <Clock className="h-3.5 w-3.5 text-surface-500" />
        </div>
        <div className="flex items-center justify-center py-12">
          <p className="text-sm text-surface-500">No generation runs yet</p>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-surface-700/60 bg-surface-800/50 backdrop-blur">
      <div className="flex items-center justify-between border-b border-surface-700/60 px-5 py-3.5">
        <h2 className="font-display text-sm font-semibold text-surface-200">
          Recent Generation Runs
        </h2>
        <Clock className="h-3.5 w-3.5 text-surface-500" />
      </div>

      <div className="divide-y divide-surface-700/40">
        {runs.slice(0, 10).map((run) => {
          const config = statusConfig[run.status as keyof typeof statusConfig] || statusConfig.completed;
          const StatusIcon = config.icon;
          const isRunning = run.status === "running";

          return (
            <div
              key={run.id}
              className="flex items-center justify-between px-5 py-3.5 transition-colors hover:bg-surface-800/40"
            >
              <div className="flex items-center gap-3">
                <StatusIcon
                  className={cn(
                    "h-4 w-4",
                    run.status === "completed" && "text-emerald-400",
                    run.status === "running" && "animate-spin text-blue-400",
                    run.status === "failed" && "text-red-400"
                  )}
                />
                <div>
                  <p className="text-sm font-medium text-surface-200">
                    {run.id}
                  </p>
                  <p className="text-[11px] text-surface-500">
                    {run.details || "generation"}
                  </p>
                </div>
              </div>

              <Badge
                variant={config.variant}
                className={cn(isRunning && "animate-pulse")}
              >
                {config.label}
              </Badge>
            </div>
          );
        })}
      </div>
    </div>
  );
}
