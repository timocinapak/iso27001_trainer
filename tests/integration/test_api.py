from __future__ import annotations

import json
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from compliance_ai_factory.api.server import OUTPUT_DIR, app, _loaded_packs

client = TestClient(app)

TEST_STANDARD = "iso27001"


@pytest.fixture(autouse=True)
def clear_state():
    _loaded_packs.clear()
    yield
    _loaded_packs.clear()


def poll_job(job_id: str, max_wait: int = 60) -> dict:
    for _ in range(max_wait):
        resp = client.get(f"/api/generate/{job_id}")
        assert resp.status_code == 200
        job = resp.json()
        if job["status"] in ("completed", "failed"):
            return job
        time.sleep(0.5)
    pytest.fail(f"Job {job_id} did not complete within {max_wait}s")


class TestHealth:
    def test_health(self):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["version"] == "0.1.0"


class TestKnowledge:
    def test_list_packs(self):
        resp = client.get("/api/knowledge")
        assert resp.status_code == 200
        data = resp.json()
        assert "packs" in data
        assert TEST_STANDARD in data["packs"]

    def test_get_pack(self):
        resp = client.get(f"/api/knowledge/{TEST_STANDARD}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["metadata"]["standard_name"] == "ISO/IEC 27001"
        assert len(data["controls"]) > 0

    def test_get_pack_not_found(self):
        resp = client.get("/api/knowledge/nonexistent")
        assert resp.status_code == 404

    def test_list_controls(self):
        resp = client.get(f"/api/knowledge/{TEST_STANDARD}/controls")
        assert resp.status_code == 200
        controls = resp.json()
        assert len(controls) > 0
        assert "control_id" in controls[0]
        assert "A.5.1" in {c["control_id"] for c in controls}

    def test_get_control(self):
        resp = client.get(f"/api/knowledge/{TEST_STANDARD}/controls/A.5.1")
        assert resp.status_code == 200
        control = resp.json()
        assert control["control_id"] == "A.5.1"
        assert control["title"]

    def test_get_control_not_found(self):
        resp = client.get(f"/api/knowledge/{TEST_STANDARD}/controls/ZZ.99")
        assert resp.status_code == 404

    def test_list_evidence(self):
        resp = client.get(f"/api/knowledge/{TEST_STANDARD}/evidence")
        assert resp.status_code == 200
        evidence = resp.json()
        assert len(evidence) > 0
        assert "evidence_id" in evidence[0]

    def test_list_reasoning(self):
        resp = client.get(f"/api/knowledge/{TEST_STANDARD}/reasoning")
        assert resp.status_code == 200
        rules = resp.json()
        assert len(rules) > 0
        assert "rule_id" in rules[0]

    def test_list_cross_references(self):
        resp = client.get(f"/api/knowledge/{TEST_STANDARD}/cross-references")
        assert resp.status_code == 200
        xrefs = resp.json()
        assert len(xrefs) > 0
        assert "source_control_id" in xrefs[0]

    def test_list_maturity(self):
        resp = client.get(f"/api/knowledge/{TEST_STANDARD}/maturity")
        assert resp.status_code == 200
        levels = resp.json()
        assert len(levels) > 0

    def test_list_industries(self):
        resp = client.get(f"/api/knowledge/{TEST_STANDARD}/industries")
        assert resp.status_code == 200
        industries = resp.json()
        assert len(industries) > 0

    def test_get_stats(self):
        resp = client.get(f"/api/knowledge/{TEST_STANDARD}/stats")
        assert resp.status_code == 200
        stats = resp.json()
        assert stats["total_controls"] > 0
        assert stats["total_evidence"] > 0
        assert "controls_by_clause" in stats


class TestScenario:
    def test_list_industries(self):
        resp = client.get("/api/scenario/industries")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["industries"]) > 0

    def test_generate_scenario(self):
        resp = client.post("/api/scenario/generate")
        assert resp.status_code == 200
        data = resp.json()
        assert "scenario" in data
        assert "organization" in data["scenario"]
        assert "industry" in data["scenario"]["organization"]
        assert "path" in data

    def test_generate_scenario_with_seed(self):
        resp = client.post("/api/scenario/generate", params={"seed": 42})
        assert resp.status_code == 200
        data1 = resp.json()

        resp = client.post("/api/scenario/generate", params={"seed": 42})
        assert resp.status_code == 200
        data2 = resp.json()

        assert data1["scenario"]["id"] == data2["scenario"]["id"]


