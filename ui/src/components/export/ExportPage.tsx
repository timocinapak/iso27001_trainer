import { useState } from "react";
import {
  Download,
  FileJson,
  FileSpreadsheet,
  Database,
  FileText,
  CheckCircle2,
  Clock,
} from "lucide-react";
import Badge from "../ui/Badge";
import { cn } from "../../lib/utils";

const formats = [
  { id: "jsonl", label: "JSONL", icon: FileJson, description: "Line-delimited JSON, ideal for LLM fine-tuning" },
  { id: "json", label: "JSON", icon: FileJson, description: "Structured JSON array format" },
  { id: "csv", label: "CSV", icon: FileSpreadsheet, description: "Tabular format for spreadsheet applications" },
  { id: "markdown", label: "Markdown", icon: FileText, description: "Human-readable documentation format" },
  { id: "parquet", label: "Parquet", icon: Database, description: "Columnar storage for large-scale processing" },
];

const exportHistory = [
  { id: "EXP-001", format: "JSONL", samples: 1200, status: "completed", date: "2026-07-05" },
  { id: "EXP-002", format: "CSV", samples: 500, status: "completed", date: "2026-07-04" },
  { id: "EXP-003", format: "Parquet", samples: 2400, status: "completed", date: "2026-07-03" },
];

