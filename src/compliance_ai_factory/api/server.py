from __future__ import annotations

import json
from pathlib import Path
from threading import Thread
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from compliance_ai_factory.api.jobs import job_manager
from compliance_ai_factory.common.exceptions import ExportError
from compliance_ai_factory.common.models.base import DatasetSample
from compliance_ai_factory.dataset_exporter.export_manager import ExportManager
from compliance_ai_factory.dataset_generator.pipeline import ConcreteDatasetGeneratorPipeline
from compliance_ai_factory.dataset_validator.pipeline import ConcreteValidationPipeline
from compliance_ai_factory.dataset_validator.validators import (
    ConsistencyValidator,
    DuplicateDetector,
    GrammarValidator,
    HallucinationDetector,
    IsoValidator,
    KnowledgeValidator,
    MetadataValidator,
    ReasoningValidator,
)
from compliance_ai_factory.knowledge_pack.loader import KnowledgePackLoader
from compliance_ai_factory.knowledge_pack.models import (
    KnowledgePack,
)
from compliance_ai_factory.scenario_generator.generator import ConcreteScenarioGenerator
from compliance_ai_factory.scenario_generator.repository import FileScenarioRepository

app = FastAPI(
    title="Compliance AI Factory API",
    version="0.1.0",
    description="Enterprise Dataset Engineering Platform for Compliance Auditing",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

KNOWLEDGE_DIR: Path = Path(__file__).parents[3] / "knowledge"
OUTPUT_DIR: Path = Path(__file__).parents[3] / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
_loaded_packs: dict[str, KnowledgePack] = {}
_scenario_generator = ConcreteScenarioGenerator()
_scenario_repo = FileScenarioRepository(OUTPUT_DIR / "scenarios")
_export_manager = ExportManager()


class GenerateRequest(BaseModel):
    standard: str = "iso27001"
    industry: str = "technology"
    maturity: str = "defined"
    difficulty: str = "intermediate"
    controls: list[str] = []
    samples_per_control: int = 10
    seed: int | None = None


class ValidateRequest(BaseModel):
    dataset_id: str
    standard: str = "iso27001"


class ExportRequest(BaseModel):
    dataset_id: str
    format: str = "jsonl"
    include_metadata: bool = True


class ConfigRequest(BaseModel):
    standard: str = "iso27001"
    industry: str = "technology"
    maturity: str = "defined"
    difficulty: str = "intermediate"
    controls: list[str] = []
    samples_per_control: int = 10
    seed: int | None = None


def _load_pack(standard: str) -> KnowledgePack:
    if standard not in _loaded_packs:
        pack_path = KNOWLEDGE_DIR / standard
        if not pack_path.exists():
            raise HTTPException(status_code=404, detail=f"Knowledge Pack '{standard}' not found")
        loader = KnowledgePackLoader(pack_path)
        _loaded_packs[standard] = loader.load()
    return _loaded_packs[standard]


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}


@app.get("/api/knowledge")
async def list_knowledge_packs() -> dict[str, list[str]]:
    if not KNOWLEDGE_DIR.exists():
        return {"packs": []}
    packs = sorted(
        d.name
        for d in KNOWLEDGE_DIR.iterdir()
        if d.is_dir() and (d / "metadata.json").exists()
    )
    return {"packs": packs}


@app.get("/api/knowledge/{standard}")
async def get_knowledge_pack(standard: str) -> dict[str, Any]:
    pack = _load_pack(standard)
    return pack.model_dump(mode="json")


@app.get("/api/knowledge/{standard}/controls")
async def list_controls(standard: str) -> list[dict[str, Any]]:
    pack = _load_pack(standard)
    return [c.model_dump(mode="json") for c in pack.controls]


@app.get("/api/knowledge/{standard}/controls/{control_id}")
async def get_control(standard: str, control_id: str) -> dict[str, Any]:
    pack = _load_pack(standard)
    control = pack.get_control(control_id)
    if control is None:
        raise HTTPException(status_code=404, detail=f"Control {control_id} not found")
    return control.model_dump(mode="json")


@app.get("/api/knowledge/{standard}/evidence")
async def list_evidence(standard: str) -> list[dict[str, Any]]:
    pack = _load_pack(standard)
    return [e.model_dump(mode="json") for e in pack.evidence]


@app.get("/api/knowledge/{standard}/reasoning")
async def list_reasoning(standard: str) -> list[dict[str, Any]]:
    pack = _load_pack(standard)
    return [r.model_dump(mode="json") for r in pack.reasoning]


@app.get("/api/knowledge/{standard}/cross-references")
async def list_cross_references(standard: str) -> list[dict[str, Any]]:
    pack = _load_pack(standard)
    return [x.model_dump(mode="json") for x in pack.cross_references]


