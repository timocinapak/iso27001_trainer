"""FastAPI server serving Knowledge Pack data and dataset endpoints."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from compliance_ai_factory.knowledge_pack.loader import KnowledgePackLoader
from compliance_ai_factory.knowledge_pack.models import (
    ControlDefinition,
    KnowledgePack,
)

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
_loaded_packs: dict[str, KnowledgePack] = {}


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
async def get_knowledge_pack(standard: str) -> dict:
    pack = _load_pack(standard)
    return pack.model_dump(mode="json")


@app.get("/api/knowledge/{standard}/controls")
async def list_controls(standard: str) -> list[dict]:
    pack = _load_pack(standard)
    return [c.model_dump(mode="json") for c in pack.controls]


@app.get("/api/knowledge/{standard}/controls/{control_id}")
async def get_control(standard: str, control_id: str) -> dict:
    pack = _load_pack(standard)
    control = pack.get_control(control_id)
    if control is None:
        raise HTTPException(status_code=404, detail=f"Control {control_id} not found")
    return control.model_dump(mode="json")


@app.get("/api/knowledge/{standard}/evidence")
async def list_evidence(standard: str) -> list[dict]:
    pack = _load_pack(standard)
    return [e.model_dump(mode="json") for e in pack.evidence]


@app.get("/api/knowledge/{standard}/reasoning")
async def list_reasoning(standard: str) -> list[dict]:
    pack = _load_pack(standard)
    return [r.model_dump(mode="json") for r in pack.reasoning]


@app.get("/api/knowledge/{standard}/cross-references")
async def list_cross_references(standard: str) -> list[dict]:
    pack = _load_pack(standard)
    return [x.model_dump(mode="json") for x in pack.cross_references]


@app.get("/api/knowledge/{standard}/maturity")
async def list_maturity(standard: str) -> list[dict]:
    pack = _load_pack(standard)
    return [m.model_dump(mode="json") for m in pack.maturity]


@app.get("/api/knowledge/{standard}/industries")
async def list_industries(standard: str) -> list[dict]:
    pack = _load_pack(standard)
    return [i.model_dump(mode="json") for i in pack.industries]


@app.get("/api/knowledge/{standard}/stats")
async def get_pack_stats(standard: str) -> dict:
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


def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    import uvicorn
    uvicorn.run(app, host=host, port=port)


def serve_with_ui(host: str = "127.0.0.1", port: int = 8000) -> None:
    ui_dist = Path(__file__).parents[3] / "ui" / "dist"
    if ui_dist.exists():
        from fastapi.responses import FileResponse, JSONResponse

        app.mount("/assets", StaticFiles(directory=str(ui_dist / "assets")), name="assets")

        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            if full_path.startswith("api/"):
                return JSONResponse(status_code=404, content={"detail": "Not found"})
            file_path = ui_dist / full_path
            if file_path.exists() and file_path.is_file():
                return FileResponse(str(file_path))
            return FileResponse(str(ui_dist / "index.html"))
    serve(host=host, port=port)
