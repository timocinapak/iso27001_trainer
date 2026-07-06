import { useEffect, useState } from "react";
import {
  Sparkles,
  Loader2,
  CheckCircle2,
} from "lucide-react";
import Badge from "../ui/Badge";
import { cn } from "../../lib/utils";
import { fetchControls } from "../../lib/api";

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

export default function GenerationPage() {
  const [controls, setControls] = useState<{ id: string; title: string }[]>([]);
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

  useEffect(() => {
    fetchControls("iso27001")
      .then((data) =>
        setControls(data.map((c) => ({ id: c.control_id, title: c.title })))
      )
      .catch(() => {});
  }, []);

  const toggleControl = (id: string) => {
    setSelectedControls((prev) =>
      prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]
    );
  };

  const handleGenerate = () => {
    setIsRunning(true);
    setProgress(0);
    const interval = setInterval(() => {
      setProgress((p) => {
        if (p >= 100) {
          clearInterval(interval);
          setIsRunning(false);
          return 100;
        }
        return p + 2;
      });
    }, 200);
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
          {/* Step 1: Scenario */}
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

          {/* Step 2: Controls */}
          <div className="rounded-xl border border-surface-700/60 bg-surface-800/50 backdrop-blur">
            <div className="flex items-center gap-3 border-b border-surface-700/60 px-5 py-3.5">
              <div className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-500/10 text-[11px] font-bold text-emerald-400">
                2
              </div>
              <h2 className="font-display text-sm font-semibold text-surface-200">
                Select Controls
              </h2>
              <Badge variant="success">{selectedControls.length} selected</Badge>
            </div>
            <div className="divide-y divide-surface-700/40">
              {controls.map((control) => (
                <label
                  key={control.id}
                  className="flex cursor-pointer items-center gap-3 px-5 py-2.5 transition-colors hover:bg-surface-800/40"
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
          </div>

          {/* Step 3: Sample Size */}
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

        {/* Sidebar */}
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

          {progress === 100 && (
            <div className="animate-slide-up flex items-center gap-2 rounded-lg border border-emerald-500/20 bg-emerald-500/5 px-4 py-3">
              <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              <span className="text-[13px] font-medium text-emerald-400">
                Dataset generated successfully
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