@app.get("/api/knowledge/{standard}/maturity")
async def list_maturity(standard: str) -> list[dict[str, Any]]:
    pack = _load_pack(standard)
    return [m.model_dump(mode="json") for m in pack.maturity]


@app.get("/api/knowledge/{standard}/industries")
async def list_industries(standard: str) -> list[dict[str, Any]]:
    pack = _load_pack(standard)
    return [i.model_dump(mode="json") for i in pack.industries]


@app.get("/api/knowledge/{standard}/stats")
async def get_pack_stats(standard: str) -> dict[str, Any]:
    pack = _load_pack(standard)
    return {
        "total_controls": len(pack.controls),
        "total_evidence": len(pack.evidence),
        "total_reasoning_rules": len(pack.reasoning),
        "total_cross_references": len(pack.cross_references),
        "total_terminology": len(pack.terminology),
        "controls_by_clause": {
            clause: len([c for c in pack.controls if c.clause == clause])
            for clause in sorted({c.clause for c in pack.controls})
        },
        "evidence_by_category": {
            cat: len([e for e in pack.evidence if e.category == cat])
            for cat in sorted({e.category for e in pack.evidence})
        },
    }


@app.get("/api/scenario/industries")
async def list_scenario_industries() -> dict[str, Any]:
    return {"industries": _scenario_generator.list_industries()}


@app.post("/api/scenario/generate")
async def generate_scenario(seed: int | None = None) -> dict[str, Any]:
    scenario = _scenario_generator.generate(seed=seed)
    path = _scenario_repo.save(scenario)
    return {
        "scenario": scenario.model_dump(mode="json"),
        "path": path,
    }


@app.post("/api/generate")
async def start_generation(req: GenerateRequest) -> dict[str, Any]:
    pack = _load_pack(req.standard)

    if req.controls:
        controls = [c for c in pack.controls if c.control_id in req.controls]
        if not controls:
            raise HTTPException(status_code=400, detail="No valid controls selected")
    else:
        controls = pack.controls[:3]

    scenario = _scenario_generator.generate(seed=req.seed)
    _scenario_repo.save(scenario)

    job_id = job_manager.create_job(
        "generate",
        standard=req.standard,
        total_controls=len(controls),
        total_samples=len(controls) * req.samples_per_control,
    )

    def run_generation() -> None:
        try:
            pipeline = ConcreteDatasetGeneratorPipeline()
            all_samples: list[DatasetSample] = []
            for control in controls:
                limited_pack = KnowledgePack(
                    metadata=pack.metadata,
                    controls=[control],
                    evidence=pack.evidence,
                    reasoning=pack.reasoning,
                    cross_references=pack.cross_references,
                    terminology=pack.terminology,
                    glossary=pack.glossary,
                    maturity=pack.maturity,
                    industries=pack.industries,
                    audit_patterns=pack.audit_patterns,
                )
                gen_samples = pipeline.run(scenario, limited_pack)
                all_samples.extend(gen_samples)

            dataset = [s.model_dump(mode="json") for s in all_samples]
            dataset_path = OUTPUT_DIR / f"dataset_{job_id}.json"
            with open(dataset_path, "w") as f:
                json.dump(dataset, f, indent=2)

            job_manager.update_job(
                job_id,
                status="completed",
                progress=100,
                result={
                    "dataset_id": job_id,
                    "sample_count": len(all_samples),
                    "control_count": len(controls),
                    "path": str(dataset_path),
                    "scenario_id": scenario.id,
                },
            )
        except Exception as e:
            job_manager.update_job(job_id, status="failed", error=str(e))

    Thread(target=run_generation, daemon=True).start()

    return {
        "job_id": job_id,
        "status": "running",
        "scenario_id": scenario.id,
        "total_samples": len(controls) * req.samples_per_control,
    }


@app.get("/api/generate/history")
async def list_generation_history() -> list[dict[str, Any]]:
    return job_manager.list_jobs("generate")


@app.get("/api/generate/{job_id}")
async def get_generation_status(job_id: str) -> dict[str, Any]:
    job = job_manager.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Generation job '{job_id}' not found")
    return job


