import io
import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np

# ReportLab Imports for PDF Generation
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Page Configuration - Executive Agronomy Theme
st.set_page_config(
    page_title="Cellular Vision | AI Crop Diagnostics",
    page_icon="🌿",
    layout="centered"
)

# Initialize Session State
if "page" not in st.session_state:
    st.session_state.page = "upload"
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "selected_lang" not in st.session_state:
    st.session_state.selected_lang = "Hindi (हिंदी)"

# Modern Professional Styling (Clean, Minimal, Industrial-Grade)
st.markdown("""
<style>
    /* Clean Dark Agronomy Theme */
    .stApp {
        background: linear-gradient(180deg, #0B192C 0%, #1E3E62 100%);
        color: #F0F4F8;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }

    /* Executive Header Badge */
    .app-header {
        text-align: center;
        padding: 10px 0 20px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }

    .brand-title {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #FFFFFF;
        margin: 0;
    }

    .brand-subtitle {
        color: #94A3B8;
        font-size: 0.95rem;
        font-weight: 400;
        margin-top: 4px;
    }

    /* Professional Card Containers */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 8px;
        padding: 18px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }

    /* Custom Input Labels & Buttons */
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
        letter-spacing: 0.3px;
    }

    /* Hide Streamlit Branding Overhead */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# Multilingual UI Dictionary
UI_TEXT = {
    "English": {
        "title": "Cellular Vision",
        "subtitle": "AI Agricultural Diagnostics & Crop Disease Detection System",
        "lang_selector_label": "🌐 Select Preferred Language / भाषा चुनें",
        "camera_input": "📷 Capture Leaf Image via Camera",
        "file_input": "📁 Or Upload Crop Leaf File...",
        "sample_loaded": "Leaf Sample Captured for Processing",
        "analyze_btn": "Run AI Diagnostic Analysis",
        "back_btn": "← Back to Scanner",
        "report_header": "Crop Diagnostic Report",
        "condition": "Identified Condition",
        "category": "Diagnostic Classification",
        "region": "Prevalent Regions & Soil Profiles",
        "symptoms": "Environmental Triggers & Visible Symptoms",
        "remedy": "Recommended Treatment & Agricultural Action Plan",
        "download_pdf": "📄 Download Official PDF Report",
        "confidence": "Accuracy Confidence"
    },
    "Hindi (हिंदी)": {
        "title": "सेल्यूलर विज़न (Cellular Vision)",
        "subtitle": "एआई फसल रोग पहचान एवं कृषि निदान प्रणाली",
        "lang_selector_label": "🌐 कृपया अपनी भाषा चुनें / Select Language",
        "camera_input": "📷 कैमरे से प्रभावित पत्ती की फोटो लें",
        "file_input": "📁 या पत्ती की फोटो अपलोड करें...",
        "sample_loaded": "पत्ती का नमूना जांच के लिए तैयार है",
        "analyze_btn": "फसल रोग की जांच करें",
        "back_btn": "← वापस स्कैन पर जाएं",
        "report_header": "फसल स्वास्थ्य एवं रोग रिपोर्ट",
        "condition": "पहचाना गया रोग / स्थिति",
        "category": "रोग श्रेणी",
        "region": "प्रभावित क्षेत्र और मिट्टी का प्रकार",
        "symptoms": "पर्यावरणीय कारण एवं शुरुआती लक्षण",
        "remedy": "अनुशंसित उपचार एवं जैविक निवारण उपाय",
        "download_pdf": "📄 पीडीएफ रिपोर्ट डाउनलोड करें",
        "confidence": "जांच सटीकता"
    },
    "Punjabi (ਪੰਜਾਬੀ)": {
        "title": "ਸੈਲੂਲਰ ਵਿਜ਼ਨ (Cellular Vision)",
        "subtitle": "ਏ.ਆਈ. ਫਸਲ ਬਿਮਾਰੀ ਪਛਾਣ ਅਤੇ ਖੇਤੀਬਾੜੀ ਨਿਦਾਨ ਪ੍ਰਣਾਲੀ",
        "lang_selector_label": "🌐 ਆਪਣੀ ਭਾਸ਼ਾ ਚੁਣੋ / Select Language",
        "camera_input": "📷 ਕੈਮਰੇ ਨਾਲ ਪੱਤੇ ਦੀ ਫੋਟੋ ਖਿੱਚੋ",
        "file_input": "📁 ਜਾਂ ਪੱਤੇ ਦੀ ਫੋਟੋ ਅੱਪਲੋਡ ਕਰੋ...",
        "sample_loaded": "ਪੱਤੇ ਦਾ ਨਮੂਨਾ ਜਾਂਚ ਲਈ ਤਿਆਰ ਹੈ",
        "analyze_btn": "ਬਿਮਾਰੀ ਦੀ ਜਾਂਚ ਸ਼ੁਰੂ ਕਰੋ",
        "back_btn": "← ਵਾਪਸ ਸਕੈਨਰ 'ਤੇ ਜਾਓ",
        "report_header": "ਫਸਲ ਸਿਹਤ ਅਤੇ ਨਿਦਾਨ ਰਿਪੋਰਟ",
        "condition": "ਪਛਾਣੀ ਗਈ ਬਿਮਾਰੀ / ਸਥਿਤੀ",
        "category": "ਬਿਮਾਰੀ ਦੀ ਸ਼੍ਰੇਣੀ",
        "region": "ਪ੍ਰਭਾਵਿਤ ਖੇਤਰ ਅਤੇ ਮਿੱਟੀ ਦੀ ਕਿਸਮ",
        "symptoms": "ਵਾਤਾਵਰਣਕ ਕਾਰਨ ਅਤੇ ਲੱਛਣ",
        "remedy": "ਸਿਫਾਰਸ਼ ਕੀਤਾ ਇਲਾਜ ਅਤੇ ਜੈਵਿਕ ਰੋਕਥਾਮ",
        "download_pdf": "📄 ਪੀ.ਡੀ.ਐਫ. ਰਿਪੋਰਟ ਡਾਊਨਲੋਡ ਕਰੋ",
        "confidence": "ਜਾਂਚ ਦੀ ਨਿਰਧਾਰਨ ਦਰ"
    }
}


# Localized Botanical & Agricultural Database
PLANT_DATABASE = {
    "Health": {
        "English": {
            "title": "Healthy Foliage — No Infection Detected",
            "category": "Optimal Crop Health",
            "region": "Widespread across properly irrigated and balanced nutrient soils.",
            "conditions": "Sustained by adequate solar light (6–8 hrs/day), good aeration, and proper N-P-K balance.",
            "remedy": "• Continue regular deep-root irrigation cycle.\n• Perform routine soil testing every 6 months to maintain pH (6.0–6.8).\n• Apply organic compost during growth cycles to maintain soil organic matter."
        },
        "Hindi (हिंदी)": {
            "title": "स्वस्थ पत्ती — कोई रोग नहीं पाया गया",
            "category": "उत्तम फसल स्वास्थ्य",
            "region": "संतुलित सिंचाई और सही पोषण वाली मिट्टी में व्यापक।",
            "conditions": "पर्याप्त धूप (6-8 घंटे/दिन), अच्छी हवा और संतुलित एन-पी-के (N-P-K) पोषकों से बना रहता है।",
            "remedy": "• नियमित सिंचाई चक्र जारी रखें, पत्तियों पर जलजमाव से बचें।\n• मिट्टी के पी.एच (6.0-6.8) की नियमित जांच कराएं।\n• फसल चक्र के दौरान जैविक खाद या वर्मीकंपोस्ट का प्रयोग करें।"
        },
        "Punjabi (ਪੰਜਾਬੀ)": {
            "title": "ਸਿਹਤਮੰਦ ਪੱਤਾ — ਕੋਈ ਬਿਮਾਰੀ ਨਹੀਂ ਮਿਲੀ",
            "category": "ਉੱਤਮ ਫਸਲ ਸਿਹਤ",
            "region": "ਸਹੀ ਸਿੰਚਾਈ ਅਤੇ ਸੰਤੁਲਿਤ ਖਾਦ ਵਾਲੀ ਮਿੱਟੀ ਵਿੱਚ ਆਮ।",
            "conditions": "ਲੋੜੀਂਦੀ ਧੁੱਪ (6-8 ਘੰਟੇ/ਦਿਨ) ਅਤੇ ਸੰਤੁਲਿਤ ਪੋਸ਼ਕ ਤੱਤਾਂ ਨਾਲ ਸਿਹਤਮੰਦ ਰਹਿੰਦਾ ਹੈ।",
            "remedy": "• ਨਿਯਮਤ ਸਿੰਚਾਈ ਚੱਕਰ ਜਾਰੀ ਰੱਖੋ।\n• ਮਿੱਟੀ ਦੇ ਪੀ.ਐਚ. ਦੀ ਸਮੇਂ-ਸਮੇਂ 'ਤੇ ਜਾਂਚ ਕਰਵਾਓ।\n• ਖੇਤ ਵਿੱਚ ਜੈਵਿਕ ਰੂੜੀ ਜਾਂ ਵਰਮੀਕੰਪੋਸਟ ਦੀ ਵਰਤੋਂ ਕਰੋ।"
        }
    },
    "Diseased": {
        "English": {
            "title": "Pathogenic Stress / Foliar Infection",
            "category": "Fungal or Bacterial Leaf Infection",
            "region": "Common in high humidity zones and waterlogged, poorly ventilated fields.",
            "conditions": "Triggered by high canopy moisture, prolonged leaf wetness, or infected residue.",
            "remedy": "• Isolate affected crops to prevent fungal spore spreading.\n• Prune severely damaged leaves using sanitized shears.\n• Apply copper-based fungicide or neem oil solution early in the morning."
        },
        "Hindi (हिंदी)": {
            "title": "रोगजनक संक्रमण / फंगल प्रकोप",
            "category": "फंगल या बैक्टीरियल पत्ती संक्रमण",
            "region": "अधिक नमी वाले क्षेत्रों और कम हवादार/जलजमाव वाले खेतों में आम।",
            "conditions": "पत्तियों पर लगातार नमी, हवा की कमी या पुरानी संक्रमित फसल अवशेषों से होता है।",
            "remedy": "• बीमारी को फैलने से रोकने के लिए प्रभावित पौधों को अलग करें।\n• साफ़ कैंची से अत्यधिक प्रभावित पत्तियों की कटाई करें।\n• सुबह या देर शाम तांबे (कॉपर-आधारित) कवकनाशी या नीम तेल का छिड़काव करें।"
        },
        "Punjabi (ਪੰਜਾਬੀ)": {
            "title": "ਬਿਮਾਰੀ ਦਾ ਹਮਲਾ / ਫੰਗਸ ਦੀ ਲਾਗ",
            "category": "ਫੰਗਲ ਜਾਂ ਬੈਕਟੀਰੀਅਲ ਪੱਤੇ ਦੀ ਬਿਮਾਰੀ",
            "region": "ਵੱਧ ਨਮੀ ਅਤੇ ਪਾਣੀ ਦੇ ਖੜੋਤ ਵਾਲੇ ਖੇਤਾਂ ਵਿੱਚ ਆਮ।",
            "conditions": "ਪੱਤਿਆਂ 'ਤੇ ਲਗਾਤਾਰ ਸਿੱਲ੍ਹ ਅਤੇ ਹਵਾ ਦੀ ਘਾਟ ਕਾਰਨ ਬਿਮਾਰੀ ਵਧਦੀ ਹੈ।",
            "remedy": "• ਬਿਮਾਰੀ ਅੱਗੇ ਫੈਲਣ ਤੋਂ ਰੋਕਣ ਲਈ ਪ੍ਰਭਾਵਿਤ ਪੌਦਿਆਂ ਦਾ ਪ੍ਰਬੰਧ ਕਰੋ।\n• ਖਰਾਬ ਪੱਤਿਆਂ ਨੂੰ ਕੱਟ ਕੇ ਖੇਤ ਤੋਂ ਬਾਹਰ ਨਸ਼ਟ ਕਰੋ।\n• ਤਾਂਬੇ (कॉपर) આધારਿਤ ਫੰਗੀਸਾਈਡ ਜਾਂ ਨੀਮ ਦੇ ਤੇਲ ਦਾ ਛਿੜਕਾਅ ਕਰੋ।"
        }
    },
    "Nitrogen_Deficiency": {
        "English": {
            "title": "Nitrogen (N) Deficiency",
            "category": "Macronutrient Shortage (Lower Leaf Chlorosis)",
            "region": "Common in sandy, heavily leached, or low-organic soils.",
            "conditions": "Yellowing starts on older lower leaves as the plant transfers mobile N to upper shoots.",
            "remedy": "• Apply fast-acting nitrogenous fertilizer (Urea or Liquid Nitrogen foliar spray).\n• Add composted poultry manure or blood meal to the root zone.\n• Rotate with leguminous cover crops (peas, beans, clover) to fix nitrogen naturally."
        },
        "Hindi (हिंदी)": {
            "title": "नाइट्रोजन (N) की कमी",
            "category": "मुख्य पोषक तत्व की कमी (पत्तियों का पीलापन)",
            "region": "बलुई, अधिक पानी बहने वाली या कम जैविक पदार्थ वाली मिट्टी में आम।",
            "conditions": "निचली पुरानी पत्तियां पहले पीली पड़ती हैं क्योंकि पौधा नाइट्रोजन को नए ऊपरी भागों में भेजता है।",
            "remedy": "• त्वरित प्रभाव के लिए यूरिया का संतुलित प्रयोग या तरल नाइट्रोजन फोलियर स्प्रे करें।\n• जड़ों के पास अच्छी तरह सड़ी हुई गोबर की खाद या वर्मीकंपोस्ट डालें।\n• मिट्टी में नाइट्रोजन बढ़ाने के लिए दलहनी फसलों (चना, मूंग, मटर) का फसल चक्र अपनाएं।"
        },
        "Punjabi (ਪੰਜਾਬੀ)": {
            "title": "ਨਾਈਟ੍ਰੋਜਨ (N) ਦੀ ਘਾਟ",
            "category": "ਮੁੱਖ ਖੁਰਾਕੀ ਤੱਤ ਦੀ ਘਾਟ (ਪੱਤਿਆਂ ਦਾ ਪੀਲਾਪਣ)",
            "region": "ਰੇਤਲੀ ਅਤੇ ਘੱਟ ਜੈਵਿਕ ਮਾਦੇ ਵਾਲੀ ਮਿੱਟੀ ਵਿੱਚ ਆਮ।",
            "conditions": "ਹੇਠਲੇ ਪੁਰਾਣੇ ਪੱਤੇ ਪਹਿਲਾਂ ਪੀਲੇ ਹੁੰਦੇ ਹਨ।",
            "remedy": "• ਲੋੜ ਅਨੁਸਾਰ ਯੂਰੀਆ ਦਾ ਛਿੜਕਾਅ ਜਾਂ ਤਰਲ ਨਾਈਟ੍ਰੋਜਨ ਦੀ ਵਰਤੋਂ ਕਰੋ।\n• ਰੂੜੀ ਦੀ ਖਾਦ ਜਾਂ ਵਰਮੀਕੰਪੋਸਟ ਮਿੱਟੀ ਵਿੱਚ ਮਿਲਾਓ।\n• ਫਸਲੀ ਚੱਕਰ ਵਿੱਚ ਫਲੀਦਾਰ ਫਸਲਾਂ (ਮਟਰ, ਮੂੰਗੀ) ਦੀ ਬਜਾਈ ਕਰੋ।"
        }
    },
    "Phosphorus_Deficiency": {
        "English": {
            "title": "Phosphorus (P) Deficiency",
            "category": "Nutritional Impairment (Purplish Leaves & Stunted Roots)",
            "region": "Prevalent in cold spring soils, acidic soils (pH < 5.5), or highly alkaline soils.",
            "conditions": "Manifests as dark green, purple, or reddish discoloration along leaf edges and veins.",
            "remedy": "• Apply single superphosphate (SSP) or bone meal near the root zone.\n• Maintain soil pH between 6.0 and 7.0 to unlock bound soil phosphorus.\n• Inoculate soil with Mycorrhizal fungi to boost root absorption efficiency."
        },
        "Hindi (हिंदी)": {
            "title": "फास्फोरस (P) की कमी",
            "category": "पोषक तत्व की कमी (बैंगनी/लाल पत्तियां और कमजोर जड़ें)",
            "region": "ठंडी मिट्टी, अत्यधिक अम्लीय (pH < 5.5) या अत्यधिक क्षारीय मिट्टी में अधिक।",
            "conditions": "पत्तियों के किनारों और नसों पर गहरा हरा, लाल या बैंगनी रंग दिखाई देता है।",
            "remedy": "• जड़ों के पास सिंगल सुपर फास्फेट (SSP) या डी.ए.पी (DAP) का प्रयोग करें।\n• मिट्टी के पी.एच को 6.0 से 7.0 के बीच बनाए रखें ताकि फास्फोरस पौधों को मिल सके।\n• जड़ों के विकास के लिए माइकोराइजा जैविक उर्वरक का प्रयोग करें।"
        },
        "Punjabi (ਪੰਜਾਬੀ)": {
            "title": "ਫਾਸਫੋਰਸ (P) ਦੀ ਘਾਟ",
            "category": "ਖੁਰਾਕੀ ਤੱਤ ਦੀ ਘਾਟ (ਜਾਮਣੀ/ਲਾਲ ਪੱਤੇ)",
            "region": "ਠੰਡੀ ਜਾਂ ਜ਼ਿਆਦਾ ਐਸਿਡਿਕ ਮਿੱਟੀ ਵਿੱਚ ਆਮ।",
            "conditions": "ਪੱਤਿਆਂ ਦੇ ਕਿਨਾਰੇ ਜਾਮਣੀ ਜਾਂ ਲਾਲ ਰੰਗ ਦੇ ਹੋ ਜਾਂਦੇ ਹਨ।",
            "remedy": "• ਐਸ.ਐਸ.ਪੀ (SSP) ਜਾਂ ਡੀ.ਏ.ਪੀ (DAP) ਖਾਦ ਦੀ ਬੁਨਿਆਦੀ ਖੁਰਾਕ ਦਿਓ।\n• ਮਿੱਟੀ ਦਾ ਪੀ.ਐਚ. ਸੰਤੁਲਿਤ ਰੱਖੋ।\n• ਜੜ੍ਹਾਂ ਦੇ ਵਾਧੇ ਲਈ ਜੈਵਿਕ ਖਾਦਾਂ ਦੀ ਵਰਤੋਂ ਕਰੋ।"
        }
    },
    "Potassium_Deficiency": {
        "English": {
            "title": "Potassium (K) Deficiency",
            "category": "Enzymatic & Water Regulation Deficit",
            "region": "Frequent in sandy soils subject to heavy rainfall and leaching.",
            "conditions": "Visible as browning or scorching along leaf margins (edge burn).",
            "remedy": "• Apply Muriate of Potash (MOP) or Potassium Sulfate to soil base.\n• Wood ash or kelp meal can be applied as an organic potassium source.\n• Maintain uniform moisture; drought exacerbates potassium uptake blockage."
        },
        "Hindi (हिंदी)": {
            "title": "पोटेशियम (K) की कमी",
            "category": "पोषक तत्व की कमी (पत्तियों के किनारों का जलना/झुलसना)",
            "region": "रेतीली मिट्टी और भारी बारिश से धुली हुई जमीनों में आम।",
            "conditions": "पत्तियों के किनारे भूरे होकर सूखे या जले हुए दिखाई देते हैं।",
            "remedy": "• पोटाश (MOP) या पोटेशियम सल्फेट का संतुलित छिड़काव करें।\n• जैविक विकल्प के रूप में लकड़ी की राख (नियंत्रित मात्रा में) जड़ों में डालें।\n• खेत में पर्याप्त नमी बनाए रखें ताकि पौधे पोटेशियम आसानी से सोख सकें।"
        },
        "Punjabi (ਪੰਜਾਬੀ)": {
            "title": "ਪੋਟਾਸ਼ੀਅਮ (K) ਦੀ ਘਾਟ",
            "category": "ਖੁਰਾਕੀ ਤੱਤ ਦੀ ਘਾਟ (ਪੱਤਿਆਂ ਦੇ ਕਿਨਾਰਿਆਂ ਦਾ ਸੜਨਾ)",
            "region": "ਰੇਤਲੀਆਂ ਅਤੇ ਬਾਰਿਸ਼ ਵਾਲੀਆਂ ਜ਼ਮੀਨਾਂ ਵਿੱਚ ਆਮ।",
            "conditions": "ਪੱਤਿਆਂ ਦੇ ਕਿਨਾਰੇ ਭੂਰੇ ਹੋ ਕੇ ਸੜੇ ਹੋਏ ਦਿਸਦੇ ਹਨ।",
            "remedy": "• ਪੋਟਾਸ਼ ਖਾਦ ਦੀ ਸਹੀ ਮਾਤਰਾ ਵਿੱਚ ਵਰਤੋਂ ਕਰੋ।\n• ਖੇਤ ਵਿੱਚ ਸਹੀ ਨਮੀ ਬਣਾ ਕੇ ਰੱਖੋ।\n• ਮਿੱਟੀ ਦੀ ਸਮੇਂ ਸਿਰ ਜਾਂਚ ਕਰਵਾਓ।"
        }
    },
    "Iron_Deficiency": {
        "English": {
            "title": "Iron (Fe) Deficiency",
            "category": "Immobile Micronutrient Shortage (Interveinal Chlorosis)",
            "region": "Common in high pH alkaline or calcareous soils (pH > 7.5).",
            "conditions": "Young upper leaves turn pale yellow while main veins remain distinctly green.",
            "remedy": "• Spray Chelated Iron (Fe-EDTA or Fe-EDDHA) directly onto young leaves.\n• Add elemental sulfur to lower excessive soil alkalinity.\n• Improve soil drainage and reduce over-watering to allow root oxygenation."
        },
        "Hindi (हिंदी)": {
            "title": "आयरन (लोहा - Fe) की कमी",
            "category": "सूक्ष्म पोषक तत्व की कमी (नसों के बीच पीलापन)",
            "region": "अधिक पी.एच (pH > 7.5) वाली क्षारीय या चूनेदार मिट्टी में आम।",
            "conditions": "नई ऊपरी पत्तियां पीली हो जाती हैं जबकि पत्ती की नसें हरी बनी रहती हैं।",
            "remedy": "• चिलेटेड आयरन (Fe-EDTA) का पत्तियों पर फोलियर छिड़काव करें।\n• मिट्टी का क्षारीयपन कम करने के लिए जिप्सम या सल्फर का उपयोग करें।\n• खेतों में जलजमाव रोकें ताकि जड़ों को पर्याप्त ऑक्सीजन मिल सके।"
        },
        "Punjabi (ਪੰਜਾਬੀ)": {
            "title": "ਆਇਰਨ (Fe) ਦੀ ਘਾਟ",
            "category": "ਸੂਖਮ ਖੁਰਾਕੀ ਤੱਤ ਦੀ ਘਾਟ",
            "region": "ਖਾਰੀ ਮਿੱਟੀ (pH > 7.5) ਵਿੱਚ ਆਮ।",
            "conditions": "ਨਵੇਂ ਉੱਪਰਲੇ ਪੱਤੇ ਪੀਲੇ ਪੈ ਜਾਂਦੇ ਹਨ ਜਦੋਂ ਕਿ ਨਾੜੀਆਂ ਹਰੀਆਂ ਰਹਿੰਦੀਆਂ ਹਨ।",
            "remedy": "• ਚਿਲੇਟਡ ਆਇਰਨ ਦਾ ਪੱਤਿਆਂ 'ਤੇ ਛਿੜਕਾਅ ਕਰੋ।\n• ਮਿੱਟੀ ਵਿੱਚ ਪਾਣੀ ਦੇ ਨਿਕਾਸ ਦਾ ਸਹੀ ਪ੍ਰਬੰਧ ਕਰੋ।\n• ਜ਼ਮੀਨ ਦੀ ਸੁਧਾਰ ਲਈ ਖੇਤੀ ਮਾਹਿਰਾਂ ਦੀ ਸਲਾਹ ਲਵੋ।"
        }
    }
}


@st.cache_resource
def load_interpreter():
    interpreter = tf.lite.Interpreter(model_path="model.tflite")
    interpreter.allocate_tensors()
    return interpreter


def generate_pdf_report(res, lang):
    info = res["info"]
    confidence = res["confidence"]
    pil_image = res["image"]
    txt = UI_TEXT[lang]

    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    primary_color = colors.HexColor("#0B192C")
    accent_color = colors.HexColor("#00875A")
    dark_neutral = colors.HexColor("#1E293B")

    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=20,
        textColor=primary_color, spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=10,
        textColor=colors.HexColor("#64748B"), spaceAfter=15
    )
    section_heading = ParagraphStyle(
        'SectionHeading', parent=styles['Heading2'],
        fontName='Helvetica-Bold', fontSize=12,
        textColor=accent_color, spaceBefore=10, spaceAfter=4
    )
    body_style = ParagraphStyle(
        'BodyTextCustom', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10, leading=14, textColor=dark_neutral
    )

    elements = []
    elements.append(Paragraph("Cellular Vision — Agricultural Report", title_style))
    elements.append(Paragraph(txt["subtitle"], subtitle_style))
    elements.append(Spacer(1, 5))

    # Process Image for ReportLab
    img_byte_arr = io.BytesIO()
    pil_image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    rl_img = RLImage(img_byte_arr, width=150, height=150)

    summary_data = [
        [Paragraph(f"<b>{txt['condition']}:</b>", body_style), Paragraph(info['title'], body_style)],
        [Paragraph(f"<b>{txt['confidence']}:</b>", body_style), Paragraph(f"{confidence:.1f}%", body_style)],
        [Paragraph(f"<b>{txt['category']}:</b>", body_style), Paragraph(info['category'], body_style)],
    ]
    summary_table = Table(summary_data, colWidths=[110, 220])
    summary_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))

    layout_table = Table([[rl_img, summary_table]], colWidths=[170, 340])
    layout_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (0,0), 'CENTER'),
    ]))
    elements.append(layout_table)
    elements.append(Spacer(1, 15))

    sections = [
        (txt["region"], info["region"]),
        (txt["symptoms"], info["conditions"]),
        (txt["remedy"], info["remedy"].replace("\n", "<br/>"))
    ]

    for heading, text in sections:
        elements.append(Paragraph(heading, section_heading))
        elements.append(Paragraph(text, body_style))
        elements.append(Spacer(1, 8))

    doc.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()


# ==================== SCREEN 1: UPLOAD PAGE ====================
if st.session_state.page == "upload":
    
    # Executive App Title Bar
    st.markdown("""
    <div class="app-header">
        <div class="brand-title">Cellular Vision</div>
        <div class="brand-subtitle">AI Agricultural Diagnostics & Crop Disease Detection System</div>
    </div>
    """, unsafe_allow_html=True)

    # STEP 1: Mandatory Language Selection BEFORE photo taking
    with st.container(border=True):
        st.subheader("🌐 Step 1: Choose Language / भाषा चुनें")
        selected_lang = st.selectbox(
            label="Select Language",
            options=["Hindi (हिंदी)", "Punjabi (ਪੰਜਾਬੀ)", "English"],
            index=["Hindi (हिंदी)", "Punjabi (ਪੰਜਾਬੀ)", "English"].index(st.session_state.selected_lang),
            label_visibility="collapsed"
        )
        st.session_state.selected_lang = selected_lang

    txt = UI_TEXT[st.session_state.selected_lang]

    # STEP 2: Camera Capture or File Upload
    with st.container(border=True):
        st.subheader(f"📷 Step 2: {txt['camera_input']}")
        
        try:
            interpreter = load_interpreter()
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()

            with open("labels.txt", "r") as f:
                labels = [line.strip().split(' ', 1)[-1].strip() for line in f.readlines()]

            img_file = st.camera_input(txt['camera_input'], label_visibility="collapsed")
            
            if not img_file:
                st.write("---")
                img_file = st.file_uploader(txt['file_input'], type=["jpg", "png", "jpeg"])

            if img_file is not None:
                image = Image.open(img_file).convert('RGB')
                st.image(image, caption=txt['sample_loaded'], use_container_width=True)

                if st.button(txt['analyze_btn'], use_container_width=True, type="primary"):
                    # TFLite Inference Execution
                    size = (224, 224)
                    image_resample = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
                    img_array = np.asarray(image_resample).astype(np.float32) / 255.0
                    img_array = np.expand_dims(img_array, axis=0)

                    interpreter.set_tensor(input_details[0]['index'], img_array)
                    interpreter.invoke()
                    output_data = interpreter.get_tensor(output_details[0]['index'])

                    predicted_index = np.argmax(output_data[0])
                    raw_label = labels[predicted_index]
                    confidence = output_data[0][predicted_index] * 100

                    # Retrieve localized database profile
                    lang_db = PLANT_DATABASE.get(raw_label, PLANT_DATABASE["Diseased"])
                    info = lang_db.get(st.session_state.selected_lang, lang_db["English"])

                    st.session_state.analysis_result = {
                        "info": info,
                        "confidence": confidence,
                        "raw_label": raw_label,
                        "image": image
                    }
                    st.session_state.page = "results"
                    st.rerun()

        except Exception as e:
            st.error(f"System Error: {e}")
            st.info("Ensure 'model.tflite' and 'labels.txt' are present in your root directory.")


# ==================== SCREEN 2: RESULTS PAGE ====================
elif st.session_state.page == "results":
    res = st.session_state.analysis_result
    info = res["info"]
    confidence = res["confidence"]
    raw_label = res["raw_label"]
    txt = UI_TEXT[st.session_state.selected_lang]

    # Executive Navigation Header
    col_nav, col_title = st.columns([1, 3])
    with col_nav:
        if st.button(txt['back_btn']):
            st.session_state.page = "upload"
            st.session_state.analysis_result = None
            st.rerun()

    with col_title:
        st.markdown(f"<h3 style='margin:0; padding:0;'>🔬 {txt['report_header']}</h3>", unsafe_allow_html=True)

    st.markdown("---")

    # Status Banner
    if "Health" in raw_label:
        st.success(f"### ✔️ {info['title']}\n**{txt['confidence']}:** {confidence:.1f}%")
    elif "Diseased" in raw_label:
        st.error(f"### ⚠️ {info['title']}\n**{txt['confidence']}:** {confidence:.1f}%")
    else:
        st.warning(f"### 📊 {info['title']}\n**{txt['confidence']}:** {confidence:.1f}%")

    # Detailed Professional Card Layout
    with st.container(border=True):
        st.markdown(f"#### 🏷️ {txt['category']}")
        st.info(info["category"])

        st.markdown(f"#### 📍 {txt['region']}")
        st.write(info["region"])

        st.markdown(f"#### 🌤️ {txt['symptoms']}")
        st.write(info["conditions"])

        st.markdown(f"#### 💊 {txt['remedy']}")
        st.success(info["remedy"])

    st.markdown("---")

    # Download PDF Report Option
    pdf_bytes = generate_pdf_report(res, st.session_state.selected_lang)
    st.download_button(
        label=txt['download_pdf'],
        data=pdf_bytes,
        file_name="cellular_vision_crop_report.pdf",
        mime="application/pdf",
        use_container_width=True
    )
