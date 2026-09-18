# System Architecture: OmniVision-DocIntel™ API (2026 Edition)
### Enterprise Document AI, Multimodal VLM, Digital Forgery Forensics & Streaming REST Microservice

---

## 1. Executive Architectural Overview

OmniVision-DocIntel is a hardened, production-ready asynchronous microservice built on FastAPI, OpenCV, and Multimodal Vision-Language heuristics. It combines pre-flight image quality validation, Error Level Analysis (ELA) pixel tampering forensics, zero-shot document classification, and real-time Server-Sent Events (SSE) streaming.

```mermaid
graph TD
    subgraph Client & Edge Layer
        Client[Client Application / Webhook] --> Gate[FastAPI ASGI Gateway]
        Studio[Streamlit Interactive Studio Port 8503] --> Gate
    end

    subgraph Security & Traffic Control
        Gate --> Sec[Token-Bucket Rate Limiter<br/>60 req/min]
        Sec --> Auth[X-API-Key Validator<br/>Header Enforcement]
    end

    subgraph V1 API Microservice Layer
        Auth --> R1[POST /document/audit<br/>OpenCV CV Quality Check]
        Auth --> R2[POST /document/forensics<br/>Error Level Analysis ELA]
        Auth --> R3[POST /document/extract<br/>VLM & Structured Entity Parsing]
        Auth --> R4[POST /document/classify<br/>Zero-Shot Document Classifier]
        Auth --> R5[GET /document/stream-audit<br/>Server-Sent Events SSE Stream]
    end

    subgraph Service & Engine Layer
        R1 --> S1[VisionQualityService<br/>Laplacian Blur & Skew Angle]
        R2 --> S2[DocumentForensicsService<br/>Compression Residual Divergence]
        R3 --> S3[MultimodalVLMService<br/>Semantic Key-Value Extraction]
        R4 --> S4[DocumentClassifierService<br/>Invoice, Receipt, ID Card, Contract]
    end

    subgraph Telemetry & Production Observability
        S1 & S2 & S3 & S4 --> Obs1[Prometheus Telemetry /metrics]
        S1 & S2 & S3 & S4 --> Obs2[Structured OpenAPI 3.0 Contract /docs]
    end
```

---

## 2. Component Breakdown & Service Engines

### A. API Gateway & Security Core (`src/core/`)
- **Token-Bucket Rate Limiter (`security.py`):** In-memory sliding token bucket enforcing 60 requests/minute per client IP to prevent denial-of-service degradation.
- **Header-Based Authentication:** Strict `X-API-Key` credential validation guarding all functional endpoints.
- **CORS & Lifecycle Configuration:** Production-configured CORS middleware and graceful startup/shutdown lifespan handlers.

### B. Computer Vision Quality Inspection (`src/services/vision_service.py`)
- **Laplacian Variance Blur Filter:** Measures the second derivative of image luminance ($Var(\nabla^2 I)$) to detect out-of-focus mobile camera captures.
- **Hough Line Transform Skew Detection:** Evaluates document orientation angles, flagging scans skewed $> 15^\circ$ for automatic deskewing.
- **Grayscale Illumination Histogram:** Analyzes pixel intensity distributions to reject underexposed ($< 40$) or glare-blown overexposed ($> 225$) scans.

### C. Digital Forgery & ELA Forensics Engine (`src/services/forensics_service.py`)
- **Error Level Analysis (ELA):** Re-compresses candidate images at a 90% JPEG quantization level and computes the mathematical absolute difference ($|I_{\text{orig}} - I_{\text{resaved}}|$). Spliced, cloned, or digitally altered text exhibits elevated high-frequency error residuals ($Std > 18.0$).
- **Signature & Official Stamp Detector:** Segmented morphological analysis of the lower document quadrant to verify the presence of authorized signatures and corporate seals.

### D. Multimodal VLM & Entity Extraction (`src/services/vlm_service.py`)
- Zero-shot multimodal parsing that understands document semantics without rigid coordinate bounding boxes.
- Extracts merchant entities, dates, itemized line items, subtotals, and taxes from real thermal slips, scanned receipts, and international invoices.

### E. Real-Time Streaming Telemetry (`src/api/v1/endpoints/stream.py`)
- Server-Sent Events (SSE) streaming real-time JSON progression packets (`IMAGE_RECEIVED` $\rightarrow$ `BLUR_INSPECTED` $\rightarrow$ `ELA_FORENSICS_PASSED` $\rightarrow$ `VLM_ENTITIES_EMITTED`) with heartbeat liveness.

---

## 3. Production Deployment Blueprint

```
Container Footprint: Multi-stage Docker build under 200 MB
P95 Latency: < 65ms per document audit
Concurrency: Asynchronous event loop with non-blocking Pillow/OpenCV workers
Observability: Prometheus /metrics scraping endpoint + OpenAPI Swagger on /docs
```
