from pathlib import Path
from tempfile import TemporaryDirectory

from compliance_ai_factory.scenario_generator.generator import ConcreteScenarioGenerator
from compliance_ai_factory.scenario_generator.repository import FileScenarioRepository
from compliance_ai_factory.common.models.base import Scenario, Industry, CompanySize, MaturityLevel


class TestConcreteScenarioGenerator:
    def test_generate_returns_scenario(self):
        gen = ConcreteScenarioGenerator()
        result = gen.generate(seed=42)
        assert isinstance(result, Scenario)
        assert result.id.startswith("SCN-")
        assert result.version == "1.0"

    def test_generate_with_seed_is_deterministic(self):
        gen = ConcreteScenarioGenerator()
        res1 = gen.generate(seed=100)
        res2 = gen.generate(seed=100)
        assert res1.id == res2.id
        assert res1.organization.name == res2.organization.name
        assert res1.organization.industry == res2.organization.industry

    def test_generate_different_seed_different_result(self):
        gen = ConcreteScenarioGenerator()
        res1 = gen.generate(seed=1)
        res2 = gen.generate(seed=2)
        assert res1.organization.name != res2.organization.name

    def test_generate_organization_has_all_fields(self):
        gen = ConcreteScenarioGenerator()
        result = gen.generate(seed=77)
        org = result.organization
        assert isinstance(org.name, str) and len(org.name) > 0
        assert isinstance(org.industry, Industry)
        assert isinstance(org.size, CompanySize)
        assert isinstance(org.maturity, MaturityLevel)
        assert isinstance(org.departments, list) and len(org.departments) > 0
        assert isinstance(org.employees, list) and len(org.employees) > 0
        assert isinstance(org.assets, list) and len(org.assets) > 0
        assert isinstance(org.applications, list) and len(org.applications) > 0
        assert isinstance(org.threats, list) and len(org.threats) > 0
        assert "ISO 27001" in org.regulations or "ISO/IEC 27001" in str(org.regulations)

    def test_list_industries(self):
        gen = ConcreteScenarioGenerator()
        industries = gen.list_industries()
        assert isinstance(industries, list)
        assert "technology" in industries
        assert len(industries) >= 5


class TestFileScenarioRepository:
    def test_save_and_load(self):
        with TemporaryDirectory() as tmp:
            repo = FileScenarioRepository(Path(tmp))
            gen = ConcreteScenarioGenerator()
            scenario = gen.generate(seed=42)
            path = repo.save(scenario)
            assert path.endswith(".json")
            loaded = repo.load(scenario.id)
            assert loaded.id == scenario.id
            assert loaded.organization.name == scenario.organization.name

    def test_load_not_found_raises(self):
        with TemporaryDirectory() as tmp:
            repo = FileScenarioRepository(Path(tmp))
            import pytest
            from compliance_ai_factory.common.exceptions import ScenarioError
            with pytest.raises(ScenarioError):
                repo.load("NONEXISTENT")

    def test_list_all(self):
        with TemporaryDirectory() as tmp:
            repo = FileScenarioRepository(Path(tmp))
            gen = ConcreteScenarioGenerator()
            s1 = gen.generate(seed=1)
            s2 = gen.generate(seed=2)
            repo.save(s1)
            repo.save(s2)
            all_s = repo.list_all()
            assert len(all_s) == 2

    def test_delete(self):
        with TemporaryDirectory() as tmp:
            repo = FileScenarioRepository(Path(tmp))
            gen = ConcreteScenarioGenerator()
            scenario = gen.generate(seed=42)
            repo.save(scenario)
            assert len(repo.list_all()) == 1
            repo.delete(scenario.id)
            assert len(repo.list_all()) == 0
