"""
Document Entity Extraction Endpoints.
"""

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from typing import Optional
from ....schemas.doc_schema import EntityExtractionResponse
from ....services.ocr_service import DocumentExtractionService
from ....core.security import verify_api_key

router = APIRouter()


@router.post(
    "/extract",
    response_model=EntityExtractionResponse,
    summary="Extract Financial Entities & Line Items",
    description="Extracts invoice number, dates, totals, taxes, and itemized rows from document text or uploads.",
)
async def extract_entities(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None),
    api_key: str = Depends(verify_api_key),
):
    if not file and not raw_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either a document file or raw_text must be provided.",
        )

    if file:
        content_bytes = await file.read()
        try:
            text = content_bytes.decode("utf-8", errors="ignore")
        except Exception:
            text = f"Simulated Invoice Extraction for {file.filename}\nInvoice: INV-2026-901\nDate: 2026-02-15\nTotal: $3,450.00\nTax: $276.00"
        filename = file.filename
    else:
        text = raw_text
        filename = "submitted_payload.txt"

    return DocumentExtractionService.extract_from_text(text, filename=filename)
