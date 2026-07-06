# Compliance AI Factory

Enterprise dataset engineering platform for fine-tuning LLMs to become compliance auditors.

## Architecture

```
src/compliance_ai_factory/
├── api/              # FastAPI REST server
├── cli.py           # Click CLI (serve, tui, generate, validate, export)
├── knowledge_pack/  # Pydantic models + JSON loader for compliance standards
├── scenario_generator/  # Organization & audit scenario generation
├── dataset_generator/   # Training sample generation
├── dataset_validator/   # Quality & compliance validation
├── dataset_exporter/    # Export to JSONL, CSV, Parquet, etc.
├── tui/             # Rich terminal UI
└── common/          # Shared models & utilities

ui/                  # React + Vite + Tailwind web dashboard
knowledge/           # Compliance framework Knowledge Packs (JSON)
```

## Quick Start

```bash
# Install Python dependencies
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest

# Start API + Web UI
python -m compliance_ai_factory.cli serve --ui

# Start terminal UI
python -m compliance_ai_factory.cli tui
```

## Web Dashboard

```bash
cd ui && npm install && npm run dev
```

## Knowledge Packs

- **ISO/IEC 27001:2022** — 93 Annex A controls, 20 evidence requirements, 12 reasoning rules, 25 cross-references

## Tech Stack

- **Backend:** Python 3.11+, Pydantic, FastAPI, Click
- **Frontend:** React 19, Vite 6, TypeScript, Tailwind CSS 3
- **Database:** None (file-based Knowledge Pack storage)
- **Testing:** pytest, mypy, ruff
