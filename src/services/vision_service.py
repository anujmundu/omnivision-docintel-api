"""
OpenCV Image Quality, Blur, Skew, and Exposure Auditing Service.
"""

import io
import time
from typing import Tuple, List
import numpy as np
from PIL import Image

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

from ..schemas.doc_schema import ImageQualityMetrics, DocumentAuditResponse
from ..core.config import settings


class VisionQualityService:
    """Enterprise computer vision inspection engine."""

    @classmethod
    def audit_image(cls, image_bytes: bytes, filename: str) -> DocumentAuditResponse:
        start_time = time.time()

        # Load image via PIL first for safe cross-format decoding
        pil_img = Image.open(io.BytesIO(image_bytes))
        width, height = pil_img.size
        aspect_ratio = round(width / max(height, 1), 2)
        channels = len(pil_img.getbands())

        # Convert to numpy array
        np_img = np.array(pil_img)

        if CV2_AVAILABLE:
            # Grayscale conversion
            if channels >= 3:
                gray = cv2.cvtColor(np_img, cv2.COLOR_RGB2GRAY)
            else:
                gray = np_img

            # 1. Laplacian Variance for Blur Detection
            blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())

            # 2. Skew Angle Detection via threshold contours
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            coords = np.column_stack(np.where(thresh > 0))
            if len(coords) > 50:
                angle = cv2.minAreaRect(coords)[-1]
                if angle < -45:
                    angle = -(90 + angle)
                else:
                    angle = -angle
                skew_angle = float(round(angle, 2))
            else:
                skew_angle = 0.0

            # 3. Brightness / Illumination
            mean_brightness = float(np.mean(gray))
        else:
            # High-performance NumPy fallback if OpenCV not compiled
            gray = np.mean(np_img, axis=2) if channels >= 3 else np_img
            # Gradient variance proxy for sharpness
            gx, gy = np.gradient(gray)
            blur_score = float(np.var(gx) + np.var(gy))
            skew_angle = 0.0
            mean_brightness = float(np.mean(gray))

        is_blurry = blur_score < settings.BLUR_THRESHOLD
        is_underexposed = mean_brightness < 40.0
        is_overexposed = mean_brightness > 230.0

        tamper_flags: List[str] = []
        if is_blurry:
            tamper_flags.append("HIGH_DEFOCUS_BLUR_DETECTED")
        if abs(skew_angle) > 15.0:
            tamper_flags.append(f"PERSPECTIVE_SKEW_EXCEEDS_TOLERANCE_{abs(skew_angle):.1f}DEG")
        if is_underexposed:
            tamper_flags.append("SEVERE_UNDEREXPOSURE")
        if is_overexposed:
            tamper_flags.append("SEVERE_OVEREXPOSURE_GLARE")
        if min(width, height) < 300:
            tamper_flags.append("SUBSTANDARD_RESOLUTION_UNDER_300PX")

        # Verdict
        if len(tamper_flags) == 0:
            verdict = "PASS"
        elif len(tamper_flags) == 1 and not is_blurry:
            verdict = "MARGINAL"
        else:
            verdict = "REJECT"

        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        metrics = ImageQualityMetrics(
            blur_score=round(blur_score, 2),
            is_blurry=is_blurry,
            skew_angle_deg=skew_angle,
            width_px=width,
            height_px=height,
            aspect_ratio=aspect_ratio,
            channels=channels,
            mean_brightness=round(mean_brightness, 1),
            is_underexposed=is_underexposed,
            is_overexposed=is_overexposed,
        )

        return DocumentAuditResponse(
            filename=filename,
            processed_in_ms=elapsed_ms,
            quality_verdict=verdict,
            quality_metrics=metrics,
            tamper_flags=tamper_flags,
        )
