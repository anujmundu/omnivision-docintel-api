"""
Document Digital Forensics and ELA Tampering Verification Endpoints.
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from typing import Dict, Any
from ....services.forensics_service import DocumentForensicsService
from ....core.security import verify_api_key

router = APIRouter()


@router.post(
    "/forensics",
    summary="Digital Forgery & ELA Tamper Forensics",
    description="Inspects images for digital manipulation, Error Level Analysis (ELA) divergence, copy-move splicing, and signatures.",
)
async def analyze_document_forensics(
    file: UploadFile = File(...),
    api_key: str = Depends(verify_api_key),
) -> Dict[str, Any]:
    if not file.content_type.startswith("image/") and not file.filename.lower().endswith((".png", ".jpg", ".jpeg", ".tiff")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image format for pixel-level forensics analysis.",
        )

    file_bytes = await file.read()
    return DocumentForensicsService.analyze_tampering(file_bytes, file.filename)
