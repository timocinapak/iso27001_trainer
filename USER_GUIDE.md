# Compliance AI Factory — User Guide

## Overview

Compliance AI Factory is an enterprise dataset engineering platform for fine-tuning LLMs to become compliance auditors. It models the ISO/IEC 27001:2022 standard as a structured **Knowledge Pack** and provides a pipeline to generate audit datasets.

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+

### Installation

```bash
# Backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[server,dev]"

# Frontend
cd ui && npm install
```

### Running the Application

**Option A — Full stack (API + Web UI):**

```bash
python -m compliance_ai_factory.cli serve --ui
```

This serves the API at `http://127.0.0.1:8000` and mounts the production frontend build. You must first build the UI:

```bash
cd ui && npm run build
```

**Option B — API only:**

```bash
python -m compliance_ai_factory.cli serve
```

**Option C — Frontend dev server (hot reload):**

In one terminal:

```bash
python -m compliance_ai_factory.cli serve
```

In another:

```bash
cd ui && npm run dev
```

The Vite dev server runs at `http://localhost:5173` and proxies API calls to the backend.

**Option D — Terminal UI:**

```bash
python -m compliance_ai_factory.cli tui
```

---

## Web Dashboard — Routes & Features

### Sidebar Navigation

The sidebar on the left provides access to five sections:

| Icon              | Section          | Route          |
| ----------------- | ---------------- | -------------- |
| LayoutDashboard   | Dashboard        | `/`            |
| BookOpen          | Knowledge Packs  | `/knowledge`   |
| PlayCircle        | Generate         | `/generate`    |
| ShieldCheck       | Validate         | `/validate`    |
| Download          | Export           | `/export`      |

The sidebar footer shows the active standard (ISO/IEC 27001:2022) and the number of loaded controls.

### 1. Dashboard (`/`)

The main overview page shows:

- **Stat Cards** — four high-level metrics:
  - **Knowledge Packs** — number of loaded packs (currently 1: ISO 27001)
  - **Controls** — total controls broken down by clause: 37 Organizational, 8 People, 14 Physical, 34 Technological
  - **Evidence Reqs** — evidence requirements by category (management, technical, physical)
  - **Reasoning Rules** — reasoning rules with cross-references count
- **Generation Pipeline** — a visual flowchart of the 12-stage dataset generation pipeline:
  1. Knowledge Pack → 2. Scenario → 3. Control → 4. Question → 5. Answer → 6. Evidence → 7. Decision → 8. Finding → 9. Recommendation → 10. Reasoning → 11. Validation → 12. Export
- **Recent Generation Runs** — a feed showing past dataset generation jobs with status indicators (completed/running/failed), progress bars, and details per run (industry, control count, sample count, difficulty)

### 2. Knowledge Packs (`/knowledge`)

Lists all available compliance framework Knowledge Packs. Currently one pack is loaded:

- **ISO/IEC 27001:2022** — Full title: "Information security, cybersecurity and privacy protection — Information security management systems — Requirements"
- Shows four stat cards: Controls, Evidence Reqs, Reasoning Rules, Cross-References
- Displays **Control Clauses** grouped by Annex A clause:
  - Clause 5 — Organizational (37 controls)
  - Clause 6 — People (8 controls)
  - Clause 7 — Physical (14 controls)
  - Clause 8 — Technological (34 controls)

Click the pack card to navigate to its detail page.

### 3. Pack Detail (`/knowledge/:standard`)

Drills into a specific knowledge pack (currently `/knowledge/iso27001`) with three tabs:

#### Controls Tab
- Lists every control with its ID, title, objective, clause badge, and implementation level
- Each control card is color-coded by clause (emerald = Organizational, blue = People, amber = Physical, purple = Technological)
- **Implementation levels:** foundational, intermediate, advanced
- Expand a control to see:
  - **Description** — full control description
  - **Audit Intent** — what the auditor should verify
  - **Implementation Guidance** — actionable steps
  - **Expected Outcomes** — what success looks like
- **Search bar** — filter controls by ID, title, or objective

#### Evidence Tab
- Lists all evidence requirements with:
  - Evidence ID and title
  - Description of what constitutes the evidence
  - **Mandatory** badge if required
  - Category (e.g., management, technical)
  - Typical documents that serve as evidence
  - Associated control IDs

#### Reasoning Tab
- Lists reasoning rules with:
  - Rule ID and description
  - **Logic** — the logical expression used for audit reasoning
  - **Severity:** high / medium / low (color-coded)
  - **Rule type:** compliance, non_compliance, vulnerability_management, etc.
  - Associated control IDs

### 4. Generate (`/generate`)

Configure and run the dataset generation pipeline. Has a three-column layout with a configuration panel and a run summary sidebar.

