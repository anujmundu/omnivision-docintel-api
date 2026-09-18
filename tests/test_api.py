"""
Integration test suite for OmniVision-DocIntel FastAPI microservice.
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

client = TestClient(app)
AUTH_HEADERS = {"X-API-Key": settings.API_KEY}


def test_healthcheck():
    response = client.get(f"{settings.API_V1_STR}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["service"] == settings.PROJECT_NAME


def test_auth_rejection_missing_key():
    response = client.post(
        f"{settings.API_V1_STR}/document/classify",
        data={"text": "Invoice test content"},
    )
    assert response.status_code == 401
    assert "Invalid or missing X-API-Key" in response.json()["detail"]


def test_document_classification_success():
    invoice_text = "INVOICE #INV-8821\nBill To: Acme Corp\nTotal Due: $4,500.00\nPayment terms 30 days"
    response = client.post(
        f"{settings.API_V1_STR}/document/classify",
        data={"text": invoice_text},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_type"] == "INVOICE"
    assert data["confidence"] > 0.3


def test_entity_extraction_success():
    invoice_text = "Acme Global Solutions\nInvoice: INV-2026-902\nDate: 2026-02-18\nCloud Hosting 1 $1,200.00 $1,200.00\nTotal: $1,200.00"
    response = client.post(
        f"{settings.API_V1_STR}/document/extract",
        data={"raw_text": invoice_text},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["invoice_number"] == "INV-2026-902"
    assert data["total_amount"] == 1200.0
    assert len(data["line_items"]) >= 1


def test_document_image_audit_success():
    # Create synthetic test image (sharp checkerboard)
    img = Image.new("RGB", (400, 400), color="white")
    for x in range(0, 400, 40):
        for y in range(0, 400, 40):
            if (x + y) % 80 == 0:
                for dx in range(40):
                    for dy in range(40):
                        img.putpixel((x + dx, y + dy), (0, 0, 0))

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    response = client.post(
        f"{settings.API_V1_STR}/document/audit",
        files={"file": ("test_doc.png", img_byte_arr, "image/png")},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["quality_verdict"] in ["PASS", "MARGINAL"]
    assert "quality_metrics" in data
    assert data["quality_metrics"]["width_px"] == 400
