import { cn } from "../../lib/utils";
import { pipelineSteps } from "../../data/knowledge";
import {
  BookOpen,
  Building2,
  CheckSquare,
  HelpCircle,
  MessageSquare,
  FileText,
  Scale,
  Search,
  Lightbulb,
  Brain,
  Shield,
  Download,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import type { PipelineStage } from "../../types";

const iconMap: Record<PipelineStage, LucideIcon> = {
  knowledge_pack: BookOpen,
  scenario: Building2,
  control: CheckSquare,
  question: HelpCircle,
  answer: MessageSquare,
  evidence: FileText,
  decision: Scale,
  finding: Search,
  recommendation: Lightbulb,
  reasoning: Brain,
  validation: Shield,
  export: Download,
};

const stageGroups = [
  pipelineSteps.slice(0, 3),
  pipelineSteps.slice(3, 6),
  pipelineSteps.slice(6, 10),
  pipelineSteps.slice(10),
];

export default function PipelineViz() {
  return (
    <div className="rounded-xl border border-surface-700/60 bg-surface-800/50 p-5 backdrop-blur">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-display text-sm font-semibold text-surface-200">
          Generation Pipeline
        </h2>
        <span className="text-[11px] text-surface-500">
          ISO 27001 → Dataset
        </span>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        {stageGroups.map((group, groupIdx) => (
          <div key={groupIdx} className="space-y-1.5">
            {group.map((step) => {
              const Icon = iconMap[step.id];
              return (
                <div
                  key={step.id}
                  className={cn(
                    "group flex items-center gap-2.5 rounded-lg px-3 py-2 transition-all duration-200",
                    groupIdx === 0
                      ? "hover:bg-emerald-500/5"
                      : groupIdx === 1
                        ? "hover:bg-blue-500/5"
                        : groupIdx === 2
                          ? "hover:bg-amber-500/5"
                          : "hover:bg-emerald-500/5"
                  )}
                >
                  <div
                    className={cn(
                      "flex h-6 w-6 shrink-0 items-center justify-center rounded-md transition-colors",
                      groupIdx === 0
                        ? "bg-emerald-500/10 text-emerald-400"
                        : groupIdx === 1
                          ? "bg-blue-500/10 text-blue-400"
                          : groupIdx === 2
                            ? "bg-amber-500/10 text-amber-400"
                            : "bg-emerald-500/10 text-emerald-400"
                    )}
                  >
                    <Icon className="h-3 w-3" />
                  </div>
                  <div className="min-w-0">
                    <p className="truncate text-[13px] font-medium text-surface-200">
                      {step.label}
                    </p>
                    <p className="truncate text-[10px] text-surface-500">
                      {step.description}
                    </p>
                  </div>
                </div>
              );
            })}
            {groupIdx < stageGroups.length - 1 && (
              <div className="flex justify-center py-0.5">
                <svg
                  className="h-4 w-4 text-surface-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
