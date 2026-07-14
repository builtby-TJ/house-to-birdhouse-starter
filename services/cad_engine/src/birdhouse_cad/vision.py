from __future__ import annotations

import base64
import hashlib
import io
import shutil
from typing import Any

from PIL import Image, ImageFilter, ImageStat

from .models import CaptureImage


def diagnose_capture(images: list[CaptureImage]) -> dict[str, Any]:
    diagnostics = []
    hashes: set[str] = set()
    usable = 0
    for capture in images:
        raw = base64.b64decode(capture.content_base64, validate=True)
        digest = hashlib.sha256(raw).hexdigest()
        duplicate = digest in hashes
        hashes.add(digest)
        with Image.open(io.BytesIO(raw)) as image:
            image.load()
            gray = image.convert("L")
            exposure = ImageStat.Stat(gray).mean[0]
            edge_variance = ImageStat.Stat(gray.filter(ImageFilter.FIND_EDGES)).var[0]
            resolution_ok = image.width >= 1200 and image.height >= 800
            exposure_ok = 35 <= exposure <= 220
            sharpness_ok = edge_variance >= 80
            accepted = resolution_ok and exposure_ok and sharpness_ok and not duplicate
            usable += int(accepted)
            diagnostics.append(
                {
                    "filename": capture.filename,
                    "side": capture.side,
                    "width": image.width,
                    "height": image.height,
                    "duplicate": duplicate,
                    "mean_luminance": round(exposure, 2),
                    "edge_variance": round(edge_variance, 2),
                    "accepted": accepted,
                    "retake_reasons": [
                        reason
                        for condition, reason in (
                            (resolution_ok, "resolution below 1200 x 800"),
                            (exposure_ok, "image is underexposed or overexposed"),
                            (sharpness_ok, "image may be blurred"),
                            (not duplicate, "duplicate image"),
                        )
                        if not condition
                    ],
                }
            )

    colmap_available = shutil.which("colmap") is not None
    return {
        "image_count": len(images),
        "usable_image_count": usable,
        "images": diagnostics,
        "colmap": {
            "available": colmap_available,
            "status": "ready_for_reconstruction" if colmap_available else "executable_not_installed",
            "registered_cameras": None,
            "sparse_points": None,
        },
        "mesh_policy": "diagnostic_only_never_used_as_uncontrolled_print_mesh",
    }
