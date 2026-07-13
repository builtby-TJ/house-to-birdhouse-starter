from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException

from .models import HouseProject
from .service import LocalJobRegistry

app = FastAPI(
    title="House-to-Birdhouse CAD API",
    version="0.1.0",
    description="Development API for validating projects and generating six-part prototype geometry.",
)
registry = LocalJobRegistry(Path("generated_jobs"))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "birdhouse-cad", "version": "0.1.0"}


@app.post("/v1/projects/validate")
def validate_project(project: HouseProject) -> dict:
    return {
        "valid": True,
        "project_name": project.project_name,
        "facade_feature_count": sum(
            len(f.features)
            for f in [project.facades.front, project.facades.back, project.facades.left, project.facades.right]
        ),
    }


@app.post("/v1/models/generate")
def generate_model(project: HouseProject) -> dict:
    return registry.generate(project)


@app.get("/v1/models/{job_id}")
def get_model_job(job_id: str) -> dict:
    job = registry.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return job
