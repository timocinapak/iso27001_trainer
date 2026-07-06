import json
from datetime import datetime
from pathlib import Path

from compliance_ai_factory.common.exceptions import ScenarioError
from compliance_ai_factory.common.models.base import Scenario
from compliance_ai_factory.scenario_generator import ScenarioRepository


class FileScenarioRepository(ScenarioRepository):
    def __init__(self, base_path: str | Path = Path("scenarios")):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save(self, scenario: Scenario) -> str:
        file_path = self.base_path / f"{scenario.id}.json"
        data = scenario.model_dump(mode="json")
        data["_created_at"] = datetime.utcnow().isoformat()
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        return str(file_path)

    def load(self, scenario_id: str) -> Scenario:
        file_path = self.base_path / f"{scenario_id}.json"
        if not file_path.exists():
            raise ScenarioError(f"Scenario not found: {scenario_id}")
        with open(file_path) as f:
            data = json.load(f)
        data.pop("_created_at", None)
        return Scenario(**data)

    def list_all(self) -> list[Scenario]:
        scenarios: list[Scenario] = []
        if not self.base_path.exists():
            return scenarios
        for file_path in sorted(self.base_path.glob("*.json")):
            try:
                scenarios.append(self.load(file_path.stem))
            except Exception:
                continue
        return scenarios

    def delete(self, scenario_id: str) -> None:
        file_path = self.base_path / f"{scenario_id}.json"
        if file_path.exists():
            file_path.unlink()
