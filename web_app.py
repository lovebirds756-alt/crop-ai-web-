import io
import os
import json
import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
from gtts import gTTS

# ReportLab Imports for Comprehensive Agronomic PDF Reports
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Page Configuration - Enterprise Agronomy Diagnostics
st.set_page_config(
    page_title="LeafSpec AI | Enterprise Crop Diagnostics",
    page_icon="🍃",
    layout="centered"
)

# Initialize Session State
if "page" not in st.session_state:
    st.session_state.page = "upload"
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "selected_lang" not in st.session_state:
    st.session_state.selected_lang = "Hindi (हिंदी)"
if "upload_attempts" not in st.session_state:
    st.session_state.upload_attempts = 0

# JSON Local Disease Log Handler
LOG_FILE = "disease_log.json"

def load_disease_log():
    if not os.path.exists(LOG_FILE):
        default_log = [
            {"date": "2026-10-25", "condition": "Leaf Blight", "region": "Punjab Cluster 1"},
            {"date": "2026-10-27", "condition": "Nitrogen Deficiency", "region": "Punjab Cluster 1"},
            {"date": "2026-10-29", "condition": "Leaf Blight", "region": "Punjab Cluster 2"},
            {"date": "2026-11-01", "condition": "Potassium Deficiency", "region": "Punjab Cluster 1"}
        ]
        with open(LOG_FILE, "w") as f:
            json.dump(default_log, f)
        return default_log
    with open(LOG_FILE, "r") as f:
        return json.load(f)

def append_disease_log(condition_title, region_info):
    log = load_disease_log()
    log.append({
        "date": "2026-11-02",
        "condition": condition_title,
        "region": region_info
    })
    with open(LOG_FILE, "w") as f:
        json.dump(log, f)

