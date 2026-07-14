from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import HouseProject, VisionDiagnosticRequest
from .persistence import PersistentProjectStore
from .vision import diagnose_capture

app = FastAPI(
    title="House-to-Birdhouse CAD API",
    version="0.1.0",
    description="Revisioned API for validating projects and generating six-part production CAD.",
)
store = PersistentProjectStore.from_environment()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    stored = store.create_project(project)
    return store.generate(stored["project_id"])


@app.post("/v1/projects")
def create_project(project: HouseProject) -> dict:
    return store.create_project(project)


@app.get("/v1/projects")
def list_projects() -> list[dict]:
    return store.list_projects()


@app.get("/v1/projects/{project_id}")
def get_project(project_id: str) -> dict:
    project = store.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    return project


@app.put("/v1/projects/{project_id}")
def revise_project(project_id: str, project: HouseProject) -> dict:
    stored = store.revise_project(project_id, project)
    if stored is None:
        raise HTTPException(status_code=404, detail="project not found")
    return stored


@app.post("/v1/projects/{project_id}/generate")
def generate_project(project_id: str) -> dict:
    job = store.generate(project_id)
    if job is None:
        raise HTTPException(status_code=404, detail="project not found")
    return job


@app.get("/v1/models/{job_id}")
def get_model_job(job_id: str) -> dict:
    job = store.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return job


@app.get("/v1/models/{job_id}/manifest")
def get_model_manifest(job_id: str) -> dict:
    job = store.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    if job["status"] != "READY":
        raise HTTPException(status_code=409, detail="manifest is not ready")
    return job["manifest"]


@app.post("/v1/vision/diagnose")
def vision_diagnostic(request: VisionDiagnosticRequest) -> dict:
    try:
        return diagnose_capture(request.images)
    except (ValueError, OSError) as exc:
        raise HTTPException(status_code=422, detail=f"invalid capture image: {exc}") from exc
