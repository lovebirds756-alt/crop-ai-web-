import io
import time
from datetime import datetime
import numpy as np
from PIL import Image
import streamlit as st
import tensorflow as tf

# Optional Serial Import for Arduino Telemetry
try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

# ReportLab Imports for PDF Generation
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# ==========================================
# 1. PAGE CONFIGURATION & DARK GRADIENT THEME
# ==========================================
st.set_page_config(
    page_title="Cellular Vision — Edge AI Botanical Explorer",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Greenish-Blue Gradient Theme CSS + Floating Emoji Keyframe Animation
st.markdown("""
<style>
    /* Dark Greenish-Blue Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #0b1d20 0%, #112d32 40%, #194341 80%, #0d2818 100%);
        color: #e0f2f1;
    }
    
    /* Headers */
    .main-header { 
        font-size: 2.5rem; 
        background: linear-gradient(90deg, #80cbc4, #a7ffeb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800; 
        text-align: center; 
        margin-bottom: 0px; 
    }
    .sub-header { 
        font-size: 1.1rem; 
        color: #b2dfdb; 
        text-align: center; 
        margin-bottom: 25px; 
    }
    
    /* Dark Glassmorphism Cards */
    .metric-card { 
        background: rgba(255, 255, 255, 0.05); 
        backdrop-filter: blur(10px);
        border-radius: 12px; 
        padding: 18px; 
        border-left: 5px solid #26a69a; 
        margin-bottom: 15px; 
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }

    /* Floating Emoji Container & Keyframe Animations */
    .emoji-container {
        position: relative;
        width: 100%;
        height: 80px;
        overflow: hidden;
        margin-bottom: 10px;
    }
    
    .floating-emoji {
        position: absolute;
        bottom: -20px;
        font-size: 2rem;
        animation: floatUp 3s ease-out infinite;
        opacity: 0;
    }
    
    .e1 { left: 10%; animation-delay: 0s; }
    .e2 { left: 30%; animation-delay: 0.4s; }
    .e3 { left: 50%; animation-delay: 0.2s; }
    .e4 { left: 70%; animation-delay: 0.6s; }
    .e5 { left: 88%; animation-delay: 0.3s; }

    @keyframes floatUp {
        0% { transform: translateY(0) scale(0.5) rotate(0deg); opacity: 1; }
        50% { opacity: 0.9; }
        100% { transform: translateY(-100px) scale(1.3) rotate(25deg); opacity: 0; }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HARDWARE & MODEL SETUP
# ==========================================
labels = [
    "Apple - Apple Scab", "Apple - Black Rot", "Apple - Cedar Apple Rust", "Apple - Healthy",
    "Corn - Cercospora Leaf Spot", "Corn - Common Rust", "Corn - Northern Leaf Blight", "Corn - Healthy",
    "Potato - Early Blight", "Potato - Late Blight", "Potato - Healthy",
    "Tomato - Bacterial Spot", "Tomato - Early Blight", "Tomato - Late Blight", "Tomato - Healthy"
]

@st.cache_resource
def load_tflite_model():
    interpreter = tf.lite.Interpreter(model_path="model.tflite")
    interpreter.allocate_tensors()
    return interpreter

try:
    interpreter = load_tflite_model()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    model_loaded = True
except Exception as e:
    model_loaded = False

def send_serial_command(command, port="COM3", baudrate=9600):
    if not SERIAL_AVAILABLE:
        return "Serial library not installed."
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(1.5)
        ser.write(command.encode())
        ser.close()
        return f"Signal '{command}' sent to {port}."
    except Exception as e:
        return f"Hardware offline: {e}"

# ==========================================
# 3. REPORT GENERATOR FUNCTIONS
# ==========================================
def generate_text_report(disease_name, confidence, status_type, pH_range, remedies):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""
====================================================================
               CELLULAR VISION - DIAGNOSTIC REPORT                  
====================================================================
Timestamp          : {timestamp}
Diagnosis          : {disease_name}
Model Confidence   : {confidence:.2f}%
Status Severity    : {status_type.upper()}

--------------------------------------------------------------------
1. AGRONOMIC & SOIL PROFILE
--------------------------------------------------------------------
Optimal Soil pH    : {pH_range}
Status Indicator   : {status_type} (Hardware Telemetry Triggered)

--------------------------------------------------------------------
2. ACTIONABLE TREATMENT & REMEDIATION PROTOCOL
--------------------------------------------------------------------
{remedies}

--------------------------------------------------------------------
Generated by Cellular Vision Edge AI Platform
====================================================================
""".strip()

def generate_pdf_report(disease_name, confidence, status_type, pH_range, remedies):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()

    NAVY = colors.HexColor("#0d1f2d")
    GREEN = colors.HexColor("#1b4332")
    TEAL = colors.HexColor("#2a9d8f")
    DARK_TEXT = colors.HexColor("#2b2d42")

    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=20, textColor=NAVY, spaceAfter=4)
    subtitle_style = ParagraphStyle('DocSubtitle', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=10, textColor=TEAL, spaceAfter=15)

    story.append(Paragraph("🍃 Cellular Vision — Diagnostic Summary", title_style))
    story.append(Paragraph("AI-Powered Botanical Explorer & Edge Telemetry Report", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=GREEN, spaceAfter=15))

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    table_data = [
        [Paragraph("<b>Parameter</b>", styles['Normal']), Paragraph("<b>Value / Assessment</b>", styles['Normal'])],
        ["Generated Timestamp", timestamp],
        ["Identified Condition", disease_name],
        ["Model Confidence Score", f"{confidence:.2f}%"],
        ["Health Classification", status_type.capitalize()],
        ["Recommended Soil pH Target", pH_range]
    ]

    t = Table(table_data, colWidths=[180, 350])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor("#f1faee")),
        ('TEXTCOLOR', (0, 0), (-1, -1), DARK_TEXT),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    sec_style = ParagraphStyle('SectionHeader', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=13, textColor=NAVY, spaceAfter=6)
    body_style = ParagraphStyle('BodyText', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=DARK_TEXT, leading=14)

    story.append(Paragraph("Actionable Remediation Protocol", sec_style))
    story.append(HRFlowable(width="100%", thickness=1, color=TEAL, spaceAfter=10))
    story.append(Paragraph(remedies.replace("\n", "<br/>"), body_style))
    story.append(Spacer(1, 20))

    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8, textColor=colors.HexColor("#8d99ae"), alignment=1)
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey, spaceAfter=10))
    story.append(Paragraph("Cellular Vision Edge AI Platform • Confidential Agronomic Diagnostic Export", footer_style))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ==========================================
