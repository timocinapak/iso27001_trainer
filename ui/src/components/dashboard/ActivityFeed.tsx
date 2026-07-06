import { Clock, CheckCircle2, XCircle, Loader2 } from "lucide-react";
import Badge from "../ui/Badge";
import { recentRuns } from "../../data/knowledge";
import { cn } from "../../lib/utils";

const statusConfig = {
  completed: { icon: CheckCircle2, variant: "success" as const, label: "Completed" },
  running: { icon: Loader2, variant: "info" as const, label: "Running" },
  failed: { icon: XCircle, variant: "danger" as const, label: "Failed" },
};

export default function ActivityFeed() {
  return (
    <div className="rounded-xl border border-surface-700/60 bg-surface-800/50 backdrop-blur">
      <div className="flex items-center justify-between border-b border-surface-700/60 px-5 py-3.5">
        <h2 className="font-display text-sm font-semibold text-surface-200">
          Recent Generation Runs
        </h2>
        <Clock className="h-3.5 w-3.5 text-surface-500" />
      </div>

      <div className="divide-y divide-surface-700/40">
        {recentRuns.map((run) => {
          const config = statusConfig[run.status];
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
                    {run.id} — {run.industry}
                  </p>
                  <p className="text-[11px] text-surface-500">
                    {run.standard} · {run.control_count} controls ·{" "}
                    {run.sample_count} samples · {run.difficulty}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                {isRunning && (
                  <div className="flex items-center gap-2">
                    <div className="h-1.5 w-16 overflow-hidden rounded-full bg-surface-700">
                      <div
                        className="h-full rounded-full bg-blue-400 transition-all"
                        style={{ width: `${run.progress}%` }}
                      />
                    </div>
                    <span className="text-[11px] text-blue-400">
                      {run.progress}%
                    </span>
                  </div>
                )}
                <Badge
                  variant={config.variant}
                  className={cn(isRunning && "animate-pulse")}
                >
                  {config.label}
                </Badge>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