#### Step 1: Scenario Configuration
- **Industry** — select the organization's industry: technology, finance, healthcare, manufacturing, retail, energy, government, education
- **Security Maturity** — select the organization's maturity level: initial, repeatable, defined, managed, optimizing
- **Difficulty** — select sample difficulty: basic, intermediate, advanced, expert

#### Step 2: Select Controls
- Checkbox list of all ISO 27001 controls
- Shows control ID and title for each
- Badge updates with the count of selected controls

#### Step 3: Sample Configuration
- Choose samples per control: 50, 100, 250, 500, or 1000
- Estimated total samples shown (samples per control × selected controls)

#### Run Configuration Sidebar
Shows a summary of the current configuration:
- Standard, Industry, Maturity, Difficulty, Controls count, Total Samples
- **Generate Dataset** button — starts generation with a progress bar
- Success confirmation when complete

### 5. Validate (`/validate`)

Review dataset quality and compliance validation results.

- **Summary cards** showing counts for:
  - Passed (green)
  - Warnings (amber)
  - Failed (red)
- **Search bar** — filter validation results by sample ID
- **Status filter buttons** — All / Passed / Failed / Warning
- Each validation result card shows:
  - Sample ID
  - Overall status badge
  - Passed/total checks count
  - Visual bar of individual check results
  - Expand to see individual checks:
    - ISO Validation
    - Knowledge Validation
    - Consistency Check
    - Grammar Check
    - Hallucination Detection
  - Each check shows pass/fail/warning status with optional message

### 6. Export (`/export`)

Export validated datasets to your preferred format.

**Available formats:**

| Format     | Icon       | Use Case                                              |
| ---------- | ---------- | ----------------------------------------------------- |
| JSONL      | FileJson   | Line-delimited JSON, ideal for LLM fine-tuning        |
| JSON       | FileJson   | Structured JSON array                                 |
| CSV        | FileSpread | Tabular format for spreadsheets                       |
| Markdown   | FileText   | Human-readable documentation                          |
| Parquet    | Database   | Columnar storage for large-scale processing           |

**Options:**
- **Include metadata fields** — toggles sample_id, scenario_id, control_id, and quality_score in the export

**Export Summary** sidebar shows:
- Dataset name, sample count, format, validation status, estimated file size

**Export History** — shows past exports with ID, format, sample count, date, and status.

---

## Backend API

The FastAPI server runs at `http://127.0.0.1:8000` by default.

### Endpoints

| Method | Path                                              | Description                      |
| ------ | ------------------------------------------------- | -------------------------------- |
| GET    | `/api/health`                                     | Health check                     |
| GET    | `/api/knowledge`                                  | List available Knowledge Packs   |
| GET    | `/api/knowledge/{standard}`                       | Get full Knowledge Pack          |
| GET    | `/api/knowledge/{standard}/controls`              | List all controls                |
| GET    | `/api/knowledge/{standard}/controls/{control_id}` | Get a specific control           |
| GET    | `/api/knowledge/{standard}/evidence`              | List evidence requirements       |
| GET    | `/api/knowledge/{standard}/reasoning`             | List reasoning rules             |
| GET    | `/api/knowledge/{standard}/cross-references`      | List cross-references            |
| GET    | `/api/knowledge/{standard}/maturity`              | List maturity mappings           |
| GET    | `/api/knowledge/{standard}/industries`            | List industry mappings           |
| GET    | `/api/knowledge/{standard}/stats`                 | Get pack statistics              |

### Statistics Response Shape

```json
{
  "total_controls": 93,
  "total_evidence": 20,
  "total_reasoning_rules": 12,
  "total_cross_references": 25,
  "total_terminology": 5,
  "controls_by_clause": { "5": 37, "6": 8, "7": 14, "8": 34 },
  "evidence_by_category": { "management": 10, "technical": 9, "physical": 1 }
}
```

---

## CLI Commands

```bash
# Start API server
python -m compliance_ai_factory.cli serve [--host 127.0.0.1] [--port 8000] [--ui]

# Launch terminal UI
python -m compliance_ai_factory.cli tui

# Generate dataset
python -m compliance_ai_factory.cli generate dataset [--standard iso27001] [--count 10] [--output output]

# Validate dataset
python -m compliance_ai_factory.cli validate dataset <path>

# Export dataset
python -m compliance_ai_factory.cli export dataset <path> [--format jsonl]

# Knowledge Pack management
python -m compliance_ai_factory.cli knowledge build <path>
python -m compliance_ai_factory.cli knowledge list
```

---

## Knowledge Packs

Knowledge Packs are JSON-based compliance standard definitions stored in the `knowledge/` directory.

### Current Pack: ISO/IEC 27001:2022