@app.post("/api/validate")
async def start_validation(req: ValidateRequest) -> dict[str, Any]:
    dataset_path = OUTPUT_DIR / f"dataset_{req.dataset_id}.json"
    if not dataset_path.exists():
        raise HTTPException(status_code=404, detail=f"Dataset '{req.dataset_id}' not found")

    with open(dataset_path) as f:
        dataset_data = json.load(f)

    pack = _load_pack(req.standard)
    samples = [DatasetSample(**s) for s in dataset_data]

    job_id = job_manager.create_job(
        "validate",
        dataset_id=req.dataset_id,
        total_samples=len(samples),
    )

    def run_validation() -> None:
        try:
            validator_instances = [
                ("ISO Compliance", IsoValidator(pack)),
                ("Knowledge Accuracy", KnowledgeValidator(pack)),
                ("Consistency", ConsistencyValidator(pack)),
                ("Grammar", GrammarValidator(pack)),
                ("Hallucination", HallucinationDetector(pack)),
                ("Metadata", MetadataValidator(pack)),
                ("Reasoning", ReasoningValidator(pack)),
            ]
            dup_detector = DuplicateDetector(pack)
            dup_detector.set_all_samples(samples)

            pipeline = ConcreteValidationPipeline(
                validators=[v for _, v in validator_instances] + [dup_detector],
                knowledge_pack=pack,
            )
            validated = pipeline.validate_all(samples)
            summary = pipeline.get_summary(validated)

            validated_dicts = []
            for s in validated:
                checks = []
                for name, validator in validator_instances:
                    errors = validator.validate(s)
                    if errors:
                        checks.append({"name": name, "status": "failed", "message": errors[0]})
                    else:
                        checks.append({"name": name, "status": "passed"})
                dup_errors = dup_detector.validate(s)
                if dup_errors:
                    checks.append({"name": "Duplicate Detection", "status": "failed", "message": dup_errors[0]})
                else:
                    checks.append({"name": "Duplicate Detection", "status": "passed"})
                d = s.model_dump(mode="json")
                d["checks"] = checks
                validated_dicts.append(d)

            validated_path = OUTPUT_DIR / f"validated_{req.dataset_id}.json"
            with open(validated_path, "w") as f:
                json.dump(
                    {
                        "samples": validated_dicts,
                        "summary": summary,
                    },
                    f,
                    indent=2,
                )

            job_manager.update_job(
                job_id,
                status="completed",
                progress=100,
                result={
                    "dataset_id": req.dataset_id,
                    "sample_count": len(validated),
                    "summary": summary,
                    "path": str(validated_path),
                    "samples": validated_dicts,
                },
            )
        except Exception as e:
            job_manager.update_job(job_id, status="failed", error=str(e))

    Thread(target=run_validation, daemon=True).start()

    return {
        "job_id": job_id,
        "status": "running",
        "dataset_id": req.dataset_id,
        "total_samples": len(samples),
    }


@app.get("/api/validate/history")
async def list_validation_history() -> list[dict[str, Any]]:
    return job_manager.list_jobs("validate")


@app.get("/api/validate/{job_id}")
async def get_validation_status(job_id: str) -> dict[str, Any]:
    job = job_manager.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Validation job '{job_id}' not found")
    return job


@app.post("/api/export")
async def start_export(req: ExportRequest) -> dict[str, Any]:
    validated_path = OUTPUT_DIR / f"validated_{req.dataset_id}.json"
    if not validated_path.exists():
        raise HTTPException(status_code=404, detail=f"Validated dataset '{req.dataset_id}' not found")

    with open(validated_path) as f:
        data = json.load(f)

    samples = [DatasetSample(**s) for s in data.get("samples", data if isinstance(data, list) else [])]
    if not samples and isinstance(data, dict):
        samples = [DatasetSample(**s) for s in data.get("samples", [])]

    if not samples:
        raise HTTPException(status_code=400, detail="No samples found in dataset")

    try:
        result = _export_manager.export(
            samples=samples,
            format_name=req.format,
            output_dir=OUTPUT_DIR / "exports",
            run_validation=False,
        )
        return result
    except ExportError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/export/history")
async def list_export_history() -> list[dict[str, Any]]:
    return _export_manager.get_history()


@app.get("/api/config")
async def get_config() -> dict[str, Any]:
    pack = _load_pack("iso27001")
    return {
        "industries": _scenario_generator.list_industries(),
        "difficulties": ["basic", "intermediate", "advanced", "expert"],
        "maturity_levels": ["initial", "repeatable", "defined", "managed", "optimizing"],
        "sample_sizes": [50, 100, 250, 500, 1000],
        "controls": [{"control_id": c.control_id, "title": c.title} for c in pack.controls],
    }


def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    import uvicorn
    uvicorn.run(app, host=host, port=port)


def serve_with_ui(host: str = "127.0.0.1", port: int = 8000) -> None:
    ui_dist = Path(__file__).parents[3] / "ui" / "dist"
    if ui_dist.exists():
        from fastapi.responses import FileResponse, JSONResponse

        app.mount("/assets", StaticFiles(directory=str(ui_dist / "assets")), name="assets")

        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str) -> Any:
            if full_path.startswith("api/"):
                return JSONResponse(status_code=404, content={"detail": "Not found"})
            file_path = ui_dist / full_path
            if file_path.exists() and file_path.is_file():
                return FileResponse(str(file_path))
            return FileResponse(str(ui_dist / "index.html"))
    serve(host=host, port=port)
