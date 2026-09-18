"""
Document Type Classification Engine.
Predicts whether a document is an INVOICE, RECEIPT, ID_CARD, or CONTRACT.
"""

import time
from ..schemas.doc_schema import DocumentType, DocumentClassificationResponse


class DocumentClassifierService:
    """Classifies documents into functional enterprise business domains."""

    KEYWORD_MAP = {
        DocumentType.INVOICE: ["invoice", "bill to", "remit to", "due date", "subtotal", "tax", "po number"],
        DocumentType.RECEIPT: ["receipt", "cashier", "subtotal", "visa", "change", "store", "terminal"],
        DocumentType.ID_CARD: ["passport", "driver license", "date of birth", "dob", "nationality", "republic", "identification"],
        DocumentType.SHIPPING_MANIFEST: ["bill of lading", "manifest", "consignee", "carrier", "freight", "gross weight"],
        DocumentType.CONTRACT: ["agreement", "parties", "hereby", "jurisdiction", "witnesseth", "in witness whereof"],
    }

    @classmethod
    def classify_document(cls, text_or_filename: str) -> DocumentClassificationResponse:
        start_time = time.time()
        lower_content = text_or_filename.lower()

        scores = {doc_type.value: 0.05 for doc_type in DocumentType if doc_type != DocumentType.UNKNOWN}

        for doc_type, keywords in cls.KEYWORD_MAP.items():
            for kw in keywords:
                if kw in lower_content:
                    scores[doc_type.value] += 0.25

        # Normalize probabilities
        total = sum(scores.values())
        probs = {k: round(v / total, 3) for k, v in scores.items()}

        best_type_str = max(probs, key=probs.get)
        best_prob = probs[best_type_str]

        predicted = DocumentType(best_type_str) if best_prob > 0.25 else DocumentType.INVOICE

        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        return DocumentClassificationResponse(
            filename=text_or_filename[:40],
            predicted_type=predicted,
            confidence=best_prob,
            class_probabilities=probs,
            processed_in_ms=elapsed_ms,
        )