class TestGenerate:
    def test_start_generation(self):
        resp = client.post(
            "/api/generate",
            json={"standard": TEST_STANDARD, "samples_per_control": 2, "controls": ["A.5.1"]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "job_id" in data
        assert data["status"] == "running"
        assert data["total_samples"] == 2

        job = poll_job(data["job_id"])
        assert job["status"] == "completed"
        assert job["result"]["sample_count"] == 17
        assert job["result"]["control_count"] == 1

    def test_generation_with_multiple_controls(self):
        resp = client.post(
            "/api/generate",
            json={
                "standard": TEST_STANDARD,
                "samples_per_control": 1,
                "controls": ["A.5.1", "A.5.2"],
            },
        )
        assert resp.status_code == 200
        job = poll_job(resp.json()["job_id"])
        assert job["status"] == "completed"
        assert job["result"]["sample_count"] >= 32
        assert job["result"]["control_count"] == 2

    def test_generation_invalid_controls(self):
        resp = client.post(
            "/api/generate",
            json={
                "standard": TEST_STANDARD,
                "controls": ["NONEXISTENT"],
                "samples_per_control": 1,
            },
        )
        assert resp.status_code == 400

    def test_get_job_not_found(self):
        resp = client.get("/api/generate/NONEXISTENT-123")
        assert resp.status_code == 404

    def test_list_history(self):
        resp = client.post(
            "/api/generate",
            json={"standard": TEST_STANDARD, "samples_per_control": 1, "controls": ["A.5.1"]},
        )
        assert resp.status_code == 200
        poll_job(resp.json()["job_id"])

        resp = client.get("/api/generate/history")
        assert resp.status_code == 200
        history = resp.json()
        assert len(history) >= 1
        assert history[0]["type"] == "generate"
        assert history[0]["status"] == "completed"


class TestValidate:
    @pytest.fixture
    def generated_dataset(self):
        resp = client.post(
            "/api/generate",
            json={"standard": TEST_STANDARD, "samples_per_control": 2, "controls": ["A.5.1"]},
        )
        assert resp.status_code == 200
        job = poll_job(resp.json()["job_id"])
        return job["result"]["dataset_id"]

    def test_start_validation(self, generated_dataset):
        resp = client.post(
            "/api/validate",
            json={"dataset_id": generated_dataset, "standard": TEST_STANDARD},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "running"
        assert data["dataset_id"] == generated_dataset

        job = poll_job(data["job_id"])
        assert job["status"] == "completed"
        assert job["result"]["sample_count"] > 0
        assert "summary" in job["result"]

    def test_validation_dataset_not_found(self):
        resp = client.post(
            "/api/validate",
            json={"dataset_id": "NONEXISTENT", "standard": TEST_STANDARD},
        )
        assert resp.status_code == 404

    def test_validation_history(self, generated_dataset):
        resp = client.post(
            "/api/validate",
            json={"dataset_id": generated_dataset, "standard": TEST_STANDARD},
        )
        assert resp.status_code == 200
        poll_job(resp.json()["job_id"])

        resp = client.get("/api/validate/history")
        assert resp.status_code == 200
        history = resp.json()
        assert len(history) >= 1

    def test_get_job_not_found(self):
        resp = client.get("/api/validate/NONEXISTENT-123")
        assert resp.status_code == 404


class TestExport:
    @pytest.fixture
    def validated_dataset(self):
        resp = client.post(
            "/api/generate",
            json={"standard": TEST_STANDARD, "samples_per_control": 2, "controls": ["A.5.1"]},
        )
        assert resp.status_code == 200
        gen_job = poll_job(resp.json()["job_id"])
        dataset_id = gen_job["result"]["dataset_id"]

        resp = client.post(
            "/api/validate",
            json={"dataset_id": dataset_id, "standard": TEST_STANDARD},
        )
        assert resp.status_code == 200
        poll_job(resp.json()["job_id"])

        return dataset_id

    def test_export_jsonl(self, validated_dataset):
        resp = client.post(
            "/api/export",
            json={"dataset_id": validated_dataset, "format": "jsonl"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["format"] == "jsonl"
        assert data["sample_count"] > 0
        assert Path(data["path"]).exists()

    def test_export_json(self, validated_dataset):
        resp = client.post(
            "/api/export",
            json={"dataset_id": validated_dataset, "format": "json"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["format"] == "json"
        assert Path(data["path"]).exists()

    def test_export_csv(self, validated_dataset):
        resp = client.post(
            "/api/export",
            json={"dataset_id": validated_dataset, "format": "csv"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["format"] == "csv"
        assert Path(data["path"]).exists()

    def test_export_markdown(self, validated_dataset):
        resp = client.post(
            "/api/export",
            json={"dataset_id": validated_dataset, "format": "markdown"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["format"] == "markdown"
        assert Path(data["path"]).exists()

    def test_export_invalid_format(self, validated_dataset):
        resp = client.post(
            "/api/export",
            json={"dataset_id": validated_dataset, "format": "invalid"},
        )
        assert resp.status_code == 400

    def test_export_not_found(self):
        resp = client.post(
            "/api/export",
            json={"dataset_id": "NONEXISTENT", "format": "jsonl"},
        )
        assert resp.status_code == 404

    def test_export_history(self, validated_dataset):
        resp = client.post(
            "/api/export",
            json={"dataset_id": validated_dataset, "format": "jsonl"},
        )
        assert resp.status_code == 200

        resp = client.get("/api/export/history")
        assert resp.status_code == 200
        history = resp.json()
        assert len(history) >= 1


class TestConfig:
    def test_get_config(self):
        resp = client.get("/api/config")
        assert resp.status_code == 200
        data = resp.json()
        assert "industries" in data
        assert "difficulties" in data
        assert "maturity_levels" in data
        assert "sample_sizes" in data
        assert "controls" in data
        assert len(data["controls"]) > 0
        assert "control_id" in data["controls"][0]
