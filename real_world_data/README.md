# Authentic Real-World Scanned Documents Directory: OmniVision-DocIntel™

This directory contains **authentic, real-world scanned receipts, photographed invoices, and thermal retail receipts** downloaded directly from official open-source AI benchmark repositories (Mistral AI Cookbook, Azure SDK, Microsoft AI Fundamentals, JigsawStack OCR, and Veryfi).

---

### Downloaded Benchmark Documents & Direct URLs

| # | File Name | File Size & Dimensions | Document Type & Origin | Direct Download URL / Source |
|---|---|---|---|---|
| **1** | `01_mistral_ai_benchmark_receipt.png` | **3.0 MB**<br>*(High-res scan)* | **Mistral AI Official OCR Benchmark**: Authentic photographed commercial receipt used in Mistral's official document extraction cookbook. | [Mistral AI Cookbook](https://raw.githubusercontent.com/mistralai/cookbook/refs/heads/main/mistral/ocr/receipt.png) |
| **2** | `02_azure_document_intelligence_receipt.png` | **1.7 MB**<br>*(Commercial scan)* | **Azure Document Intelligence (Contoso Receipt)**: Official benchmark receipt from Microsoft Azure AI SDK test suite. | [Azure Python SDK Repo](https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/receipt/contoso-receipt.png) |
| **3** | `03_microsoft_ai_scanned_receipt.jpg` | **30.7 KB**<br>*(Thermal paper receipt)* | **Microsoft AI Fundamentals Benchmark**: Scanned thermal register receipt with authentic paper creases, vendor header, itemized tax, and card auth code. | [Microsoft Learning AI-900 Repo](https://raw.githubusercontent.com/MicrosoftLearning/AI-900-AIFundamentals/main/data/vision/receipt.jpg) |
| **4** | `04_jigsawstack_ocr_thermal_receipt.jpg` | **109.7 KB**<br>*(Photographed store slip)* | **JigsawStack OCR Test Suite**: Real thermal checkout receipt with print fading, skew, and uneven background lighting. | [JigsawStack OCR Repo](https://raw.githubusercontent.com/JigsawStack/ocr-test-files/refs/heads/main/sample_receipt.jpg) |
| **5** | `05_veryfi_commercial_receipt_audit.jpg` | **2.4 MB**<br>*(Full commercial invoice/receipt)* | **Veryfi Financial Document Audit**: Real-world commercial expense receipt with itemized line items, tips, and signature field. | [Veryfi Python SDK Repo](https://raw.githubusercontent.com/veryfi/veryfi-python/master/tests/assets/receipt_public.jpg) |

---

### How to Test in the Browser UI & API
1. **Interactive Streamlit Studio**:
   - Open `http://localhost:8503`.
   - In the **Digital Document Forensic Inspector** or **Multimodal VLM Field Extractor**, drag and drop any of the 5 images above.
   - Run **Error Level Analysis (ELA)** to inspect pixel compression residuals and verify authenticity.
   - Run the **VLM/OCR Extraction** to pull merchant name, total, date, and tax fields.
2. **FastAPI OpenAPI Swagger Documentation**:
   - Open `http://127.0.0.1:8000/docs`.
   - Test the `/api/v1/forensics/tampering-check` endpoint by uploading any of the real images.
   - Test the `/api/v1/documents/process` and `/api/v1/extract/receipt` endpoints.
