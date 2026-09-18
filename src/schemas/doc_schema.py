"""
Pydantic schemas for Document AI and Vision API contracts.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    INVOICE = "INVOICE"
    RECEIPT = "RECEIPT"
    ID_CARD = "ID_CARD"
    SHIPPING_MANIFEST = "SHIPPING_MANIFEST"
    CONTRACT = "CONTRACT"
    UNKNOWN = "UNKNOWN"


class ImageQualityMetrics(BaseModel):
    blur_score: float = Field(..., description="Laplacian variance (higher = sharper)")
    is_blurry: bool = Field(..., description="True if blur_score is below threshold")
    skew_angle_deg: float = Field(..., description="Estimated orientation skew in degrees")
    width_px: int
    height_px: int
    aspect_ratio: float
    channels: int
    mean_brightness: float = Field(..., description="0-255 average grayscale illumination")
    is_underexposed: bool
    is_overexposed: bool


class DocumentAuditResponse(BaseModel):
    filename: str
    processed_in_ms: float
    quality_verdict: str = Field(..., description="PASS, MARGINAL, or REJECT")
    quality_metrics: ImageQualityMetrics
    tamper_flags: List[str] = Field(default_factory=list)


class LineItem(BaseModel):
    item_description: str
    quantity: float = 1.0
    unit_price: float
    line_total: float


class EntityExtractionResponse(BaseModel):
    filename: str
    document_type: DocumentType
    confidence_score: float
    invoice_number: Optional[str] = None
    vendor_name: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    subtotal: Optional[float] = None
    tax_amount: Optional[float] = None
    total_amount: Optional[float] = None
    currency: str = "USD"
    line_items: List[LineItem] = Field(default_factory=list)
    raw_text_preview: Optional[str] = None


class DocumentClassificationResponse(BaseModel):
    filename: str
    predicted_type: DocumentType
    confidence: float = Field(..., ge=0.0, le=1.0)
    class_probabilities: Dict[str, float]
    processed_in_ms: float


class HealthResponse(BaseModel):
    status: str
    version: str
    service: str
    timestamp: str