export default function ExportPage() {
  const [selectedFormat, setSelectedFormat] = useState("jsonl");
  const [includeMeta, setIncludeMeta] = useState(true);
  const [isExporting, setIsExporting] = useState(false);
  const [exportDone, setExportDone] = useState(false);

  const handleExport = () => {
    setIsExporting(true);
    setTimeout(() => {
      setIsExporting(false);
      setExportDone(true);
    }, 2000);
  };

  return (
    <div className="animate-fade-in p-6">
      <div className="mb-8">
        <h1 className="font-display text-2xl font-bold text-surface-50">
          Export
        </h1>
        <p className="mt-1 text-sm text-surface-400">
          Export validated datasets to your preferred format
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="space-y-6">
          <div className="rounded-xl border border-surface-700/60 bg-surface-800/50 backdrop-blur">
            <div className="border-b border-surface-700/60 px-5 py-3.5">
              <h2 className="font-display text-sm font-semibold text-surface-200">
                Export Format
              </h2>
            </div>
            <div className="space-y-1 p-3">
              {formats.map((format) => (
                <button
                  key={format.id}
                  onClick={() => {
                    setSelectedFormat(format.id);
                    setExportDone(false);
                  }}
                  className={cn(
                    "flex w-full items-center gap-3 rounded-lg px-3 py-3 text-left transition-all",
                    selectedFormat === format.id
                      ? "bg-emerald-500/10 ring-1 ring-emerald-500/20"
                      : "hover:bg-surface-800/40"
                  )}
                >
                  <div
                    className={cn(
                      "flex h-9 w-9 items-center justify-center rounded-lg",
                      selectedFormat === format.id
                        ? "bg-emerald-500/10 text-emerald-400"
                        : "bg-surface-700/30 text-surface-400"
                    )}
                  >
                    <format.icon className="h-4 w-4" />
                  </div>
                  <div className="flex-1">
                    <p
                      className={cn(
                        "text-sm font-medium",
                        selectedFormat === format.id
                          ? "text-emerald-400"
                          : "text-surface-200"
                      )}
                    >
                      {format.label}
                    </p>
                    <p className="text-[11px] text-surface-500">
                      {format.description}
                    </p>
                  </div>
                  {selectedFormat === format.id && (
                    <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                  )}
                </button>
              ))}
            </div>
          </div>

          <div className="rounded-xl border border-surface-700/60 bg-surface-800/50 backdrop-blur">
            <div className="border-b border-surface-700/60 px-5 py-3.5">
              <h2 className="font-display text-sm font-semibold text-surface-200">
                Options
              </h2>
            </div>
            <div className="space-y-3 p-5">
              <label className="flex cursor-pointer items-center gap-3">
                <input
                  type="checkbox"
                  checked={includeMeta}
                  onChange={() => setIncludeMeta(!includeMeta)}
                  className="h-4 w-4 rounded border-surface-600 bg-surface-700 text-emerald-500 focus:ring-emerald-500/20"
                />
                <div>
                  <p className="text-[13px] font-medium text-surface-200">
                    Include metadata fields
                  </p>
                  <p className="text-[11px] text-surface-500">
                    Add sample_id, scenario_id, control_id, and quality_score
                  </p>
                </div>
              </label>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="rounded-xl border border-surface-700/60 bg-surface-800/50 backdrop-blur">
            <div className="border-b border-surface-700/60 px-5 py-3.5">
              <h2 className="font-display text-sm font-semibold text-surface-200">
                Export Summary
              </h2>
            </div>
            <div className="space-y-3 p-5">
              <div className="flex items-center justify-between text-[13px]">
                <span className="text-surface-400">Dataset</span>
                <span className="font-medium text-surface-200">
                  GEN-001
                </span>
              </div>
              <div className="flex items-center justify-between text-[13px]">
                <span className="text-surface-400">Samples</span>
                <span className="font-medium text-surface-200">240</span>
              </div>
              <div className="flex items-center justify-between text-[13px]">
                <span className="text-surface-400">Format</span>
                <span className="font-medium text-surface-200 uppercase">
                  {selectedFormat}
                </span>
              </div>
              <div className="flex items-center justify-between text-[13px]">
                <span className="text-surface-400">Validation</span>
                <Badge variant="success">All Passed</Badge>
              </div>
              <div className="border-t border-surface-700/40 pt-3">
                <div className="flex items-center justify-between text-[13px]">
                  <span className="text-surface-400">Estimated Size</span>
                  <span className="font-medium text-surface-200">
                    ~2.4 MB
                  </span>
                </div>
              </div>
            </div>
          </div>

          <button
            onClick={handleExport}
            disabled={isExporting}
            className={cn(
              "flex w-full items-center justify-center gap-2 rounded-lg px-4 py-3 font-medium transition-all",
              isExporting
                ? "cursor-not-allowed bg-surface-700 text-surface-500"
                : exportDone
                  ? "bg-emerald-500 text-white shadow-lg shadow-emerald-500/20"
                  : "bg-emerald-500 text-white shadow-lg shadow-emerald-500/20 hover:bg-emerald-600"
            )}
          >
            {isExporting ? (
              <>
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                Exporting...
              </>
            ) : exportDone ? (
              <>
                <CheckCircle2 className="h-4 w-4" />
                Exported Successfully
              </>
            ) : (
              <>
                <Download className="h-4 w-4" />
                Export Dataset
              </>
            )}
          </button>

          {exportDone && (
            <div className="rounded-xl border border-surface-700/60 bg-surface-800/30 backdrop-blur">
              <div className="border-b border-surface-700/60 px-5 py-3.5">
                <h2 className="font-display text-sm font-semibold text-surface-200">
                  Export History
                </h2>
              </div>
              <div className="divide-y divide-surface-700/40">
                {exportHistory.map((exp) => (
                  <div
                    key={exp.id}
                    className="flex items-center justify-between px-5 py-3 transition-colors hover:bg-surface-800/40"
                  >
                    <div className="flex items-center gap-3">
                      <FileJson className="h-4 w-4 text-surface-400" />
                      <div>
                        <p className="text-[13px] font-medium text-surface-200">
                          {exp.id}
                        </p>
                        <p className="text-[11px] text-surface-500">
                          {exp.format} · {exp.samples} samples
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="h-3 w-3 text-surface-500" />
                      <span className="text-[11px] text-surface-500">
                        {exp.date}
                      </span>
                      <Badge variant="success">Done</Badge>
                    </div>
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
