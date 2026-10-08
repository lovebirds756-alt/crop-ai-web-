import io
import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np

# ReportLab Imports for Comprehensive Agronomic PDF Reports
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Page Configuration - Enterprise Agronomy Diagnostics
st.set_page_config(
    page_title="Cellular Vision | Enterprise Crop Diagnostics",
    page_icon="🔬",
    layout="centered"
)

# Initialize Session State
if "page" not in st.session_state:
    st.session_state.page = "upload"
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "selected_lang" not in st.session_state:
    st.session_state.selected_lang = "Hindi (हिंदी)"

# Strict Industrial / Laboratory UI Design CSS
st.markdown("""
<style>
    /* Dark Industrial Agronomy Theme */
    .stApp {
        background-color: #0F172A;
        color: #E2E8F0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }

    /* Enterprise Header Bar */
    .brand-header {
        border-bottom: 2px solid #334155;
        padding-bottom: 16px;
        margin-bottom: 24px;
    }

    .brand-title {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: #F8FAFC;
        margin: 0;
        text-transform: uppercase;
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


# Multilingual Technical Dictionary
UI_TEXT = {
    "English": {
        "title": "CELLULAR VISION",
        "subtitle": "SCERT Autonomous Crop Pathology & Nutrient Diagnostic Platform",
        "lang_step": "System Operating Language / भाषा का चयन",
        "scan_step": "Foliar Image Acquisition & Sensor Input",
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
        "confidence": "Diagnostic Certainty Index"
    },
    "Hindi (हिंदी)": {
        "title": "सेल्यूलर विज़न (CELLULAR VISION)",
        "subtitle": "एससीईआरटी स्वचालित फसल रोग एवं पोषक तत्व निदान प्रणाली",
        "lang_step": "प्रणाली की भाषा चुनें / System Operating Language",
        "scan_step": "पत्ती का फोटो लें या नमूना दर्ज करें",
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
        "confidence": "निदान सटीकता सूचकांक"
    },
    "Punjabi (ਪੰਜਾਬੀ)": {
        "title": "ਸੈਲੂਲਰ ਵਿਜ਼ਨ (CELLULAR VISION)",
        "subtitle": "ਐਸ.ਸੀ.ਈ.ਆਰ.ਟੀ. ਫਸਲ ਬਿਮਾਰੀ ਅਤੇ ਨਿਦਾਨ ਪ੍ਰਣਾਲੀ",
        "lang_step": "ਸਿਸਟਮ ਦੀ ਭਾਸ਼ਾ ਚੁਣੋ / Select Operating Language",
        "scan_step": "ਪੱਤੇ ਦਾ ਨਮੂਨਾ ਦਰਜ ਕਰੋ",
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
        "confidence": "ਜਾਂਚ ਨਿਰਧਾਰਨ ਦਰ"
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
            "symptoms": "ਪੱਤੇ ਗੂੜ੍ਹੇ ਹਰੇ ਹੋ ਕੇ ਕਿਨਾਰਿਆਂ ਤੋਂ ਜਾਮਣੀ ਜਾਂ ਲਾਲ ਰੰਗ ਦੇ ਹੋ ਜਾਂਦੇ ਹਨ। ਜੜ੍ਹਾਂ ਦਾ ਵਾਧਾ ਰੁਕ ਜਾਂਦਾ ਹੈ।",
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
            "category": "ਪੱਤਿਆਂ ਦੇ ਕਿਨਾਰਿਆਂ ਦਾ ਸੜਨਾ",
            "region": "ਰੇਤਲੀਆਂ ਜ਼ਮੀਨਾਂ ਅਤੇ ਵੱਧ ਯੂਰੀਆ ਵਰਤਣ ਵਾਲੇ ਖੇਤਾਂ ਵਿੱਚ ਆਮ।",
            "symptoms": "ਪੱਤਿਆਂ ਦੇ ਕਿਨਾਰੇ ਭੂਰੇ ਹੋ ਕੇ ਸੜੇ ਹੋਏ (Scorched) ਦਿਸਦੇ ਹਨ। ਤਣਾ ਕਮਜ਼ੋਰ ਹੋ ਜਾਂਦਾ ਹੈ।",
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
            "category": "ਸੂਖਮ ਖੁਰਾਕੀ ਤੱਤ ਦੀ ਘਾਟ",
            "region": "ਖਾਰੀ ਮਿੱਟੀ (pH > 7.5) ਅਤੇ ਪਾਣੀ ਖੜ੍ਹਨ ਵਾਲੀਆਂ ਜ਼ਮੀਨਾਂ ਵਿੱਚ ਆਮ।",
            "symptoms": "ਨਵੀਆਂ ਉੱਪਰਲੀਆਂ ਪੱਤਿਆਂ ਦੀਆਂ ਨਾੜੀਆਂ ਹਰੀਆਂ ਰਹਿੰਦੀਆਂ ਹਨ ਜਦੋਂ ਕਿ ਬਾਕੀ ਪੱਤਾ ਪੀਲਾ/ਚਿੱਟਾ ਪੈ ਜਾਂਦਾ ਹੈ।",
            "action_plan": "1. ਸਪਰੇਅ: ਚਿਲੇਟਡ ਆਇਰਨ (Fe-EDDHA) 2 ਗ੍ਰਾਮ/ਲੀਟਰ ਦਾ ਛਿੜਕਾਅ ਕਰੋ।\n2. ਮਿੱਟੀ ਸੁਧਾਰ: ਮਿੱਟੀ ਦਾ ਖਾਰਾਪਣ ਘਟਾਉਣ ਲਈ ਸਲਫਰ ਦੀ ਵਰਤੋਂ ਕਰੋ।\n3. ਹਵਾ ਦਾ ਸੰਚਾਰ: ਖੇਤ ਵਿੱਚੋਂ ਵਾਧੂ ਪਾਣੀ ਨਿਕਾਸ ਦਾ ਪ੍ਰਬੰਧ ਕਰੋ।",
            "preventive": "ਮਿੱਟੀ ਦਾ pH ਸੰਤੁਲਿਤ ਰੱਖਣ ਲਈ ਜੈਵਿਕ ਖਾਦਾਂ ਵਰਤੋਂ।"
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
    
    # Official Header
    elements.append(Paragraph("CELLULAR VISION — AGRONOMIC PATHOLOGY REPORT", title_style))
    elements.append(Paragraph(f"SYSTEM EVALUATION REPORT | {txt['subtitle']}", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=1, spaceAfter=10))

    # Leaf Image
    img_byte_arr = io.BytesIO()
    pil_image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    rl_img = RLImage(img_byte_arr, width=140, height=140)

    # Diagnostic Summary Table
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

    # Long Form Diagnostic Sections
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


# ==================== SCREEN 1: UPLOAD & ACQUISITION ====================
if st.session_state.page == "upload":
    
    # Industrial Enterprise Title Bar
    st.markdown("""
    <div class="brand-header">
        <div class="brand-title">CELLULAR VISION</div>
        <div class="brand-subtitle">SCERT Autonomous Crop Pathology & Nutrient Diagnostic System</div>
    </div>
    """, unsafe_allow_html=True)

    # STEP 1: Mandatory Language Selection BEFORE photo taking
    with st.container(border=True):
        st.markdown(f'<div class="section-label">STEP 1: SYSTEM LANGUAGE SELECTION</div>', unsafe_allow_html=True)
        selected_lang = st.selectbox(
            label="Language Selection",
            options=["Hindi (हिंदी)", "Punjabi (ਪੰਜਾਬੀ)", "English"],
            index=["Hindi (हिंदी)", "Punjabi (ਪੰਜਾਬੀ)", "English"].index(st.session_state.selected_lang),
            label_visibility="collapsed"
        )
        st.session_state.selected_lang = selected_lang

    txt = UI_TEXT[st.session_state.selected_lang]

    # STEP 2: Camera Capture or File Upload
    with st.container(border=True):
        st.markdown(f'<div class="section-label">STEP 2: {txt["scan_step"].upper()}</div>', unsafe_allow_html=True)
        
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
                    # TFLite Model Execution
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

                    # Retrieve localized deep agronomic database profile
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


# ==================== SCREEN 2: EXTENDED DIAGNOSTIC REPORT ====================
elif st.session_state.page == "results":
    res = st.session_state.analysis_result
    info = res["info"]
    confidence = res["confidence"]
    raw_label = res["raw_label"]
    txt = UI_TEXT[st.session_state.selected_lang]

    # Executive Navigation
    col_nav, col_title = st.columns([1, 3])
    with col_nav:
        if st.button(txt['back_btn']):
            st.session_state.page = "upload"
            st.session_state.analysis_result = None
            st.rerun()

    with col_title:
        st.markdown(f"<h3 style='margin:0; padding:0; color:#F8FAFC;'>{txt['report_header']}</h3>", unsafe_allow_html=True)

    st.markdown("---")

    # Primary Diagnosis Card
    with st.container(border=True):
        st.markdown(f'<div class="section-label">{txt["condition"].upper()}</div>', unsafe_allow_html=True)
        st.markdown(f"## {info['title']}")
        st.markdown(f"**{txt['confidence']}:** {confidence:.2f}% Certainty Index")

    # Long-Form Detailed Agronomic Sections
    with st.container(border=True):
        st.markdown(f'<div class="section-label">{txt["category"].upper()}</div>', unsafe_allow_html=True)
        st.info(info["category"])

        st.markdown(f'<div class="section-label">{txt["region"].upper()}</div>', unsafe_allow_html=True)
        st.write(info["region"])

        st.markdown(f'<div class="section-label">{txt["symptoms"].upper()}</div>', unsafe_allow_html=True)
        st.write(info["symptoms"])

        st.markdown(f'<div class="section-label">{txt["action_plan"].upper()}</div>', unsafe_allow_html=True)
        st.success(info["action_plan"])

        st.markdown(f'<div class="section-label">{txt["preventive"].upper()}</div>', unsafe_allow_html=True)
        st.warning(info["preventive"])

    st.markdown("---")

    # Download Long PDF Report Option
    pdf_bytes = generate_pdf_report(res, st.session_state.selected_lang)
    st.download_button(
        label=txt['download_pdf'],
        data=pdf_bytes,
        file_name="cellular_vision_agronomic_report.pdf",
        mime="application/pdf",
        use_container_width=True
    )
