"""
OmniVision Agentic™ — Visual Document AI & Forensics Studio (Streamlit).
Allows clients and auditors to test document inspection, ELA digital forgery detection,
and multimodal VLM extraction directly in the browser.
"""

import sys
from pathlib import Path
import io
import json
import pandas as pd
from PIL import Image
import streamlit as st

# Setup sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.services.vision_service import VisionQualityService
from src.services.forensics_service import DocumentForensicsService
from src.services.vlm_service import MultimodalVLMService
from src.services.model_service import DocumentClassifierService
from src.core.config import settings


st.set_page_config(
    page_title="OmniVision Agentic™ | Document AI & Forensics Studio",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main { background-color: #0A0E17; color: #FFFFFF; }
    .metric-card {
        background: linear-gradient(135deg, #1A233A 0%, #101622 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        margin-bottom: 12px;
    }
    .metric-label { font-size: 0.8rem; color: #8F9CAE; text-transform: uppercase; letter-spacing: 1px; }
    .metric-val { font-size: 1.6rem; font-weight: 700; color: #FFFFFF; margin-top: 4px; }
    .badge-pass { color: #00E676; font-weight: bold; }
    .badge-warn { color: #FFB300; font-weight: bold; }
    .badge-fail { color: #FF5252; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("👁️ OmniVision Agentic™")
st.caption("Enterprise Document AI, Digital Forgery Forensics & VLM Extraction Studio • Built by Anuj")

st.sidebar.header("⚙️ Vision & Forensic Parameters")
blur_thresh = st.sidebar.slider("Laplacian Sharpness Threshold", 20.0, 300.0, float(settings.BLUR_THRESHOLD), step=10.0)
skew_tolerance = st.sidebar.slider("Max Acceptable Skew (Degrees)", 5.0, 30.0, 15.0, step=1.0)
st.sidebar.markdown("---")
st.sidebar.info("💡 **2026 Capability:** Combines OpenCV quality heuristics with Error Level Analysis (ELA) pixel forensics to catch tampered invoices before processing.")

# Sample Files Directory
sample_dir = root_dir / "demo_samples"
sample_files = list(sample_dir.glob("*.png")) + list(sample_dir.glob("*.jpg"))

col_upload, col_samples = st.columns([2, 1])

with col_upload:
    uploaded_file = st.file_uploader("Upload Document (PNG, JPG, TIFF)", type=["png", "jpg", "jpeg", "tiff"])

active_bytes = None
active_name = None

with col_samples:
    st.write("#### Or Select Real Test Benchmark:")
    if sample_files:
        chosen_sample = st.selectbox("Sample Document Gallery:", [f.name for f in sample_files])
        if st.button("🚀 Load Selected Benchmark File", use_container_width=True):
            target = sample_dir / chosen_sample
            active_bytes = target.read_bytes()
            active_name = target.name
    else:
        st.caption("No sample gallery files found in demo_samples/")

if uploaded_file:
    active_bytes = uploaded_file.read()
    active_name = uploaded_file.name

# Main Display
if active_bytes and active_name:
    st.markdown("---")
    preview_col, audit_col = st.columns([1, 2])

    with preview_col:
        st.write(f"### 📄 Document Preview: `{active_name}`")
        try:
            pil_img = Image.open(io.BytesIO(active_bytes))
            st.image(pil_img, use_container_width=True)
            st.caption(f"Resolution: {pil_img.size[0]} x {pil_img.size[1]} px | Mode: {pil_img.mode}")
        except Exception as e:
            st.error(f"Image load error: {e}")

    with audit_col:
        # Run Vision & Forensics Engines
        audit_res = VisionQualityService.audit_image(active_bytes, active_name)
        forensics_res = DocumentForensicsService.analyze_tampering(active_bytes, active_name)
        vlm_res = MultimodalVLMService.parse_multimodal_document(active_bytes, active_name)
        class_res = DocumentClassifierService.classify_document(active_name)

        # Top Metric Row
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            v_color = "#00E676" if audit_res.quality_verdict == "PASS" else ("#FFB300" if audit_res.quality_verdict == "MARGINAL" else "#FF5252")
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Quality Verdict</div>
                <div class="metric-val" style="color:{v_color};">{audit_res.quality_verdict}</div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Sharpness Score</div>
                <div class="metric-val">{audit_res.quality_metrics.blur_score:.1f}</div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Skew Angle</div>
                <div class="metric-val">{audit_res.quality_metrics.skew_angle_deg:+.1f}°</div>
            </div>
            """, unsafe_allow_html=True)
        with m4:
            f_color = "#00E676" if forensics_res["forgery_risk_score"] < 40 else ("#FFB300" if forensics_res["forgery_risk_score"] < 70 else "#FF5252")
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Forgery Risk</div>
                <div class="metric-val" style="color:{f_color};">{forensics_res['forgery_risk_score']:.0f}/100</div>
            </div>
            """, unsafe_allow_html=True)

        st.write("")

        # Detailed Analysis Tabs
        t1, t2, t3, t4 = st.tabs([
            "🔍 Computer Vision Inspection",
            "🛡️ ELA Forgery Forensics (2026)",
            "🧠 Multimodal VLM Extraction (2026)",
            "🏷️ Document Classification",
        ])

        with t1:
            st.write("#### Image Quality Metrics")
            q_metrics = [
                {"Metric": "Laplacian Blur Score", "Value": audit_res.quality_metrics.blur_score, "Status": "Sharp" if not audit_res.quality_metrics.is_blurry else "DEFOCUS BLUR DETECTED"},
                {"Metric": "Estimated Skew Angle", "Value": f"{audit_res.quality_metrics.skew_angle_deg}°", "Status": "Aligned" if abs(audit_res.quality_metrics.skew_angle_deg) <= skew_tolerance else "SKEWED"},
                {"Metric": "Mean Brightness (0-255)", "Value": f"{audit_res.quality_metrics.mean_brightness:.1f}", "Status": "Normal Illumination"},
                {"Metric": "Aspect Ratio", "Value": audit_res.quality_metrics.aspect_ratio, "Status": "Standard"},
            ]
            st.table(pd.DataFrame(q_metrics))
            if audit_res.tamper_flags:
                st.warning(f"⚠️ Quality Flags: {', '.join(audit_res.tamper_flags)}")
            else:
                st.success("✓ All quality checks passed successfully!")

        with t2:
            st.write("#### Error Level Analysis (ELA) & Tampering Diagnostics")
            st.caption("Analyzes JPEG compression error residuals to detect digitally pasted numbers or altered text.")
            st.write(f"**Forensic Verdict:** `{forensics_res['forensic_verdict']}`")
            st.write(f"**Mean ELA Residual:** `{forensics_res['ela_mean_residual']}` | **ELA Divergence:** `{forensics_res['ela_std_divergence']}`")
            st.write(f"**Signature Detected:** `{'YES' if forensics_res['signature_detected'] else 'NO'}`")
            st.write(f"**Corporate Seal/Stamp:** `{'YES' if forensics_res['corporate_stamp_detected'] else 'NO'}`")

            if forensics_res["forensic_flags"]:
                for flag in forensics_res["forensic_flags"]:
                    st.error(f"🚩 Forensic Flag: {flag}")
            else:
                st.success("✓ Pixel compression uniform. Zero copy-move splicing detected.")

        with t3:
            st.write("#### Multimodal VLM Zero-Shot Extraction")
            vlm_data = vlm_res["data"]
            st.json({
                "Document Subtype": vlm_data["document_subtype"],
                "Issuer": vlm_data["entity_name"],
                "Invoice Ref": vlm_data["invoice_reference"],
                "Total Amount": f"${vlm_data['gross_total']:,.2f}",
                "Tax Amount": f"${vlm_data['tax_total']:,.2f}",
                "Confidence": f"{vlm_data['confidence_score']*100:.1f}%",
                "Handwritten Notes Found": vlm_data["handwritten_annotations_found"],
            })
            if "line_items" in vlm_data:
                st.write("**Itemized Line Items:**")
                st.dataframe(pd.DataFrame(vlm_data["line_items"]), use_container_width=True)

        with t4:
            st.write("#### Document Domain Classification")
            st.write(f"**Predicted Type:** `{class_res.predicted_type.value}` (Confidence: {class_res.confidence*100:.1f}%)")
            st.bar_chart(pd.DataFrame(list(class_res.class_probabilities.items()), columns=["Type", "Probability"]).set_index("Type"))
else:
    st.info("👆 Please upload a document or select one of the real benchmark files from the gallery above to start testing.")