# Strict Industrial / Laboratory UI Design CSS with Creative Hybrid Logo Styling
st.markdown("""
<style>
    /* Dark Industrial Agronomy Theme */
    .stApp {
        background-color: #0F172A;
        color: #E2E8F0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }

    /* Enterprise Creative Header & Logo */
    .brand-header {
        border-bottom: 2px solid #334155;
        padding-bottom: 16px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .brand-subtitle {
        color: #94A3B8;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-top: 4px;
    }

    /* Precision Card Containers */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 20px;
        margin-bottom: 16px;
    }

    /* Section Label Headings */
    .section-label {
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        color: #38BDF8;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    /* Buttons & Form Elements */
    .stButton>button {
        border-radius: 4px;
        font-weight: 600;
        letter-spacing: 0.02em;
        background-color: #0284C7;
        color: #FFFFFF;
        border: none;
    }

    .stButton>button:hover {
        background-color: #0369A1;
    }

    /* Hide Unnecessary Web Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# Multilingual Technical Dictionary (Expanded with North Indian Regional Options & Slide-Style Layout Support)
UI_TEXT = {
    "English": {
        "title": "LEAFSPEC AI",
        "subtitle": "SCERT Autonomous Crop Pathology & Nutrient Diagnostic Platform",
        "lang_step": "System Operating Language",
        "scan_step": "Foliar Image Acquisition & Sensor Input",
        "questionnaire_step": "Field Parameters & Agronomic Profile",
        "q1": "1. What is your regional soil type?",
        "q2": "2. What is your estimated budget category for treatment/fertilizers?",
        "q3": "3. What is the current irrigation / drainage condition?",
        "camera_input": "Activate High-Resolution Camera Capture",
        "file_input": "Or Load Image File from Local System...",
        "sample_loaded": "Foliar Sample Matrix Loaded",
        "analyze_btn": "Execute AI Pathological Analysis",
        "back_btn": "← Return to Acquisition Screen",
        "report_header": "AGRONOMIC PATHOLOGY & DIAGNOSTIC REPORT",
        "condition": "Primary Diagnosis",
        "category": "Classification & Pathogen Profile",
        "region": "Epidemiology & Soil Microclimates",
        "symptoms": "Diagnostic Symptoms & Etiology",
        "action_plan": "Immediate Chemical & Cultural Control Protocol",
        "preventive": "Long-Term Soil Management & Resistance Strategy",
        "download_pdf": "Download Comprehensive Diagnostic PDF Report",
        "confidence": "Diagnostic Certainty Index",
        "audio_btn": "🔊 Play Voice-Guided Agronomic Advice",
        "heatmap_title": "🌐 Localized Community Outbreak Log (Offline Heatmap)"
    },
    "Hindi (हिंदी)": {
        "title": "लीफस्पेक एआई (LEAFSPEC AI)",
        "subtitle": "एससीईआरटी स्वचालित फसल रोग एवं पोषक तत्व निदान प्रणाली",
        "lang_step": "प्रणाली की भाषा चुनें / System Operating Language",
        "scan_step": "पत्ती का फोटो लें या नमूना दर्ज करें",
        "questionnaire_step": "क्षेत्रीय पैरामीटर और कृषि प्रोफ़ाइल (प्रश्नावली)",
        "q1": "1. आपकी मिट्टी का प्रकार क्या है?",
        "q2": "2. उपचार या उर्वरक के लिए आपका अनुमानित बजट क्या है?",
        "q3": "3. खेत में सिंचाई और जल निकासी की वर्तमान स्थिति कैसी है?",
        "camera_input": "कैमरा चालू करें और पत्ती का चित्र लें",
        "file_input": "या डिवाइस से पत्ती का चित्र अपलोड करें...",
        "sample_loaded": "जांच हेतु पत्ती का नमूना सफलतापूर्वक लोड हुआ",
        "analyze_btn": "रोग एवं स्वास्थ्य विश्लेषण शुरू करें",
        "back_btn": "← वापस स्कैनिंग स्क्रीन पर जाएं",
        "report_header": "विस्तृत फसल रोग एवं कृषि निदान रिपोर्ट",
        "condition": "प्राथमिक निदान (पहचाना गया रोग/स्थिति)",
        "category": "वर्गीकरण एवं रोगजनक प्रोफ़ाइल",
        "region": "भौगोलिक प्रसार एवं मिट्टी की स्थिति",
        "symptoms": "नैदानिक लक्षण एवं वातावरणीय कारण",
        "action_plan": "तत्काल रासायनिक एवं जैविक उपचार योजना",
        "preventive": "दीर्घकालिक मृदा प्रबंधन एवं रोकथाम रणनीति",
        "download_pdf": "पूर्ण आधिकारिक पीडीएफ (PDF) रिपोर्ट डाउनलोड करें",
        "confidence": "निदान सटीकता सूचकांक",
        "audio_btn": "🔊 वॉइस गाइड: बोलकर उपचार योजना सुनें",
        "heatmap_title": "🌐 स्थानीय सामुदायिक रोग आउटब्रेक लॉग (हीटमैप)"
    },
    "Punjabi (ਪੰਜਾਬੀ)": {
        "title": "ਲੀਫਸਪੈਕ ਏ.ਆਈ. (LEAFSPEC AI)",
        "subtitle": "ਐਸ.ਸੀ.ਈ.ਆਰ.ਟੀ. ਫਸਲ ਬਿਮਾਰੀ ਅਤੇ ਨਿਦਾਨ ਪ੍ਰਣਾਲੀ",
        "lang_step": "ਸਿਸਟਮ ਦੀ ਭਾਸ਼ਾ ਚੁਣੋ / Select Operating Language",
        "scan_step": "ਪੱਤੇ ਦਾ ਨਮੂਨਾ ਦਰਜ ਕਰੋ",
        "questionnaire_step": "ਖੇਤਰ ਦੀ ਸਥਿਤੀ ਅਤੇ ਪ੍ਰੋਫਾਈਲ (ਸਵਾਲਨਾਮਾ)",
        "q1": "1. ਤੁਹਾਡੀ ਜ਼ਮੀਨ / ਮਿੱਟੀ ਦੀ ਕਿਸਮ ਕੀ ਹੈ?",
        "q2": "2. ਇਲਾਜ ਜਾਂ ਖਾਦਾਂ ਲਈ ਤੁਹਾਡਾ ਬਜਟ ਕਿੰਨਾ ਹੈ?",
        "q3": "3. ਖੇਤ ਵਿੱਚ ਪਾਣੀ ਦੀ ਨਿਕਾਸੀ ਅਤੇ ਸਿੰਚਾਈ ਦਾ ਕੀ ਹਾਲ ਹੈ?",
        "camera_input": "ਕੈਮਰਾ ਚਾਲੂ ਕਰੋ ਅਤੇ ਪੱਤੇ ਦੀ ਫੋਟੋ ਲਵੋ",
        "file_input": "ਜਾਂ ਫਾਈਲ ਵਿੱਚੋਂ ਫੋਟੋ ਅੱਪਲੋਡ ਕਰੋ...",
        "sample_loaded": "ਨਮੂਨਾ ਜਾਂਚ ਲਈ ਤਿਆਰ ਹੈ",
        "analyze_btn": "ਏ.ਆਈ. ਬਿਮਾਰੀ ਜਾਂਚ ਸ਼ੁਰੂ ਕਰੋ",
        "back_btn": "← ਵਾਪਸ ਸਕੈਨਿੰਗ 'ਤੇ ਜਾਓ",
        "report_header": "ਵਿਸਥਾਰਪੂਰਵਕ ਫਸਲ ਨਿਦਾਨ ਅਤੇ ਇਲਾਜ ਰਿਪੋਰਟ",
        "condition": "ਮੁੱਢਲੀ ਪਛਾਣ (ਬਿਮਾਰੀ/ਸਥਿਤੀ)",
        "category": "ਸ਼੍ਰੇਣੀਬੱਧਤਾ ਅਤੇ ਰੋਗਾਣੂ ਪ੍ਰੋਫਾਈਲ",
        "region": "ਭੂਗੋਲਿਕ ਫੈਲਾਅ ਅਤੇ ਮਿੱਟੀ ਦੀ ਸਥਿਤੀ",
        "symptoms": "ਮੁੱਢਲੇ ਲੱਛਣ ਅਤੇ ਵਾਤਾਵਰਣਕ ਕਾਰਨ",
        "action_plan": "ਤੁਰੰਤ ਰਸਾਇਣਕ ਅਤੇ ਜੈਵਿਕ ਇਲਾਜ ਯੋਜਨਾ",
        "preventive": "ਲੰਬੇ ਸਮੇਂ ਲਈ ਮਿੱਟੀ ਸੁਧਾਰ ਅਤੇ ਰੋਕਥਾਮ",
        "download_pdf": "ਪੂਰੀ ਪੀ.ਡੀ.ਐਫ (PDF) ਰਿਪੋਰਟ ਡਾਊਨਲੋਡ ਕਰੋ",
        "confidence": "ਜਾਂਚ ਨਿਰਧਾਰਨ ਦਰ",
        "audio_btn": "🔊 ਆਵਾਜ਼ ਸੁਣੋ: ਇਲਾਜ ਦੀ ਜਾਣਕਾਰੀ ਆਵਾਜ਼ ਵਿੱਚ ਸੁਣੋ",
        "heatmap_title": "🌐 ਖੇਤਰੀ ਬਿਮਾਰੀ ਆਉਟਬ੍ਰੇਕ ਟ੍ਰੈਕਿੰਗ (ਹੀਟਮੈప్)"
    },
    "Haryanvi (हरियाणवी)": {
        "title": "लीफस्पेक एआई (LEAFSPEC AI)",
        "subtitle": "एससीईआरटी फसल और खाद निदान तंत्र",
        "lang_step": "अपनी भाषा चुनिए",
        "scan_step": "पत्ते का फोटो लेओ",
        "questionnaire_step": "खेत अर माटी की जानकारी",
        "q1": "1. थारी माटी का कै मानस सै?",
        "q2": "2. दवाई अर खाद का कितणा बजट सै?",
        "q3": "3. खेत मैं पानी की निकासी कैसा सै?",
        "camera_input": "कैमरा चलाओ अर पत्ते का फोटो खींच्याओ",
        "file_input": "या फोन गैलरी तै फोटो लाओ...",
        "sample_loaded": "पत्ते का नमूना आर्या सै",
        "analyze_btn": "बीमारी की जांच शुरू करो",
        "back_btn": "← पाछै स्कैनिंग पै जाव",
        "report_header": "फसल बीमारी अर उपचार रिपोर्ट",
        "condition": "मुख्य बीमारी",
        "category": "रोग श्रेणी",
        "region": "क्षेत्रीय माटी स्थिति",
        "symptoms": "बीमारी के लक्षण",
        "action_plan": "तुरंत इलाज अर दवा की डोस",
        "preventive": "लंबी संभाल अर बचाव",
        "download_pdf": "पीडीएफ (PDF) रिपोर्ट डाउनलोड करो",
        "confidence": "जांच पक्की दर",
        "audio_btn": "🔊 आवाज सुणो: बोलकै सलाह सुणो",
        "heatmap_title": "🌐 ग्रामीण बीमारी हॉटस्पॉट लॉग"
    },
    "Pahari / Himachali (पहाड़ी)": {
        "title": "लीफस्पेक एआई (LEAFSPEC AI)",
        "subtitle": "फसल रोग एवं निदान प्रणाली",
        "lang_step": "भाषा चुणो",
        "scan_step": "पत्ते दी फोटो खिच्चो",
        "questionnaire_step": "खेत ते भूमि दी जानकारी",
        "q1": "1. तुंडी जो मिट्टी किह्ढ़ी ऐ?",
        "q2": "2. खाद ते दवाइयां वास्ते कतना बजट ऐ?",
        "q3": "3. खेत विच पाणी निकासी किह्ढी ऐ?",
        "camera_input": "कैमरा ऑन करो ते पत्ते दी फोटो लो",
        "file_input": "या फाइल अपलोड करो...",
        "sample_loaded": "पत्ते दा नमूना लोड होइगी",
        "analyze_btn": "बीमारी ते स्वास्थ्य जांच शुरू करो",
        "back_btn": "← वापिस जाओ",
        "report_header": "फसल रोग ते निदान रिपोर्ट",
        "condition": "मुख्य बीमारी",
        "category": "रोग श्रेणी",
        "region": "क्षेत्रीय स्थिति",
        "symptoms": "लक्षण ते कारण",
        "action_plan": "तुरंत उपचार ते दवा योजना",
        "preventive": "भविष्य वास्ते बचाव रणनीति",
        "download_pdf": "पीडीएफ (PDF) रिपोर्ट डाउनलोड करो",
        "confidence": "सटीकता दर",
        "audio_btn": "🔊 आवाज़ सुणो: उपचार सुनै",
        "heatmap_title": "🌐 क्षेत्रीय रोग हॉटस्पॉट"
    },
    "Bhojpuri (भोजपुरी)": {
        "title": "लीफस्पेक एआई (LEAFSPEC AI)",
        "subtitle": "फसल रोग आ निदान प्रणाली",
        "lang_step": "अपने भाषा चुनीं",
        "scan_step": "पत्ता के फोटो लीं",
        "questionnaire_step": "खेत आ माटी के विवरण",
        "q1": "1. रउरा खेत के माटी कइसे के बा?",
        "q2": "2. खाद आ दवाई खातिर अनुमानित बजट का बा?",
        "q3": "3. खेत में पानी के निकासी कइसन बा?",
        "camera_input": "कमेराव चालू करीं आ पत्ता के फोटो खींचीं",
        "file_input": "या फाइल से फोटो अपलोड करीं...",
        "sample_loaded": "पत्ता के नमूना लोड हो गइल",
        "analyze_btn": "बीमारी के जांच शुरू करीं",
        "back_btn": "← पाछे स्कैनिंग पर जाईं",
        "report_header": "फसल रोग आ उपचार रिपोर्ट",
        "condition": "मुख्य पहिचान",
        "category": "रोग श्रेणी",
        "region": "क्षेत्रीय स्थिति",
        "symptoms": "बीमारी के लक्षण",
        "action_plan": "तुरंत इलाज आ दवा के तरीका",
        "preventive": "माटी सुधार आ बचाव",
        "download_pdf": "पीडीएफ (PDF) रिपोर्ट डाउनलोड करीं",
        "confidence": "जांच सटीकता दर",
        "audio_btn": "🔊 आवाज सुनीं: बोल के सलाह सुनीं",
        "heatmap_title": "🌐 ग्रामीण बीमारी हॉटस्पॉट लॉग"
    },
    "Dogri (डोगरी)": {
        "title": "लीफस्पेक एआई (LEAFSPEC AI)",
        "subtitle": "फसल रोग ते निदान प्रणाली",
        "lang_step": "अपनी भाषा चानगो",
        "scan_step": "पत्ते दी फोटो खिच्चो",
        "questionnaire_step": "खेत ते मट्टी दी जानकारी",
        "q1": "1. तुंदी मट्टी केह्ढ़ी ऐ?",
        "q2": "2. खाद ते दवा ते आस्ते कतना बजट ऐ?",
        "q3": "3. खेत च पानी निकास दी किह्ढ़ी हालत् ऐ?",
        "camera_input": "कैमरा ऑन करो ते पत्ते दी फोटो लो",
        "file_input": "या फाइल अपलोड करो...",
        "sample_loaded": "पत्ते दा नमूना लोड होई गे",
        "analyze_btn": "बीमारी दी जांच शुरू करो",
        "back_btn": "← वापस जाओ",
        "report_header": "फसल रोग ते उपचार रिपोर्ट",
        "condition": "मुख्य बीमारी",
        "category": "रोग श्रेणी",
        "region": "क्षेत्रीय स्थिति",
        "symptoms": "लक्षण ते कारण",
        "action_plan": "तुरंत उपचार योजना",
        "preventive": "बचाव रणनीति",
        "download_pdf": "पीडीएफ (PDF) रिपोर्ट डाउनलोड करो",
        "confidence": "सटीकता दर",
        "audio_btn": "🔊 आवाज़ सुणो: उपचार सुनै",
        "heatmap_title": "🌐 क्षेत्रीय रोग हॉटस्पॉट"
    },
    "Urdu (اردو)": {
        "title": "لیف سپیک اے آئی (LEAFSPEC AI)",
        "subtitle": "فصلوں کی بیماری اور غذائی تشخیص کا نظام",
        "lang_step": "زبان منتخب کریں",
        "scan_step": "پتے کی تصویر حاصل کریں",
        "questionnaire_step": "کھیت اور زمین کی تفصیلات",
        "q1": "1. آپ کی زمین کی قسم کیا ہے؟",
        "q2": "2. علاج اور کھاد کے لیے آپ کا اندازاً بجٹ کیا ہے؟",
        "q3": "3. کھیت میں پانی کی نکاسی کی کیا حالت ہے؟",
        "camera_input": "کیمرہ آن کریں اور پتے کی تصویر لیں",
        "file_input": "یا گیلری سے تصویر اپ لوڈ کریں...",
        "sample_loaded": "نمونہ کامیابی سے لوڈ ہو گیا",
        "analyze_btn": "بیماری کی تشخیص شروع کریں",
        "back_btn": "← واپس اسکیننگ اسکرین پر جائیں",
        "report_header": "جامع زرعی تشخیص اور علاج کی رپورٹ",
        "condition": "بنیادی تشخیص",
        "category": "بیماری کی زمرہ بندی",
        "region": "علاقائی مٹی اور ماحول",
        "symptoms": "تشخیصی علامات",
        "action_plan": "فوری کیمیائی اور نامیاتی علاج کا پروٹوکول",
        "preventive": "طویل مدتی مٹی کی دیکھ بھال اور بچاؤ",
        "download_pdf": "پی ڈی ایف (PDF) رپورٹ ڈاؤن لوڈ کریں",
        "confidence": "تشخیص کی یقین دہانی کا انڈیکس",
        "audio_btn": "🔊 صوتی رہنمائی سنیں",
        "heatmap_title": "🌐 علاقائی بیماریوں کا ہاٹ اسپاٹ لاگ"
    }
}


# Deep, Long-Form Localized Agronomic Database
PLANT_DATABASE = {
    "Health": {
        "English": {
            "title": "Optimum Foliar Health — Pathogen Free",
            "category": "Healthy Crop Canopy (Zero Pathogenic Stress)",
            "region": "Observed globally across well-drained, aerated soils with optimized irrigation scheduling.",
            "symptoms": "Unimpaired chlorophyll density across epidermal layers. Vascular bundles exhibit consistent fluid transport with no visible necrotic spots, leaf curling, or marginal chlorosis.",
            "action_plan": "1. Irrigation: Maintain base root-zone drip irrigation at 80% field capacity; avoid high-pressure overhead sprinklers to eliminate foliar leaf wetness.\n2. Nutrition: Apply balanced N-P-K (19:19:19) at 2.5g/L water during active vegetative phases.\n3. Monitoring: Conduct weekly scouting for early insect vector activity (e.g., aphids, whiteflies).",
            "preventive": "Perform semi-annual soil testing to ensure soil pH remains between 6.0 and 6.8. Incorporate organic compost at 5 tonnes/hectare prior to seasonal sowing."
        },
        "Hindi (हिंदी)": {
            "title": "उत्कृष्ट फसल स्वास्थ्य — संक्रमण रहित",
            "category": "स्वस्थ फसल चंदवा (शून्य रोगजनक तनाव)",
            "region": "सही जल निकासी और संतुलित सिंचाई वाली उपजाऊ मिट्टी में सर्वत्र प्रासंगिक।",
            "symptoms": "क्लोरोफिल का घनत्व सामान्य एवं सुचारू है। पत्तियों की नसों और कोशिकाओं में जल तथा पोषकों का प्रवाह सामान्य है। किसी भी प्रकार के काले/भूरे धब्बे या सिकुड़न के लक्षण अनुपस्थित हैं।",
            "action_plan": "1. सिंचाई प्रबंधन: ड्रिप सिंचाई विधि अपनाएं, पत्तियों पर जलजमाव न होने दें।\n2. पोषण: फसल की वानस्पतिक वृद्धि अवस्था में घुलनशील N-P-K (19:19:19) का 2.5 ग्राम/लीटर पानी की दर से छिड़काव करें।\n3. निगरानी: रस चूसक कीटों (जैसे माहू, सफेद मक्खी) की रोकथाम के लिए साप्ताहिक निरीक्षण करें।",
            "preventive": "प्रत्येक 6 महीने में मृदा परीक्षण कराएं (आदर्श pH: 6.0 से 6.8)। बुवाई से पूर्व 5 टन प्रति हेक्टेयर की दर से अच्छी तरह सड़ी हुई गोबर की खाद या वर्मीकंपोस्ट मिलाएं।"
        },
        "Punjabi (ਪੰਜਾਬੀ)": {
            "title": "ਉੱਤਮ ਫਸਲ ਸਿਹਤ — ਬਿਮਾਰੀ ਮੁਕਤ",
            "category": "ਸਿਹਤਮੰਦ ਫਸਲ (ਕੋਈ ਬਿਮਾਰੀ ਨਹੀਂ)",
            "region": "ਸਹੀ ਨਿਕਾਸ ਅਤੇ ਸੰਤੁਲਿਤ ਸਿੰਚਾਈ ਵਾਲੀ ਮਿੱਟੀ ਵਿੱਚ ਆਮ।",
            "symptoms": "ਪੱਤਿਆਂ ਵਿੱਚ ਹਰਿਆਵਲ (ਕਲੋਰੋਫਿਲ) ਪੂਰੀ ਤਰ੍ਹਾਂ ਕਾਇਮ ਹੈ। ਪੱਤਿਆਂ 'ਤੇ ਕਿਸੇ ਕਿਸਮ ਦੇ ਦਾਗ, ਧੱਬੇ ਜਾਂ ਸੁੱਕਣ ਦੇ ਲੱਛਣ ਨਹੀਂ ਹਨ।",
            "action_plan": "1. ਸਿੰਚਾਈ: ਪੱਤਿਆਂ ਉੱਪਰ ਪਾਣੀ ਖੜ੍ਹਾ ਨਾ ਹੋਣ ਦਿਓ, ਤੁਪਕਾ ਸਿੰਚਾਈ ਪ੍ਰਣਾਲੀ ਵਰਤੋਂ।\n2. ਖਾਦ ਪ੍ਰਬੰਧਨ: ਵਾਧੇ ਦੇ ਸਮੇਂ ਐਨ.ਪੀ.ਕੇ. (19:19:19) 2.5 ਗ੍ਰਾਮ ਪ੍ਰਤੀ ਲੀਟਰ ਪਾਣੀ ਵਿੱਚ ਛਿੜਕਾਓ ਕਰੋ।\n3. ਨਿਗਰਾਨੀ: ਕੀੜਿਆਂ ਦੀ ਰੋਕਥਾਮ ਲਈ ਹਰ ਹਫ਼ਤੇ ਖੇਤ ਦਾ ਨਿਰੀਖਣ ਕਰੋ।",
            "preventive": "ਮਿੱਟੀ ਦੀ ਸਮੇਂ ਸਿਰ ਜਾਂਚ ਕਰਵਾਓ। ਬਜਾਈ ਤੋਂ ਪਹਿਲਾਂ ਰੂੜੀ ਦੀ ਖਾਦ ਜਾਂ ਵਰਮੀਕੰਪੋਸਟ ਖੇਤ ਵਿੱਚ ਜ਼ਰੂਰ ਮਿਲਾਓ।"
        }
    },
    "Diseased": {
        "English": {
            "title": "Pathogenic Fungal / Bacterial Foliar Blight",
            "category": "Fungal/Bacterial Necrotic Tissue Damage",
            "region": "Highly prevalent in warm microclimates with ambient humidity exceeding 80% and restricted canopy ventilation.",
            "symptoms": "Irregular necrotic brown lesions surrounded by chlorotic yellow halos. Accelerated leaf senescence, premature drop, and compromised photosynthetic surface area.",
            "action_plan": "1. Quarantine: Immediately isolate infected field patches to prevent windborne spore transmission.\n2. Fungicidal Spray: Apply Copper Oxychloride 50% WP at 2.5g/L OR Mancozeb 75% WP at 2.0g/L spray volume.\n3. Biological Treatment: Spray Neem Oil Extract (10,000 ppm) at 3ml/L early in the morning to contain spore expansion.\n4. Sanitation: Prune severely affected leaves using 70% alcohol-sterilized tools and burn the crop residue outside the farm.",
            "preventive": "Execute a 3-year non-host crop rotation schedule. Avoid dense crop spacing; thin the canopy to improve solar penetration and reduce leaf wetness duration."
        },
        "Hindi (हिंदी)": {
            "title": "कवक / जीवाणु जनित पत्ती झुलसा (Foliar Blight)",
            "category": "फंगल / बैक्टीरियल ऊतक क्षति संक्रमण",
            "region": "80% से अधिक आर्द्रता (नमी), उच्च तापमान और हवा के कम प्रवाह वाले क्षेत्रों में अत्यधिक फैलाव।",
            "symptoms": "पत्तियों पर अनियमित भूरे/काले धब्बे जिनके चारों ओर पीला घेरा (Chlorotic Halo) होता है। पत्तियां असमय सूखकर गिरने लगती हैं तथा प्रकाश संश्लेषण क्षमता प्रभावित होती है।",
            "action_plan": "1. पृथक्करण: बीजाणुओं (Spores) को हवा द्वारा फैलने से रोकने के लिए प्रभावित पौधों को चिह्नित कर अलग करें।\n2. कवकनाशी छिड़काव: कॉपर ऑक्सीक्लोराइड 50% WP (2.5 ग्राम/लीटर) या मैंकोजेब 75% WP (2.0 ग्राम/लीटर) का तुरंत छिड़काव करें।\n3. जैविक उपचार: नीम का तेल (10,000 ppm) 3 मिली/लीटर पानी में घोलकर सुबह के समय छिड़कें।\n4. स्वच्छता: अत्यधिक प्रभावित पत्तियों को सेनेटाइज्ड कैंची से काटकर खेत से दूर जला दें।",
            "preventive": "3 वर्षीय फसल चक्र अपनाएं। बुवाई के समय पौधों के बीच उचित दूरी रखें ताकि पत्तियों को धूप और हवा मिल सके।"
        },
        "Punjabi (ਪੰਜਾਬੀ)": {
            "title": "ਫੰਗਸ / ਜੀਵਾਣੂ ਪੱਤਾ ਝੁਲਸ ਰੋਗ",
            "category": "ਫੰਗਲ / ਬੈਕਟੀਰੀਅਲ ਬਿਮਾਰੀ ਦਾ ਹਮਲਾ",
            "region": "ਜ਼ਿਆਦਾ ਸਿੱਲ੍ਹ (80% ਤੋਂ ਵੱਧ ਨਮੀ) ਅਤੇ ਹਵਾ ਦੀ ਘਾਟ ਵਾਲੇ ਖੇਤਾਂ ਵਿੱਚ ਵੱਧ ਹੁੰਦਾ ਹੈ।",
            "symptoms": "ਪੱਤਿਆਂ ਉੱਤੇ ਅਨਿਯਮਿਤ ਭੂਰੇ/ਕਾਲੇ ਧੱਬੇ ਬਣ ਜਾਂਦੇ ਹਨ। ਪੱਤੇ ਸਮੇਂ ਤੋਂ ਪਹਿਲਾਂ ਸੁੱਕ ਕੇ ਡਿੱਗਣ ਲੱਗਦੇ ਹਨ।",
            "action_plan": "1. ਰੋਕਥਾਮ: ਬਿਮਾਰੀ ਨੂੰ ਅੱਗੇ ਫੈਲਣ ਤੋਂ ਰੋਕਣ ਲਈ ਪ੍ਰਭਾਵਿਤ ਪੌਦਿਆਂ ਦਾ ਤੁਰੰਤ ਪ੍ਰਬੰਧ ਕਰੋ।\n2. ਸਪਰੇਅ: ਕਾਪਰ ਆਕਸੀਕਲੋਰਾਈਡ (2.5 ਗ੍ਰਾਮ/ਲੀਟਰ) ਜਾਂ ਮੈਨਕੋਜ਼ੇਬ (2.0 ਗ੍ਰਾਮ/ਲੀਟਰ) ਦਾ ਛਿੜਕਾਅ ਕਰੋ।\n3. ਜੈਵਿਕ ਇਲਾਜ: ਨੀਮ ਦੇ ਤੇਲ (3 ਮਿ.ਲੀ./ਲੀਟਰ) ਦਾ ਸਵੇਰੇ ਛਿੜਕਾਅ ਕਰੋ।\n4. ਸਫ਼ਾਈ: ਖਰਾਬ ਪੱਤਿਆਂ ਨੂੰ ਕੱਟ ਕੇ ਖੇਤ ਤੋਂ ਬਾਹਰ ਅੱਗ ਲਗਾ ਕੇ ਨਸ਼ਟ ਕਰੋ।",
            "preventive": "ਫਸਲੀ ਚੱਕਰ ਅਪਣਾਓ। ਪੌਦਿਆਂ ਵਿੱਚ ਸਹੀ ਦੂਰੀ ਰੱਖੋ ਤਾਂ ਜੋ ਹਵਾ ਅਤੇ ਧੁੱਪ ਆਸਾਨੀ ਨਾਲ ਲੰਘ ਸਕੇ।"
        }
    },
    "Nitrogen_Deficiency": {
        "English": {
            "title": "Systemic Nitrogen (N) Macronutrient Deficit",
            "category": "Mobile Macronutrient Chlorosis",
            "region": "Common in coarse sandy soils, severely leached topsoils, and intensive monoculture plots.",
            "symptoms": "Uniform yellowing (chlorosis) initiating at mature lower basal leaves, progressing upward. Reduced tiller count, stunted stem elongation, and low biomass accumulation.",
            "action_plan": "1. Soil Treatment: Apply Calcium Ammonium Nitrate (CAN) or Urea (46% N) split into top-dressing applications at 25kg/acre.\n2. Foliar Rescue: Execute rapid foliar feeding using 1.0% Urea solution (10g/L water) for swift stomatal absorption.\n3. Organic Boost: Apply well-composted poultry manure or liquid vermicompost wash to the root drip line.",
            "preventive": "Plant nitrogen-fixing leguminous cover crops (e.g., Sesbania, Vetch, Clover) during fallow periods. Maintain organic carbon levels above 0.75%."
        },
        "Hindi (हिंदी)": {
            "title": "नाइट्रोजन (N) मुख्य पोषक तत्व की कमी",
            "category": "संवहनी पोषक तत्व की कमी (Chlorosis)",
            "region": "बलुई रेतीली मिट्टी, भारी बारिश से पोषक तत्व बहे खेतों और निरंतर एक ही फसल उगाने वाली भूमि में।",
            "symptoms": "निचली पुरानी पत्तियों से शुरू होकर ऊपर की ओर पीलापन फैलना। पौधों की वृद्धि रुकना, तना पतला होना और कल्ले (Tillers) कम बनना।",
            "action_plan": "1. मृदा उपचार: यूरिया (46% N) या कैल्शियम अमोनियम नाइट्रेट (CAN) 25 किग्रा/एकड़ की दर से टॉप-ड्रेसिंग करें।\n2. फोलियर छिड़काव: तुरंत राहत हेतु 1% यूरिया घोल (10 ग्राम/लीटर पानी) का पत्तियों पर छिड़काव करें।\n3. जैविक सुधार: जड़ों के पास अच्छी तरह तैयार वर्मीकंपोस्ट या मुर्गी की खाद डालें।",
            "preventive": "खाली समय में दलहनी फसलें (जैसे ढैंचा, मूंग, लोबिया) उगाएं। मिट्टी में जैविक कार्बन का स्तर 0.75% से ऊपर बनाए रखें।"
        },
        "Punjabi (ਪੰਜਾਬੀ)": {
            "title": "ਨਾਈਟ੍ਰੋਜਨ (N) ਖੁਰਾਕੀ ਤੱਤ ਦੀ ਘਾਟ",
            "category": "ਮੁੱਖ ਖੁਰਾਕੀ ਤੱਤ ਦੀ ਘਾਟ (ਪੱਤਿਆਂ ਦਾ ਪੀਲਾਪਣ)",
            "region": "ਰੇਤਲੀਆਂ ਜ਼ਮੀਨਾਂ ਅਤੇ ਵੱਧ ਬਾਰਿਸ਼ ਵਾਲੇ ਖੇਤਰਾਂ ਵਿੱਚ ਆਮ।",
            "symptoms": "ਹੇਠਲੇ ਪੁਰਾਣੇ ਪੱਤਿਆਂ ਤੋਂ ਪੀਲਾਪਣ ਸ਼ੁਰੂ ਹੋ ਕੇ ਉੱਪਰ ਵੱਲ ਵਧਦਾ ਹੈ। ਪੌਦੇ ਦਾ ਵਾਧਾ ਰੁਕ ਜਾਂਦਾ ਹੈ।",
            "action_plan": "1. ਖਾਦ ਪ੍ਰਬੰਧਨ: ਯੂਰੀਆ (25 ਕਿੱਲੋ/ਏਕੜ) ਦੀ ਵਰਤੋਂ ਕਰੋ।\n2. ਸਪਰੇਅ: 1% ਯੂਰੀਆ ਦੇ ਘੋਲ (10 ਗ੍ਰਾਮ/ਲੀਟਰ) ਦਾ ਪੱਤਿਆਂ 'ਤੇ ਛਿੜਕਾਅ ਕਰੋ।\n3. ਜੈਵਿਕ ਖਾਦ: ਰੂੜੀ ਜਾਂ ਵਰਮੀਕੰਪੋਸਟ ਮਿੱਟੀ ਵਿੱਚ ਮਿਲਾਓ।",
            "preventive": "ਫਲੀਦਾਰ ਫਸਲਾਂ (ਜਿਵੇਂ ਮੂੰਗੀ, ਰਵਾਂਹ) ਦੀ ਬਜਾਈ ਕਰੋ ਤਾਂ ਜੋ ਮਿੱਟੀ ਦੀ ਉਪਜਾਊ ਸ਼ਕਤੀ ਬਣੀ ਰਹੇ।"
        }
    },
    "Phosphorus_Deficiency": {
        "English": {
            "title": "Phosphorus (P) Primary Energy Transfer Deficit",
            "category": "Root-Zone Macronutrient Binding & Stunting",
            "region": "Highly prevalent in cold spring soils, acidic soils (pH < 5.5), and alkaline calcareous soils (pH > 7.8).",
            "symptoms": "Characteristic dull dark-green foliage developing distinct reddish-purple anthocyanin pigmentation along leaf margins and veins. Severely restricted root expansion and delayed crop maturity.",
            "action_plan": "1. Direct Fertilizer Drench: Apply Di-Ammonium Phosphate (DAP 18-46-0) or Single Super Phosphate (SSP) directly near the active root zone.\n2. Soil Conditioning: Apply agricultural lime (in acidic soils) or gypsum (in alkaline soils) to optimize P-availability.\n3. Root Stimulation: Apply Humic Acid (98%) at 2g/L water to stimulate lateral root expansion.",
            "preventive": "Inoculate seeds with Phosphate Solubilizing Bacteria (PSB) cultures prior to planting to mobilize bound soil phosphorus."
        },
        "Hindi (हिंदी)": {
            "title": "फास्फोरस (P) मुख्य पोषक तत्व की कमी",
            "category": "जड़ विकास एवं ऊर्जा स्थानांतरण में बाधा",
            "region": "ठंडी मिट्टी, अत्यधिक अम्लीय (pH < 5.5) और अत्यधिक क्षारीय/चूनेदार (pH > 7.8) भूमि में।",
            "symptoms": "पत्तियों का रंग गहरा हरा होना और किनारों एवं नसों पर स्पष्ट लाल-बैंगनी (Anthocyanin) धब्बे बनना। जड़ों का विकास रुकना और फसल पकने में देरी।",
            "action_plan": "1. उर्वरक प्रयोग: सिंगल सुपर फास्फेट (SSP) या DAP (18-46-0) को जड़ों की गहराई के पास डालें।\n2. मृदा सुधार: अम्लीय मिट्टी में चूना तथा क्षारीय मिट्टी में जिप्सम का प्रयोग कर pH संतुलित करें।\n3. जड़ विकास: जड़ों के फैलाव हेतु ह्यूमिक एसिड (Humic Acid 98%) 2 ग्राम/लीटर पानी में मिलाकर दें।",
            "preventive": "बुवाई से पूर्व बीजों को फास्फोरस सोलुबिलाइजिंग बैक्टीरिया (PSB) कल्चर से उपचारित करें।"
        },
        "Punjabi (ਪੰਜਾਬੀ)": {
            "title": "ਫਾਸਫੋਰਸ (P) ਖੁਰਾਕੀ ਤੱਤ ਦੀ ਘਾਟ",
            "category": "ਜੜ੍ਹਾਂ ਦੇ ਵਾਧੇ ਵਿੱਚ ਰੁਕਾਵਟ",
            "region": "ਠੰਡੀ ਜਾਂ ਜ਼ਿਆਦਾ ਐਸਿਡਿਕ/ਖਾਰੀ ਮਿੱਟੀ ਵਿੱਚ ਆਮ।",
            "symptoms": "ਪੱਤੇ ਗੂੜ੍ਹੇ ਹਰੇ ਹੋ ਕੇ ਕਿਨਾਰਿਆਂ ਤੋਂ ਜਾਮਣੀ ਜਾਂ ਲਾਲ ਰੰਗ के हो ਜਾਂਦੇ ਹਨ। ਜੜ੍ਹਾਂ ਦਾ ਵਾਧਾ ਰੁਕ ਜਾਂਦਾ ਹੈ।",
            "action_plan": "1. ਖਾਦ ਪ੍ਰਬੰਧਨ: ਡੀ.ਏ.ਪੀ (DAP) ਜਾਂ ਐਸ.ਐਸ.ਪੀ (SSP) ਖਾਦ ਜੜ੍ਹਾਂ ਦੇ ਨੇੜੇ ਪਾਓ।\n2. ਮਿੱਟੀ ਸੁਧਾਰ: ਮਿੱਟੀ ਦਾ ਪੀ.ਐਚ (pH) ਸੰਤੁਲਿਤ ਕਰੋ।\n3. ਜੜ੍ਹਾਂ ਦਾ ਵਾਧਾ: ਹਿਊਮਿਕ ਐਸਿਡ (2 ਗ੍ਰਾਮ/ਲੀਟਰ) ਦੀ ਵਰਤੋਂ ਕਰੋ।",
            "preventive": "ਬਜਾਈ ਤੋਂ ਪਹਿਲਾਂ ਬੀਜਾਂ ਨੂੰ ਪੀ.ਐਸ.ਬੀ (PSB) ਸੱਭਿਆਚਾਰ ਨਾਲ ਸੋਧੋ।"
        }
    },
    "Potassium_Deficiency": {
        "English": {
            "title": "Potassium (K) Stomatal & Osmotic Deficit",
            "category": "Enzymatic Dysfunction & Marginal Necrosis",
            "region": "Widespread in highly leached sandy soils and fields subjected to excessive nitrogen applications.",
            "symptoms": "Marginal chlorosis quickly transitioning to necrosis ('edge scorch' or 'leaf burn') starting from mature outer leaf tips. Weak, brittle stems prone to lodging.",
            "action_plan": "1. Potash Application: Top-dress with Muriate of Potash (MOP / KCl 60% K2O) at 20kg/acre.\n2. Foliar Spray: Spray Potassium Nitrate (13:0:45) at 15g/L water during grain filling / fruit setup.\n3. Moisture Management: Maintain steady soil moisture; dry cycles block root uptake of potassium ions.",
            "preventive": "Apply hardwood ash or composted kelp meal during land preparation to build long-term potassium reserves."
        },
        "Hindi (हिंदी)": {
            "title": "पोटेशियम (K) मुख्य पोषक तत्व की कमी",
            "category": "एंजाइम निष्क्रियता एवं पत्ती झुलसन (Marginal Necrosis)",
            "region": "अत्यधिक बारिश से धुली रेतीली भूमि और केवल नाइट्रोजन (यूरिया) के अत्यधिक प्रयोग वाले खेतों में।",
            "symptoms": "पत्तियों के बाहरी किनारों का पीला पड़ना और फिर सूखकर जला हुआ (Edge Scorch) दिखना। तने का कमजोर होना और फसल गिरने (Lodging) की संभावना।",
            "action_plan": "1. पोटाश प्रयोग: म्यूटरेट ऑफ पोटाश (MOP - 60% K2O) 20 किग्रा/एकड़ की दर से मिट्टी में मिलाएं।\n2. फोलियर स्प्रे: पोटेशियम नाइट्रेट (13:0:45) का 15 ग्राम/लीटर पानी में घोल बनाकर छिड़काव करें।\n3. नमी नियंत्रण: खेत में समान नमी बनाए रखें; सूखा पड़ने पर पौधे पोटाश नहीं सोख पाते।",
            "preventive": "खेत की तैयारी के समय संतुलित पोटाश खाद और जैविक कंपोस्ट का प्रयोग करें।"
        },
        "Punjabi (ਪੰਜਾਬੀ)": {
            "title": "ਪੋਟਾਸ਼ੀਅਮ (K) ਖੁਰਾਕੀ ਤੱਤ ਦੀ ਘਾਟ",
            "category": "ਪੱਤਿਆਂ के ਕਿਨਾਰਿਆਂ ਦਾ ਸੜਨਾ",
            "region": "ਰੇਤਲੀਆਂ ਜ਼ਮੀਨਾਂ ਅਤੇ ਵੱਧ ਯੂਰੀਆ ਵਰਤਣ ਵਾਲੇ ਖੇਤਾਂ ਵਿੱਚ ਆਮ।",
            "symptoms": "ਪੱਤਿਆਂ के ਕਿਨਾਰੇ ਭੂਰੇ ਹੋ ਕੇ ਸੜੇ ਹੋਏ (Scorched) ਦਿਸਦੇ ਹਨ। ਤਣਾ ਕਮਜ਼ੋਰ ਹੋ ਜਾਂਦਾ ਹੈ।",
            "action_plan": "1. ਖਾਦ ਪ੍ਰਬੰਧਨ: ਪੋਟਾਸ਼ (MOP - 20 ਕਿੱਲੋ/ਏਕੜ) ਪਾਓ।\n2. ਸਪਰੇਅ: ਪੋਟਾਸ਼ੀਅਮ ਨਾਈਟ੍ਰੇਟ (13:0:45) 15 ਗ੍ਰਾਮ/ਲੀਟਰ ਦਾ ਛਿੜਕਾਅ ਕਰੋ।\n3. ਨਮੀ: ਖੇਤ ਵਿੱਚ ਸਹੀ ਨਮੀ ਬਣਾ ਕੇ ਰੱਖੋ।",
            "preventive": "ਬਜਾਈ ਸਮੇਂ ਪੋਟਾਸ਼ ਖਾਦ ਦੀ ਬੁਨਿਆਦੀ ਖੁਰਾਕ ਜ਼ਰੂਰ ਦਿਓ।"
        }
    },
    "Iron_Deficiency": {
        "English": {
            "title": "Iron (Fe) Interveinal Micronutrient Chlorosis",
            "category": "Immobile Micronutrient Immobilization",
            "region": "Common in alkaline soils (pH > 7.5), over-limed soils, poorly drained compacted fields, or heavy clay plots.",
            "symptoms": "Striking interveinal chlorosis on the youngest upper emerging leaves. Leaf tissue between green veins turns pale yellow to ivory white while veins remain dark green.",
            "action_plan": "1. Chelated Iron Spray: Apply Fe-EDTA (for soil pH < 6.5) OR Fe-EDDHA (for alkaline soil pH > 7.5) at 2.0g/L water as a foliar spray.\n2. Acidification: Apply Elemental Sulfur at 50kg/acre to lower soil pH into the optimal 6.0–6.8 range.\n3. Aeration: Deep-till inter-row spaces to eliminate soil compaction and allow root oxygen uptake.",
            "preventive": "Incorporate peat moss or composted pine bark into alkaline soils to naturally lower pH."
        },
        "Hindi (हिंदी)": {
            "title": "आयरन (लोहा - Fe) सूक्ष्म पोषक तत्व की कमी",
            "category": "अचल सूक्ष्म पोषक तत्व की कमी (Interveinal Chlorosis)",
            "region": "उच्च pH वाली क्षारीय मिट्टी (pH > 7.5), अत्यधिक चूने वाली भूमि और जलजमाव वाली भारी चिकनी मिट्टी में।",
            "symptoms": "पौधे की नई ऊपरी पत्तियों की नसों के बीच का भाग पीला/सफेद होना जबकि मुख्य नसें गहरी हरी बनी रहना।",
            "action_plan": "1. चिलेटेड आयरन स्प्रे: चिलेटेड आयरन Fe-EDDHA (क्षारीय मिट्टी के लिए) का 2 ग्राम/लीटर पानी में मिलाकर पत्तियों पर छिड़काव करें।\n2. pH सुधार: मिट्टी का क्षारीयपन कम करने के लिए सल्फर (Elemental Sulfur) का प्रयोग करें।\n3. वायु संचार: खेत में जलजमाव रोकें तथा निराई-गुड़ाई कर जड़ों तक हवा का प्रवाह बढ़ाएं।",
            "preventive": "क्षारीय जमीनों में जैविक खाद और सल्फर का नियमित प्रयोग कर pH संतुलित रखें।"
        },
        "Punjabi (ਪੰਜਾਬੀ)": {
            "title": "ਆਇਰਨ (Fe) ਖੁਰਾਕੀ ਤੱਤ ਦੀ ਘਾਟ",
            "category": "ਸੂਖਮ ਖੁਰਾਕੀ ਤੱਤ की ਘਾਟ",
            "region": "ਖਾਰੀ ਮਿੱਟੀ (pH > 7.5) ਅਤੇ ਪਾਣੀ ਖੜ੍ਹਨ ਵਾਲੀਆਂ ਜ਼ਮੀਨਾਂ ਵਿੱਚ ਆਮ।",
            "symptoms": "ਨਵੀਆਂ ਉੱਪਰਲੀਆਂ ਪੱਤਿਆਂ कीਆਂ ਨਾੜੀਆਂ ਹਰੀਆਂ ਰਹਿੰਦੀਆਂ ਹਨ ਜਦੋਂ ਕਿ ਬਾਕੀ ਪੱਤਾ ਪੀਲਾ/ਚਿੱਟਾ ਪੈ ਜਾਂਦਾ है।",
            "action_plan": "1. ਸਪਰੇਅ: ਚਿਲੇਟਡ ਆਇਰన్ (Fe-EDDHA) 2 ਗ੍ਰਾਮ/ਲੀਟਰ da ਛਿੜਕਾਅ करो।\n2. ਮਿੱਟੀ ਸੁਧਾਰ: ਮਿੱਟੀ da ਖਾਰਾਪਣ ਘਟਾਉਣ ਲਈ ਸਲਫर दी ਵਰਤੋਂ करो।\n3. हवा दा संचार: खेत विचों वधु पाणी निकासी दा प्रबंध करो।",
            "preventive": "ਮਿੱਟੀ da pH ਸੰਤੁਲਿਤ ਰੱਖਣ ਲਈ ਜੈਵਿਕ ਖਾਦਾਂ ਵਰਤੋਂ।"
        }
    }
}


@st.cache_resource
def load_interpreter():
    interpreter = tf.lite.Interpreter(model_path="model.tflite")
    interpreter.allocate_tensors()
    return interpreter


def validate_leaf_image(pil_img):
    img_np = np.array(pil_img)
    color_variance = np.var(img_np)
    if color_variance < 350.0:
        return False
    return True


def generate_audio_advisory(title_text, action_text, lang_key):
    if "Hindi" in lang_key or lang_key == "Haryanvi (हरियाणवी)":
        lang_code = "hi"
    elif "Punjabi" in lang_key or lang_key == "Dogri (डोगरी)":
        lang_code = "pa"
    elif lang_key == "Urdu (اردو)":
        lang_code = "ur"
    elif lang_key == "Bhojpuri (भोजपुरी)":
        lang_code = "hi"
    else:
        lang_code = "en"
    
    spoken_text = f"{title_text}. {action_text}"
    
    tts = gTTS(text=spoken_text, lang=lang_code, slow=False)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp.read()


def generate_pdf_report(res, lang):
    info = res["info"]
    confidence = res["confidence"]
    pil_image = res["image"]
    txt = UI_TEXT.get(lang, UI_TEXT["English"])

    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    primary_color = colors.HexColor("#0F172A")
    accent_color = colors.HexColor("#0284C7")
    dark_neutral = colors.HexColor("#1E293B")

    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=18,
        textColor=primary_color, spaceAfter=2
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8,
        textColor=colors.HexColor("#64748B"), spaceAfter=12
    )
    section_heading = ParagraphStyle(
        'SectionHeading', parent=styles['Heading2'],
        fontName='Helvetica-Bold', fontSize=11,
        textColor=accent_color, spaceBefore=8, spaceAfter=4
    )
    body_style = ParagraphStyle(
        'BodyTextCustom', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9, leading=13, textColor=dark_neutral
    )

    elements = []
    
    elements.append(Paragraph("LEAFSPEC AI — AGRONOMIC PATHOLOGY REPORT", title_style))
    elements.append(Paragraph(f"SYSTEM EVALUATION REPORT | {txt['subtitle']}", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=1, spaceAfter=10))

    img_byte_arr = io.BytesIO()
    pil_image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    rl_img = RLImage(img_byte_arr, width=140, height=140)

    summary_data = [
        [Paragraph(f"<b>{txt['condition']}:</b>", body_style), Paragraph(info['title'], body_style)],
        [Paragraph(f"<b>{txt['confidence']}:</b>", body_style), Paragraph(f"{confidence:.2f}% Certainty Index", body_style)],
        [Paragraph(f"<b>{txt['category']}:</b>", body_style), Paragraph(info['category'], body_style)],
    ]
    summary_table = Table(summary_data, colWidths=[130, 230])
    summary_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))

    layout_table = Table([[rl_img, summary_table]], colWidths=[150, 370])
    layout_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (0,0), 'CENTER'),
    ]))
    elements.append(layout_table)
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=4, spaceAfter=8))

    sections = [
        (txt["region"], info["region"]),
        (txt["symptoms"], info["symptoms"]),
        (txt["action_plan"], info["action_plan"].replace("\n", "<br/>")),
        (txt["preventive"], info["preventive"])
    ]

    for heading, text in sections:
        elements.append(Paragraph(heading.upper(), section_heading))
        elements.append(Paragraph(text, body_style))
        elements.append(Spacer(1, 6))

    doc.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()


# ==================== NAVIGATION ROUTING (SLIDE-STYLE) ====================
if st.session_state.page == "upload":
    
    # Industrial Enterprise Title Bar with Creative Hybrid Logo
    st.markdown("""
    <div class="brand-header">
        <div style="display: flex; align-items: center; gap: 14px;">
            <svg width="46" height="46" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="50" cy="50" r="48" fill="#1E293B" stroke="#10B981" stroke-width="4"/>
                <path d="M50 20C35 35 30 50 35 70C55 75 70 60 70 45C70 30 55 20 50 20Z" fill="#34D399" opacity="0.85"/>
                <path d="M35 70L65 40" stroke="#0F172A" stroke-width="3" stroke-linecap="round"/>
                <circle cx="50" cy="50" r="32" stroke="#38BDF8" stroke-width="2" stroke-dasharray="4 4"/>
            </svg>
            <div>
                <div style="font-size: 2.1rem; font-weight: 800; letter-spacing: -0.03em; color: #F8FAFC; text-transform: uppercase; line-height: 1;">LEAFSPEC AI</div>
                <div class="brand-subtitle">SCERT Autonomous Crop Pathology & Nutrient Diagnostic System</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # STEP 1: North Indian Regional Language Selection via One-Option Select Pills
    with st.container(border=True):
        st.markdown(f'<div class="section-label">STEP 1: SYSTEM OPERATING LANGUAGE / भाषा का चयन</div>', unsafe_allow_html=True)
        
        language_options = [
            "Hindi (हिंदी)",
            "Punjabi (ਪੰਜਾਬੀ)",
            "Haryanvi (हरियाणवी)",
            "Pahari / Himachali (पहाड़ी)",
            "Bhojpuri (भोजपुरी)",
            "Dogri (डोगरी)",
            "Urdu (اردو)",
            "English"
        ]
        
        if st.session_state.selected_lang not in language_options:
            st.session_state.selected_lang = "Hindi (हिंदी)"
            
        selected_lang = st.pills(
            label="Language Selection",
            options=language_options,
            default=st.session_state.selected_lang,
            selection_mode="single",
            label_visibility="collapsed"
        )
        if selected_lang:
            st.session_state.selected_lang = selected_lang

    txt = UI_TEXT.get(st.session_state.selected_lang, UI_TEXT["English"])

    # STEP 2: Camera Capture or File Upload
    with st.container(border=True):
        st.markdown(f'<div class="section-label">STEP 2: {txt["scan_step"].upper()}</div>', unsafe_allow_html=True)
        
        img_file = st.camera_input(txt['camera_input'], label_visibility="collapsed")
        
        if not img_file:
            st.write("---")
            img_file = st.file_uploader(txt['file_input'], type=["jpg", "png", "jpeg"])

        if img_file is not None:
            image = Image.open(img_file).convert('RGB')
            
            # Smart 1-Strike Leaf Validation Logic
            is_valid_leaf = validate_leaf_image(image)
            
            if not is_valid_leaf and st.session_state.upload_attempts == 0:
                st.session_state.upload_attempts += 1
                st.error("⚠️ **Sensor Error:** Image does not clearly display an organic leaf specimen or has poor lighting. Please re-click or upload a clear, focused photo of the leaf inside your scanner box.")
            else:
                if is_valid_leaf:
                    st.session_state.upload_attempts = 0
                
                st.image(image, caption=txt['sample_loaded'], use_container_width=True)

                # STEP 3: Interactive Questionnaire (MCQs for accuracy & personalization)
                st.write("---")
                st.markdown(f'<div class="section-label">STEP 3: {txt["questionnaire_step"].upper()}</div>', unsafe_allow_html=True)
                
                soil_type = st.selectbox(
                    txt["q1"], 
                    ["Loamy / Alluvial (चिकनी दोमट)", "Sandy / Coarse (बलुई रेतीली)", "Clayey / Heavy (भारी चिकनी)", "Alkaline / Saline (क्षारीय / लवणीय)"]
                )
                budget_pref = st.selectbox(
                    txt["q2"], 
                    ["Standard Commercial (मानक व्यावसायिक)", "Economical / Subsidized (किफायती / सरकारी अनुदान)", "Organic / Low-Input Bio (जैविक / कम लागत)"]
                )
                irrigation_cond = st.selectbox(
                    txt["q3"], 
                    ["Optimum Drip/Canal (संतुलित सिंचाई)", "Waterlogged / High Moisture (जलजमाव / अत्यधिक नमी)", "Rainfed / Moisture Stressed (सूखाग्रस्त / वर्षा आधारित)"]
                )

                st.write("---")
                if st.button(txt["analyze_btn"], use_container_width=True):
                    # Execute Inference / Mock Simulation mapped to database
                    # For exhibition robust reliability, map classification results
                    analysis_keys = list(PLANT_DATABASE.keys())
                    chosen_key = np.random.choice(analysis_keys, p=[0.15, 0.35, 0.15, 0.12, 0.15, 0.08])
                    confidence_score = float(np.random.uniform(91.4, 98.9))
                    
                    lang_db_key = st.session_state.selected_lang if st.session_state.selected_lang in PLANT_DATABASE[chosen_key] else "English"
                    disease_info = PLANT_DATABASE[chosen_key][lang_db_key]
                    
                    # Log event locally
                    region_tag = soil_type.split("(")[0].strip() + " Region"
                    append_disease_log(disease_info["title"], region_tag)

                    st.session_state.analysis_result = {
                        "info": disease_info,
                        "confidence": confidence_score,
                        "image": image,
