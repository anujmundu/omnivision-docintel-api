"""
Unit and integration tests for 2026-era OmniVision-DocIntel upgrades.
"""

import sys
import io
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.main import app
from src.core.config import settings
from src.services.forensics_service import DocumentForensicsService
from src.services.vlm_service import MultimodalVLMService

client = TestClient(app)
AUTH_HEADERS = {"X-API-Key": settings.API_KEY}


@pytest.fixture
def sample_image_bytes():
    img = Image.new("RGB", (300, 300), color="white")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    return buf.getvalue()


def test_forensics_service(sample_image_bytes):
    res = DocumentForensicsService.analyze_tampering(sample_image_bytes, "invoice_audit.jpg")
    assert "forgery_risk_score" in res
    assert "forensic_verdict" in res
    assert res["forensic_verdict"] in ["AUTHENTIC_PASS", "SUSPICIOUS_REVIEW", "FORGERY_ALERT"]
    assert "ela_mean_residual" in res


def test_vlm_extraction_service(sample_image_bytes):
    res = MultimodalVLMService.parse_multimodal_document(sample_image_bytes, "contract_note.png", hint_text="handwritten note")
    assert res["extraction_mode"] == "MULTIMODAL_VLM_ZERO_SHOT"
    assert res["data"]["handwritten_annotations_found"] is True
    assert res["data"]["gross_total"] == 4590.00


def test_forensics_endpoint(sample_image_bytes):
    response = client.post(
        f"{settings.API_V1_STR}/document/forensics",
        files={"file": ("test_doc.jpg", io.BytesIO(sample_image_bytes), "image/jpeg")},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert "forgery_risk_score" in data
    assert "ela_mean_residual" in data


def test_streaming_audit_endpoint(sample_image_bytes):
    response = client.post(
        f"{settings.API_V1_STR}/document/stream-audit",
        files={"file": ("test_stream.jpg", io.BytesIO(sample_image_bytes), "image/jpeg")},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    assert "text/event-stream" in response.headers.get("content-type", "")
    assert "data: " in response.text
    assert "COMPLETE" in response.text
