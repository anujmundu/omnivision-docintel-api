"""
Document Type Classification Endpoints.
"""

from fastapi import APIRouter, Form, Depends, HTTPException, status
from ....schemas.doc_schema import DocumentClassificationResponse
from ....services.model_service import DocumentClassifierService
from ....core.security import verify_api_key

router = APIRouter()


@router.post(
    "/classify",
    response_model=DocumentClassificationResponse,
    summary="Classify Document Type",
    description="Categorizes documents into INVOICE, RECEIPT, ID_CARD, CONTRACT, or SHIPPING_MANIFEST.",
)
async def classify_document_type(
    text: str = Form(..., description="Raw text snippet or header of the document"),
    api_key: str = Depends(verify_api_key),
):
    if not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text snippet cannot be empty.",
        )

    return DocumentClassifierService.classify_document(text)