# 4. STREAMLIT UI - 2-PAGE TAB NAVIGATION
# ==========================================
st.markdown('<div class="main-header">Cellular Vision — Edge AI Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Real-Time Foliar Diagnostics & Embedded Hardware Telemetry</div>', unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🛠️ Hardware & Settings")
com_port = st.sidebar.text_input("Arduino COM Port", value="COM3")
enable_hardware = st.sidebar.checkbox("Enable Serial Hardware", value=False)

# Tab Navigation for 2-Page Flow
tab1, tab2 = st.tabs(["📸 Page 1: Upload & Scan", "📊 Page 2: Diagnostic Results"])

with tab1:
    st.subheader("1. Input Foliar Sample")
    input_mode = st.radio("Select Source:", ["📁 Upload Image", "📸 Live Camera"])

    uploaded_file = None
    if input_mode == "📁 Upload Image":
        uploaded_file = st.file_uploader("Select leaf sample...", type=["jpg", "jpeg", "png"])
    else:
        uploaded_file = st.camera_input("Snap leaf photo")

    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Current Sample Loaded", width=350)
        
        # Analyze Button
        if st.button("🚀 Run AI Diagnosis & Fire Results"):
            with st.spinner("Processing Edge MobileNet Model & Hardware Signals..."):
                # Run Inference
                img_resized = image.resize((224, 224))
                input_data = np.expand_dims(np.array(img_resized, dtype=np.float32) / 255.0, axis=0)

                interpreter.set_tensor(input_details[0]['index'], input_data)
                interpreter.invoke()
                output_data = interpreter.get_tensor(output_details[0]['index'])[0]

                pred_idx = np.argmax(output_data)
                confidence_score = float(output_data[pred_idx] * 100) if max(output_data) <= 1.0 else float(output_data[pred_idx])
                raw_label = labels[pred_idx] if pred_idx < len(labels) else "Unknown Condition"

                if "Healthy" in raw_label:
                    status_type = "Healthy"
                    signal = "H"
                    ph_range = "6.0 - 7.0"
                    status_color = "#66bb6a"
                    remedies = "1. Plant status is optimal.\n2. Maintain current irrigation schedule.\n3. Continue weekly monitoring."
                elif "Blight" in raw_label or "Rust" in raw_label or "Spot" in raw_label:
                    status_type = "Infected (Biotic Stress)"
                    signal = "I"
                    ph_range = "5.8 - 6.5"
                    status_color = "#ef5350"
                    remedies = "1. Isolate leaf area to stop spore spread.\n2. Apply bio-fungicide spray.\n3. Switch to drip irrigation to keep canopy dry."
                else:
                    status_type = "Deficient (Abiotic Stress)"
                    signal = "D"
                    ph_range = "6.2 - 6.8"
                    status_color = "#ffa726"
                    remedies = "1. Test N-P-K micronutrients in soil.\n2. Add organic compost tea.\n3. Adjust soil pH toward 6.5."

                if enable_hardware:
                    hw_status = send_serial_command(signal, port=com_port)
                    st.sidebar.info(hw_status)

                # Store into Session State for Page 2
                st.session_state['results'] = {
                    'raw_label': raw_label,
                    'confidence_score': confidence_score,
                    'status_type': status_type,
                    'ph_range': ph_range,
                    'status_color': status_color,
                    'remedies': remedies,
                    'analyzed': True
                }
                
                st.success("Analysis Complete! Switch to 'Page 2: Diagnostic Results' above to view detailed report and floating emojis!")
                st.balloons()

with tab2:
    if st.session_state.get('results', {}).get('analyzed', False):
        res = st.session_state['results']

        # Floating Emojis Fire Up Animation
        st.markdown("""
        <div class="emoji-container">
            <span class="floating-emoji e1">🍃</span>
            <span class="floating-emoji e2">🌾</span>
            <span class="floating-emoji e3">⚡</span>
            <span class="floating-emoji e4">🔬</span>
            <span class="floating-emoji e5">✨</span>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("Diagnostic Telemetry Results")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown(f"### Condition Identified")
            st.code(res['raw_label'], language="text")
            
            st.markdown("### Confidence Metric")
            st.progress(min(int(res['confidence_score']), 100))
            st.write(f"**Model Score:** `{res['confidence_score']:.2f}%`")

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="margin:0; color:#b2dfdb;">Health Classification</h4>
                <p style="color:{res['status_color']}; font-size:1.4rem; font-weight:bold; margin:5px 0 0 0;">{res['status_type']}</p>
            </div>
            <div class="metric-card">
                <h4 style="margin:0; color:#b2dfdb;">Recommended Soil pH Target</h4>
                <p style="color:#e0f2f1; font-size:1.3rem; font-weight:bold; margin:5px 0 0 0;">{res['ph_range']}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📋 Actionable Remediation Protocol")
        st.info(res['remedies'])

        # One-Click Report Exports
        st.markdown("---")
        st.subheader("📄 Export Diagnostic Summary Report")

        text_report = generate_text_report(res['raw_label'], res['confidence_score'], res['status_type'], res['ph_range'], res['remedies'])
        pdf_buffer = generate_pdf_report(res['raw_label'], res['confidence_score'], res['status_type'], res['ph_range'], res['remedies'])

        c_pdf, c_txt = st.columns(2)
        with c_pdf:
            st.download_button(
                label="📥 Download PDF Report (.pdf)",
                data=pdf_buffer,
                file_name=f"CellularVision_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        with c_txt:
            st.download_button(
                label="📝 Download Text Report (.txt)",
                data=text_report,
                file_name=f"CellularVision_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )

    else:
        st.info("👈 Please upload an image on 'Page 1: Upload & Scan' and click 'Run AI Diagnosis' first to generate results.")
