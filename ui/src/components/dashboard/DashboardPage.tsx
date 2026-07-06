import { useEffect, useState } from "react";
import { Database, FileText, CheckCircle2, AlertTriangle } from "lucide-react";
import StatCard from "../ui/StatCard";
import PipelineViz from "./PipelineViz";
import ActivityFeed from "./ActivityFeed";
import { fetchStats } from "../../lib/api";
import type { PackStats } from "../../lib/api";

export default function DashboardPage() {
  const [stats, setStats] = useState<PackStats | null>(null);

  useEffect(() => {
    fetchStats("iso27001").then(setStats).catch(() => {});
  }, []);

  return (
    <div className="animate-fade-in p-6">
      <div className="mb-8">
        <h1 className="font-display text-2xl font-bold text-surface-50">
          Dashboard
        </h1>
        <p className="mt-1 text-sm text-surface-400">
          Compliance AI Factory — Dataset Generation Pipeline
        </p>
      </div>

      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Knowledge Packs"
          value="1"
          subtitle={stats ? "ISO/IEC 27001:2022 loaded" : "Loading..."}
          icon={FileText}
        />
        <StatCard
          title="Controls"
          value={stats ? stats.total_controls : "—"}
          subtitle={stats ? "37 Organizational · 8 People · 14 Physical · 34 Tech" : "Loading..."}
          icon={CheckCircle2}
        />
        <StatCard
          title="Evidence Reqs"
          value={stats ? stats.total_evidence : "—"}
          subtitle={stats ? "10 management · 9 technical · 1 physical" : "Loading..."}
          icon={Database}
        />
        <StatCard
          title="Reasoning Rules"
          value={stats ? stats.total_reasoning_rules : "—"}
          subtitle={stats ? `${stats.total_cross_references} cross-references` : "Loading..."}
          icon={AlertTriangle}
        />
      </div>

      <div className="mb-8">
        <PipelineViz />
      </div>

      <div>
        <ActivityFeed />
      </div>
    </div>
  );
}
