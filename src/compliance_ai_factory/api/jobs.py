import uuid
from datetime import datetime
from typing import Any


class JobManager:
    def __init__(self) -> None:
        self._jobs: dict[str, dict[str, Any]] = {}

    def create_job(self, job_type: str, **kwargs: Any) -> str:
        job_id = f"{job_type.upper()}-{uuid.uuid4().hex[:8]}"
        self._jobs[job_id] = {
            "job_id": job_id,
            "type": job_type,
            "status": "running",
            "progress": 0,
            "created_at": datetime.utcnow().isoformat(),
            "result": None,
            "error": None,
            **kwargs,
        }
        return job_id

    def update_job(self, job_id: str, **updates: Any) -> None:
        if job_id in self._jobs:
            self._jobs[job_id].update(updates)

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        return self._jobs.get(job_id)

    def list_jobs(self, job_type: str | None = None) -> list[dict[str, Any]]:
        jobs = list(self._jobs.values())
        if job_type:
            jobs = [j for j in jobs if j["type"] == job_type]
        return sorted(jobs, key=lambda j: j["created_at"], reverse=True)


job_manager = JobManager()
