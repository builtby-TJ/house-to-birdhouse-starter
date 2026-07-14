FROM python:3.11-slim

WORKDIR /app
COPY services/cad_engine/pyproject.toml ./
COPY services/cad_engine/src ./src
COPY config ./config
RUN pip install --no-cache-dir '.[production-cad]'
RUN python -c "import cadquery as cq; from pathlib import Path; cube = cq.Workplane('XY').box(10, 10, 10); cq.exporters.export(cube, '/tmp/cube.step'); cq.exporters.export(cube, '/tmp/cube.stl'); assert Path('/tmp/cube.step').stat().st_size > 0; assert Path('/tmp/cube.stl').stat().st_size > 0"

EXPOSE 8000
CMD ["uvicorn", "birdhouse_cad.api:app", "--host", "0.0.0.0", "--port", "8000"]
