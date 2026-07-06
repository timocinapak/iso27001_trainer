import json
from pathlib import Path

import pytest

from compliance_ai_factory.knowledge_pack.models import (
    ControlDefinition,
    EvidenceRequirement,
    KnowledgePack,
    ReasoningRule,
    StandardMetadata,
)
from compliance_ai_factory.knowledge_pack.loader import KnowledgePackLoader


class TestStandardMetadata:
    def test_valid_metadata(self):
        metadata = StandardMetadata(
            standard_name="ISO/IEC 27001",
            version="2022",
            release_date="2022-10-25",
            publisher="ISO",
        )
        assert metadata.standard_name == "ISO/IEC 27001"
        assert metadata.version == "2022"


class TestControlDefinition:
    def test_valid_control(self):
        control = ControlDefinition(
            control_id="A.5.1",
            clause="5",
            title="Policies for Information Security",
            objective="Define policies",
            description="A set of policies shall be defined.",
        )
        assert control.control_id == "A.5.1"
        assert control.title == "Policies for Information Security"

    def test_control_with_optional_fields(self):
        control = ControlDefinition(
            control_id="A.5.2",
            clause="5",
            title="Test Control",
            objective="Test objective",
            description="Test description",
            implementation_guidance=["Step 1", "Step 2"],
            expected_outcomes=["Outcome 1"],
            related_controls=["A.5.1"],
            required_evidence=["EVID-001"],
        )
        assert len(control.implementation_guidance) == 2
        assert control.related_controls == ["A.5.1"]


class TestEvidenceRequirement:
    def test_valid_evidence(self):
        evidence = EvidenceRequirement(
            evidence_id="EVID-POL-001",
            title="Policy Document",
            description="The approved policy document",
            category="management",
            control_ids=["A.5.1"],
        )
        assert evidence.evidence_id == "EVID-POL-001"
        assert evidence.mandatory is False

    def test_mandatory_evidence(self):
        evidence = EvidenceRequirement(
            evidence_id="EVID-MAN-001",
            title="Mandatory Evidence",
            description="Required evidence",
            category="technical",
            control_ids=["A.8.8"],
            mandatory=True,
        )
        assert evidence.mandatory is True


class TestKnowledgePack:
    @pytest.fixture
    def sample_pack(self):
        return KnowledgePack(
            metadata=StandardMetadata(
                standard_name="ISO/IEC 27001",
                version="2022",
                release_date="2022-10-25",
                publisher="ISO",
            ),
            controls=[
                ControlDefinition(
                    control_id="A.5.1",
                    clause="5",
                    title="Policies",
                    objective="Define policies",
                    description="Policy description",
                    related_controls=["A.5.2"],
                ),
                ControlDefinition(
                    control_id="A.5.2",
                    clause="5",
                    title="Roles",
                    objective="Define roles",
                    description="Roles description",
                ),
            ],
            evidence=[
                EvidenceRequirement(
                    evidence_id="EVID-001",
                    title="Policy Document",
                    description="Policy document",
                    category="management",
                    control_ids=["A.5.1"],
                )
            ],
            reasoning=[
                ReasoningRule(
                    rule_id="RR-001",
                    rule_type="compliance",
                    description="Compliance rule",
                    logic="IF x THEN y",
                    control_ids=["A.5.1"],
                )
            ],
        )

    def test_get_control_found(self, sample_pack):
        control = sample_pack.get_control("A.5.1")
        assert control is not None
        assert control.control_id == "A.5.1"

    def test_get_control_not_found(self, sample_pack):
        control = sample_pack.get_control("A.9.99")
        assert control is None

    def test_get_evidence_for_control(self, sample_pack):
        evidence = sample_pack.get_evidence_for_control("A.5.1")
        assert len(evidence) == 1
        assert evidence[0].evidence_id == "EVID-001"

    def test_get_evidence_for_control_no_match(self, sample_pack):
        evidence = sample_pack.get_evidence_for_control("A.5.2")
        assert len(evidence) == 0

    def test_get_related_controls(self, sample_pack):
        related = sample_pack.get_related_controls("A.5.1")
        assert len(related) == 1
        assert related[0].control_id == "A.5.2"

    def test_get_reasoning_rules_for_control(self, sample_pack):
        rules = sample_pack.get_reasoning_rules("A.5.1")
        assert len(rules) == 1
        assert rules[0].rule_id == "RR-001"

    def test_get_reasoning_rules_all(self, sample_pack):
        rules = sample_pack.get_reasoning_rules()
        assert len(rules) == 1

    def test_model_dump_for_export(self, sample_pack):
        exported = sample_pack.model_dump_for_export()
        assert "metadata" in exported
        assert "controls" in exported
        assert isinstance(exported["controls"], list)


class TestKnowledgePackLoader:
    @pytest.fixture
    def iso27001_path(self):
        return Path(__file__).parents[2] / "knowledge" / "iso27001"

    def test_load_iso27001(self, iso27001_path):
        loader = KnowledgePackLoader(iso27001_path)
        pack = loader.load()
        assert pack.metadata.standard_name == "ISO/IEC 27001"
        assert len(pack.controls) > 0
        assert len(pack.terminology) > 0

    def test_load_and_verify_controls(self, iso27001_path):
        loader = KnowledgePackLoader(iso27001_path)
        pack = loader.load()

        control_ids = {c.control_id for c in pack.controls}
        assert "A.5.1" in control_ids
        assert "A.5.37" in control_ids
        assert "A.6.1" in control_ids
        assert "A.6.8" in control_ids
        assert "A.7.1" in control_ids
        assert "A.7.14" in control_ids
        assert "A.8.1" in control_ids
        assert "A.8.34" in control_ids

    def test_list_available(self, iso27001_path):
        loader = KnowledgePackLoader(iso27001_path)
        available = loader.list_available()
        assert "iso27001" in available

    def test_loader_raises_on_missing(self):
        loader = KnowledgePackLoader(Path("/nonexistent/path"))
        with pytest.raises(Exception):
            loader.load()

    def test_controls_json_structure(self, iso27001_path):
        controls_file = iso27001_path / "controls.json"
        with open(controls_file) as f:
            controls = json.load(f)
        for control in controls:
            assert "control_id" in control
            assert "title" in control
            assert "objective" in control
            assert "description" in control
            assert "audit_intent" in control
            assert isinstance(control.get("implementation_guidance"), list)
            assert isinstance(control.get("expected_outcomes"), list)
            assert isinstance(control.get("related_controls"), list)

    def test_cross_references_are_valid(self, iso27001_path):
        xref_file = iso27001_path / "cross_references.json"
        controls_file = iso27001_path / "controls.json"
        with open(controls_file) as f:
            controls = json.load(f)
        control_ids = {c["control_id"] for c in controls}
        with open(xref_file) as f:
            xrefs = json.load(f)
        for xref in xrefs:
            assert xref["source_control_id"] in control_ids, (
                f"Cross-reference source {xref['source_control_id']} not found in controls"
            )
            assert xref["target_control_id"] in control_ids, (
                f"Cross-reference target {xref['target_control_id']} not found in controls"
            )
