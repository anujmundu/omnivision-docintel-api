"""
V1 API Route Aggregator.
"""

from fastapi import APIRouter
from .endpoints import audit, extract, classify, forensics, stream

api_router = APIRouter()

api_router.include_router(audit.router, prefix="/document", tags=["Document Quality & Tamper Audit"])
api_router.include_router(extract.router, prefix="/document", tags=["Entity Extraction & OCR"])
api_router.include_router(classify.router, prefix="/document", tags=["Document Classification"])
api_router.include_router(forensics.router, prefix="/document", tags=["Digital Forgery & ELA Forensics (2026)"])
api_router.include_router(stream.router, prefix="/document", tags=["Real-Time Streaming Audit (2026)"])
