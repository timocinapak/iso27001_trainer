import { useState, useEffect } from "react";
import {
  Download,
  FileJson,
  FileSpreadsheet,
  Database,
  FileText,
  CheckCircle2,
  Clock,
  XCircle,
} from "lucide-react";
import Badge from "../ui/Badge";
import { cn } from "../../lib/utils";
import { getGenerationHistory, startExport, getExportHistory } from "../../lib/api";
import type { ExportResult } from "../../lib/api";

const formats = [
  { id: "jsonl", label: "JSONL", icon: FileJson, description: "Line-delimited JSON, ideal for LLM fine-tuning" },
  { id: "json", label: "JSON", icon: FileJson, description: "Structured JSON array format" },
  { id: "csv", label: "CSV", icon: FileSpreadsheet, description: "Tabular format for spreadsheet applications" },
  { id: "markdown", label: "Markdown", icon: FileText, description: "Human-readable documentation format" },
  { id: "parquet", label: "Parquet", icon: Database, description: "Columnar storage for large-scale processing" },
];

export default function ExportPage() {
  const [selectedFormat, setSelectedFormat] = useState("jsonl");
  const [isExporting, setIsExporting] = useState(false);
  const [exportDone, setExportDone] = useState(false);
  const [exportResult, setExportResult] = useState<ExportResult | null>(null);
  const [exportHistory, setExportHistory] = useState<ExportResult[]>([]);
  const [datasetIds, setDatasetIds] = useState<string[]>([]);
  const [selectedDataset, setSelectedDataset] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getGenerationHistory().then((jobs) => {
      const ids = jobs
        .filter((j) => j.status === "completed" && j.result?.dataset_id)
        .map((j) => j.result!.dataset_id as string);
      setDatasetIds(ids);
      if (ids.length > 0) setSelectedDataset(ids[0] ?? "");
    }).catch(() => {});
    getExportHistory().then(setExportHistory).catch(() => {});
  }, []);

  const handleExport = async () => {
    if (!selectedDataset) return;
    setError(null);
    setIsExporting(true);
    try {
      const result = await startExport(selectedDataset, selectedFormat);
      setExportResult(result);
      setExportDone(true);
      setExportHistory((prev) => [
        {
          export_id: result.export_id,
          format: result.format,
          sample_count: result.sample_count,
          path: result.path,
          metadata: result.metadata,
        },
        ...prev,
      ]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Export failed");
    } finally {
      setIsExporting(false);
    }
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
                    setExportResult(null);
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
                Dataset Selection
              </h2>
            </div>
            <div className="p-5">
              <select
                value={selectedDataset}
                onChange={(e) => { setSelectedDataset(e.target.value); setExportDone(false); }}
                className="w-full rounded-lg border border-surface-700/60 bg-surface-800/50 px-3 py-2.5 text-[13px] text-surface-200 backdrop-blur"
              >
                {datasetIds.length === 0 && <option value="">No datasets available</option>}
                {datasetIds.map((id) => (
                  <option key={id} value={id}>{id}</option>
                ))}
              </select>
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
                  {selectedDataset || "—"}
                </span>
              </div>
              <div className="flex items-center justify-between text-[13px]">
                <span className="text-surface-400">Format</span>
                <span className="font-medium text-surface-200 uppercase">
                  {selectedFormat}
                </span>
              </div>
              {exportResult && (
                <div className="flex items-center justify-between text-[13px]">
                  <span className="text-surface-400">Samples</span>
                  <span className="font-medium text-surface-200">
                    {exportResult.sample_count}
                  </span>
                </div>
              )}
              <div className="flex items-center justify-between text-[13px]">
                <span className="text-surface-400">Validation</span>
                <Badge variant="success">Required</Badge>
              </div>
              <div className="border-t border-surface-700/40 pt-3">
                <div className="flex items-center justify-between text-[13px]">
                  <span className="text-surface-400">Output Path</span>
                  <span className="font-mono text-[11px] text-surface-500 truncate max-w-[200px]">
                    {exportResult?.path || "output/exports/"}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <button
            onClick={handleExport}
            disabled={isExporting || !selectedDataset}
            className={cn(
              "flex w-full items-center justify-center gap-2 rounded-lg px-4 py-3 font-medium transition-all",
              isExporting || !selectedDataset
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

          {error && (
            <div className="flex items-center gap-2 rounded-lg border border-red-500/20 bg-red-500/5 px-4 py-3">
              <XCircle className="h-4 w-4 text-red-400" />
              <span className="text-[13px] font-medium text-red-400">{error}</span>
            </div>
          )}

          {exportHistory.length > 0 && (
            <div className="rounded-xl border border-surface-700/60 bg-surface-800/30 backdrop-blur">
              <div className="border-b border-surface-700/60 px-5 py-3.5">
                <h2 className="font-display text-sm font-semibold text-surface-200">
                  Export History
                </h2>
              </div>
              <div className="divide-y divide-surface-700/40">
                {exportHistory.slice(0, 10).map((exp) => (
                  <div
                    key={exp.export_id}
                    className="flex items-center justify-between px-5 py-3 transition-colors hover:bg-surface-800/40"
                  >
                    <div className="flex items-center gap-3">
                      <FileJson className="h-4 w-4 text-surface-400" />
                      <div>
                        <p className="text-[13px] font-medium text-surface-200">
                          {exp.export_id}
                        </p>
                        <p className="text-[11px] text-surface-500">
                          {exp.format} · {exp.sample_count} samples
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="h-3 w-3 text-surface-500" />
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
