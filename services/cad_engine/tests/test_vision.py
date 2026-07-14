from __future__ import annotations

import base64
import io

from PIL import Image

from birdhouse_cad.models import CaptureImage
from birdhouse_cad.vision import diagnose_capture


def _image_payload(color: tuple[int, int, int], filename: str) -> CaptureImage:
    image = Image.new("RGB", (1200, 800), color)
    stream = io.BytesIO()
    image.save(stream, format="JPEG")
    return CaptureImage(
        filename=filename,
        side="front",
        content_base64=base64.b64encode(stream.getvalue()).decode("ascii"),
    )


def test_capture_diagnostic_flags_duplicates_and_reports_colmap_boundary() -> None:
    first = _image_payload((120, 130, 140), "front-1.jpg")
    duplicate = first.model_copy(update={"filename": "front-duplicate.jpg"})
    report = diagnose_capture([first, duplicate])

    assert report["image_count"] == 2
    assert report["images"][1]["duplicate"] is True
    assert "available" in report["colmap"]
    assert report["mesh_policy"] == "diagnostic_only_never_used_as_uncontrolled_print_mesh"