Located at `knowledge/iso27001/` with these JSON files:

| File                   | Contents                                                     |
| ---------------------- | ------------------------------------------------------------ |
| `metadata.json`        | Standard name, version, publisher, description               |
| `controls.json`        | 93 Annex A controls with guidance, outcomes, attributes      |
| `terminology.json`     | Key terms and definitions (ISMS, risk assessment, etc.)      |
| `glossary.json`        | Glossary entries with context and cross-references           |
| `evidence.json`        | 20 evidence requirements with typical documents              |
| `reasoning.json`       | 12 reasoning rules for audit decision logic                  |
| `cross_references.json`| 25 cross-references between controls                         |
| `maturity.json`        | Maturity level mappings (initial, defined, optimizing)        |
| `industries.json`      | Industry focus mappings (technology, finance, healthcare)    |
| `prompts/`             | Prompt templates for generation                              |
| `validators/`          | Validation rule definitions                                  |

### Adding a New Standard

1. Create a new directory under `knowledge/` (e.g., `knowledge/soc2/`)
2. Add the required JSON files (minimum: `metadata.json` and `controls.json`)
3. Restart the server — the new pack appears automatically

---

## Data Model

### Control

```json
{
  "control_id": "A.5.1",
  "clause": "5",
  "title": "Policies for Information Security",
  "objective": "Define and manage information security policies...",
  "description": "A set of policies for information security shall be defined...",
  "implementation_guidance": ["Develop an information security policy..."],
  "expected_outcomes": ["Information security policy is documented..."],
  "attributes": [
    { "name": "clause_group", "value": "organizational" },
    { "name": "control_type", "value": "preventive" },
    { "name": "implementation_level", "value": "foundational" }
  ],
  "related_controls": ["A.5.2", "A.5.36", "A.6.1"],
  "required_evidence": ["EVID-POL-001", "EVID-POL-002"],
  "audit_intent": "Verify the organization has established..."
}
```

### Evidence Requirement

```json
{
  "evidence_id": "EVID-POL-001",
  "title": "Information Security Policy Document",
  "description": "The approved and signed information security policy document.",
  "category": "management",
  "control_ids": ["A.5.1"],
  "typical_documents": ["Information Security Policy", "Policy Approval Record"],
  "system_evidence": ["Policy repository with version control"],
  "management_evidence": ["Board minutes approving policy"],
  "mandatory": false
}
```

### Reasoning Rule

```json
{
  "rule_id": "RR-001",
  "rule_type": "compliance",
  "description": "A control is fully compliant when all expected outcomes are demonstrated through evidence.",
  "logic": "IF evidence exists for all expected outcomes AND evidence is current AND evidence covers scope THEN control_status = 'compliant'",
  "control_ids": [],
  "severity": "medium"
}
```

---

## Architecture

```
src/compliance_ai_factory/
├── api/                    # FastAPI REST server
├── cli.py                  # Click CLI entry point
├── knowledge_pack/         # Pydantic models + JSON loader
├── scenario_generator/     # Organization & audit scenario generation
├── dataset_generator/      # Training sample generation
├── dataset_validator/      # Quality & compliance validation
├── dataset_exporter/       # Export to JSONL, CSV, Parquet, etc.
├── knowledge_builder/      # Build Knowledge Packs from source docs
├── tui/                    # Rich terminal UI
├── benchmark_studio/       # Benchmarking tools
├── training_studio/        # LLM training utilities
└── common/                 # Shared models & exceptions

ui/                         # React + Vite + Tailwind web dashboard
knowledge/                  # Compliance framework Knowledge Packs (JSON)
```

### Generation Pipeline (12 stages)

1. **Knowledge Pack** — Load compliance standard
2. **Scenario** — Generate organization profile
3. **Control** — Select audit controls
4. **Question** — Generate audit questions
5. **Answer** — Generate sample responses
6. **Evidence** — Generate supporting evidence
7. **Decision** — Determine compliance status
8. **Finding** — Document audit findings
9. **Recommendation** — Generate recommendations
10. **Reasoning** — Add audit reasoning
11. **Validation** — Validate sample quality
12. **Export** — Export final dataset

---

## Tech Stack

| Layer      | Technology                                       |
| ---------- | ------------------------------------------------ |
| Backend    | Python 3.11+, Pydantic 2, FastAPI, Click, Rich   |
| Frontend   | React 19, Vite 6, TypeScript, Tailwind CSS 3     |
| Icons      | Lucide React                                     |
| Database   | None (file-based Knowledge Pack JSON storage)    |
| Testing    | pytest, pytest-cov, mypy, ruff                   |

## Running Tests

```bash
pytest
```

This runs all tests with coverage reporting.
