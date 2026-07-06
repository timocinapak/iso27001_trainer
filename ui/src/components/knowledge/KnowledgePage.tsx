import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { BookOpen, Layers, FileText, Shield, Loader2 } from "lucide-react";
import Badge from "../ui/Badge";
import { cn } from "../../lib/utils";
import { fetchPacks, fetchStats } from "../../lib/api";
import type { PackStats } from "../../lib/api";

const clauseMeta: Record<string, { label: string; color: string }> = {
  "5": { label: "Organizational", color: "text-emerald-400" },
  "6": { label: "People", color: "text-blue-400" },
  "7": { label: "Physical", color: "text-amber-400" },
  "8": { label: "Technological", color: "text-purple-400" },
};

export default function KnowledgePage() {
  const navigate = useNavigate();
  const [stats, setStats] = useState<PackStats | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const [packsRes, statsData] = await Promise.all([
          fetchPacks(),
          fetchStats("iso27001"),
        ]);
        if (cancelled) return;
        if (!packsRes.packs.includes("iso27001")) {
          setError("ISO 27001 Knowledge Pack not found");
          return;
        }
        setStats(statsData);
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
  }, []);

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
        <Shield className="h-8 w-8 text-red-400" />
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

  const _stats = stats!;

  const statCards = [
    { label: "Controls", value: _stats.total_controls, icon: Layers, color: "text-emerald-400" },
    { label: "Evidence Reqs", value: _stats.total_evidence, icon: FileText, color: "text-blue-400" },
    { label: "Reasoning Rules", value: _stats.total_reasoning_rules, icon: Shield, color: "text-amber-400" },
    { label: "Cross-References", value: _stats.total_cross_references, icon: BookOpen, color: "text-purple-400" },
  ];

  const clauseGroups = Object.entries(_stats.controls_by_clause).map(
    ([id, count]) => ({
      id,
      label: clauseMeta[id]?.label ?? `Clause ${id}`,
      count,
    })
  );

  return (
    <div className="animate-fade-in p-6">
      <div className="mb-8">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="font-display text-2xl font-bold text-surface-50">
              Knowledge Packs
            </h1>
            <p className="mt-1 text-sm text-surface-400">
              Browse and inspect compliance framework knowledge
            </p>
          </div>
          <Badge variant="success">1 Pack Loaded</Badge>
        </div>
      </div>

      <div
        onClick={() => navigate("/knowledge/iso27001")}
        className="group mb-8 cursor-pointer rounded-xl border border-surface-700/60 bg-surface-800/50 p-5 backdrop-blur transition-all hover:border-emerald-500/30 hover:bg-surface-800"
      >
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-500/10 ring-1 ring-emerald-500/20">
              <BookOpen className="h-6 w-6 text-emerald-400" />
            </div>
            <div>
              <h2 className="font-display text-lg font-semibold text-surface-50 group-hover:text-emerald-400 transition-colors">
                ISO/IEC 27001
              </h2>
              <p className="mt-0.5 text-sm text-surface-400">
                Version 2022 · Released 2022-10-25
              </p>
              <p className="mt-1.5 max-w-2xl text-[13px] leading-relaxed text-surface-500">
                Information security, cybersecurity and privacy protection — Information security management systems — Requirements
              </p>
            </div>
          </div>
          <Badge variant="info">ISO</Badge>
        </div>

        <div className="mt-5 grid grid-cols-4 gap-4">
          {statCards.map((stat) => (
            <div
              key={stat.label}
              className="rounded-lg bg-surface-900/50 p-3 ring-1 ring-surface-700/50"
            >
              <div className="flex items-center gap-2">
                <stat.icon className={cn("h-3.5 w-3.5", stat.color)} />
                <span className="text-[11px] font-medium uppercase tracking-wider text-surface-500">
                  {stat.label}
                </span>
              </div>
              <p className="mt-1 font-display text-xl font-bold text-surface-200">
                {stat.value}
              </p>
            </div>
          ))}
        </div>
      </div>

      <div className="rounded-xl border border-surface-700/60 bg-surface-800/50 backdrop-blur">
        <div className="border-b border-surface-700/60 px-5 py-3.5">
          <h2 className="font-display text-sm font-semibold text-surface-200">
            Control Clauses
          </h2>
        </div>
        <div className="divide-y divide-surface-700/40">
          {clauseGroups.map((group) => (
            <div
              key={group.id}
              className="flex items-center justify-between px-5 py-3.5 transition-colors hover:bg-surface-800/40"
            >
              <div className="flex items-center gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-surface-700/50 text-xs font-bold text-surface-300">
                  {group.id}
                </div>
                <span className="text-sm font-medium text-surface-200">
                  {group.label}
                </span>
              </div>
              <span className="text-sm text-surface-400">
                {group.count} controls
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
