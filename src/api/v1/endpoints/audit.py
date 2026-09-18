"""
Document Quality and Tamper Audit Endpoints.
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from ....schemas.doc_schema import DocumentAuditResponse
from ....services.vision_service import VisionQualityService
from ....core.security import verify_api_key

router = APIRouter()


@router.post(
    "/audit",
    response_model=DocumentAuditResponse,
    summary="Audit Document Quality & Skew",
    description="Analyzes image sharpness (Laplacian variance), skew angle, and illumination anomalies.",
)
async def audit_document(
    file: UploadFile = File(...),
    api_key: str = Depends(verify_api_key),
):
    if not file.content_type.startswith("image/") and not file.filename.lower().endswith((".png", ".jpg", ".jpeg", ".tiff", ".webp")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image format (PNG, JPG, TIFF, WebP).",
        )

    file_bytes = await file.read()
    if len(file_bytes) > 15 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Payload exceeds 15MB limit.",
        )

    return VisionQualityService.audit_image(file_bytes, file.filename)
