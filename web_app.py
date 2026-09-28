import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import re

# Page configuration
st.set_page_config(page_title="Cellular Vision", page_icon="🍃", layout="centered")

# Custom CSS for Cute Animations, Styling & Floating Elements
st.markdown("""
<style>
    /* Cute Dark Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #0d1f2d 0%, #1d3557 50%, #112a46 100%);
        color: #f1faee;
    }

    /* Keyframe Animations */
    @keyframes floatLeaf {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-10px) rotate(6deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }

    @keyframes popIn {
        0% { transform: scale(0.88); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }

    @keyframes pulseGlow {
        0% { box-shadow: 0 0 15px rgba(168, 255, 120, 0.2); }
        50% { box-shadow: 0 0 28px rgba(168, 255, 120, 0.45); }
        100% { box-shadow: 0 0 15px rgba(168, 255, 120, 0.2); }
    }

    /* Floating Bouncing Leaf Header Logo */
    .cute-logo {
        font-size: 3.5rem;
        text-align: center;
        display: block;
        animation: floatLeaf 3s ease-in-out infinite;
        margin-top: 10px;
    }

    /* Title Styling */
    .title-text {
        font-family: 'Comic Sans MS', 'Fredoka', sans-serif;
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(120deg, #a8ff78, #78ffd6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.2rem;
    }

    .subtitle-text {
        text-align: center;
        color: #a8dadc;
        font-size: 1.05rem;
        font-weight: 500;
        margin-bottom: 1.8rem;
    }

    /* Result Container with Animated Pop-in & Leaf Pattern */
    .result-card {
        animation: popIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards, pulseGlow 4s infinite;
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 2px solid rgba(168, 255, 120, 0.35);
        border-radius: 25px;
        padding: 28px;
        margin-top: 20px;
        
        /* Cute Repeating Leaf Doodle Pattern Background */
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='80' viewBox='0 0 100 100' opacity='0.12'%3E%3Cpath fill='%23a8ff78' d='M50 15 C30 35 15 60 50 85 C85 60 70 35 50 15 Z M50 25 L50 75 M50 45 L38 35 M50 58 L62 48' stroke='%23a8ff78' stroke-width='3' stroke-linecap='round' fill='none'/%3E%3C/svg%3E");
        background-repeat: repeat;
    }

    /* Info Headers & Rounded Body Text */
    .info-header {
        color: #a8ff78;
        font-size: 1.2rem;
        font-weight: 700;
        margin-top: 14px;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .info-body {
        color: #f1faee;
        font-size: 1.02rem;
        background: rgba(0, 0, 0, 0.28);
        padding: 10px 16px;
        border-radius: 14px;
        margin-bottom: 12px;
        border-left: 4px solid #a8ff78;
    }

    /* Cute Status Badges */
    .status-badge-healthy {
        background: linear-gradient(135deg, #2a9d8f, #e9c46a);
        color: #03045e;
        padding: 14px 22px;
        border-radius: 20px;
        font-weight: 800;
        font-size: 1.2rem;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 6px 20px rgba(42, 157, 143, 0.4);
    }

    .status-badge-diseased {
        background: linear-gradient(135deg, #e63946, #f4a261);
        color: #ffffff;
        padding: 14px 22px;
        border-radius: 20px;
        font-weight: 800;
        font-size: 1.2rem;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 6px 20px rgba(230, 57, 70, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown('<div class="cute-logo">🍃🌱🔬</div>', unsafe_allow_html=True)
st.markdown('<div class="title-text">Cellular Vision</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">✨ AI Botanical Explorer & Plant Care Companion ✨</div>', unsafe_allow_html=True)

@st.cache_resource
def load_interpreter():
    interpreter = tf.lite.Interpreter(model_path="model.tflite")
    interpreter.allocate_tensors()
    return interpreter

def parse_label(raw_label):
    """
    Intelligently extracts (plant_name, disease_status) regardless of how raw_label is formatted.
    Handles 'Apple___healthy', 'Apple___Black_rot', 'Healthy_Tomato', '0 Rice___Bacterial_blight', etc.
    """
    # Remove leading numbers/spaces if present (e.g. "0 Apple___healthy")
    cleaned = re.sub(r'^\d+\s*', '', raw_label).strip()

    # Split by common delimiters like triple/double underscores or dashes
    if "___" in cleaned:
        parts = cleaned.split("___")
    elif "__" in cleaned:
        parts = cleaned.split("__")
    elif " - " in cleaned:
        parts = cleaned.split(" - ")
    else:
        parts = [cleaned]

    if len(parts) >= 2:
        plant = parts[0].replace("_", " ").title()
        status = parts[1].replace("_", " ").title()
    else:
        # Single-word label or reversed label like "Healthy_Tomato"
        val = parts[0].replace("_", " ")
        if "healthy" in val.lower():
            # Extract plant name if label is "Healthy Tomato" or "Tomato Healthy"
            plant_cleaned = re.sub(r'(?i)\bhealthy\b', '', val).strip()
            plant = plant_cleaned.title() if plant_cleaned else "Crop Sample"
            status = "Healthy Leaf"
        else:
            plant = val.title()
            status = "Condition Detected"

    if "healthy" in status.lower():
        status = "Super Healthy Leaf! ✨"

    return plant, status

try:
    interpreter = load_interpreter()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    with open("labels.txt", "r") as f:
        labels = [line.strip().split(' ', 1)[-1] for line in f.readlines()]

    # Detailed Botanical & Care Info Dictionary
    PLANT_DATABASE = {
        "Apple___Apple_scab": {
            "plant_name": "Apple Tree (*Malus domestica*) 🍎",
            "region": "Central Asian Mountains (Tian Shan), grown in cool temperate zones globally.",
            "conditions": "Full sunshine (6+ hrs/day), rich loamy soil, cold winter chilling.",
            "status": "Infected with Apple Scab 🍂",
            "remedy": "Apply organic copper or sulfur fungicide spray. Rake up fallen leaves to keep soil clean."
        },
        "Apple___Black_rot": {
            "plant_name": "Apple Tree (*Malus domestica*) 🍎",
            "region": "Central Asia, cultivated across Europe, Asia, and North America.",
            "conditions": "Cool to moderate climate, fertile well-drained soil.",
            "status": "Infected with Black Rot 🥀",
            "remedy": "Prune away dead or infected branches during dormant season and destroy mummified fruits."
        },
        "Apple___healthy": {
            "plant_name": "Apple Tree (*Malus domestica*) 🍎",
            "region": "Central Asian Mountains, cultivated globally.",
            "conditions": "Full sunlight, deep fertile soil, consistent watering.",
            "status": "Super Healthy Leaf! ✨",
            "remedy": "Your apple tree is thriving! Maintain regular watering and annual winter pruning."
        },
        "Corn_(maize)___Common_rust_": {
            "plant_name": "Corn / Maize (*Zea mays*) 🌽",
            "region": "Mesoamerica (Southern Mexico), grown in sunny warm climates worldwide.",
            "conditions": "Warm soil (20°C–32°C), high sunlight, rich nitrogen-fertilized ground.",
            "status": "Infected with Common Rust 🌽🍂",
            "remedy": "Ensure proper row spacing for airflow. Apply neem oil or sulfur-based spray if severe."
        },
        "Corn_(maize)___healthy": {
            "plant_name": "Corn / Maize (*Zea mays*) 🌽",
            "region": "Mesoamerica (Mexico), grown in agricultural belts worldwide.",
            "conditions": "Warm weather, full sun, deep organic soil with steady moisture.",
            "status": "Super Healthy Leaf! ✨",
            "remedy": "Looking great! Keep providing balanced nitrogen nutrients during key growth phases."
        },
        "Potato___Early_blight": {
            "plant_name": "Potato Plant (*Solanum tuberosum*) 🥔",
            "region": "South American Andes (Peru & Bolivia).",
            "conditions": "Cool climates (15°C–20°C), loose acidic soil (pH 5.0–6.0).",
            "status": "Infected with Early Blight 🥔🍂",
            "remedy": "Spray bio-fungicide or copper spray. Avoid splashing water onto foliage during irrigation."
        },
        "Potato___Late_blight": {
            "plant_name": "Potato Plant (*Solanum tuberosum*) 🥔",
            "region": "South American Andes, cultivated in cool moist zones globally.",
            "conditions": "Cool weather, high humidity (>90%), light well-drained soil.",
            "status": "Infected with Late Blight 🚨",
            "remedy": "Remove infected leaves immediately to stop spreading. Keep soil surface dry."
        },
        "Potato___healthy": {
            "plant_name": "Potato Plant (*Solanum tuberosum*) 🥔",
            "region": "South American Andes Mountains.",
            "conditions": "Cool weather, light sandy-loam soil, moderate moisture.",
            "status": "Super Healthy Leaf! ✨",
            "remedy": "Healthy plant! Pile extra soil around stem bases to protect developing tubers."
        },
        "Tomato___Bacterial_spot": {
            "plant_name": "Tomato Plant (*Solanum lycopersicum*) 🍅",
            "region": "Western South America (Andean region).",
            "conditions": "Full sun, warm temperature (21°C–29°C), rich sandy-loam soil.",
            "status": "Infected with Bacterial Spot 🍅🦠",
            "remedy": "Apply copper-based fungicide spray. Water at root level only to keep leaves dry."
        },
        "Tomato___healthy": {
            "plant_name": "Tomato Plant (*Solanum lycopersicum*) 🍅",
            "region": "South American Andes, grown in home gardens and farms globally.",
            "conditions": "6-8 hours direct sunshine, warm soil, calcium-rich fertilizer.",
            "status": "Super Healthy Leaf! ✨",
            "remedy": "Plant is super happy! Keep soil evenly moist to encourage sweet, healthy tomatoes."
        }
    }

    img_file = st.camera_input("📷 Snap a leaf photo") 
    if not img_file:
        img_file = st.file_uploader("📁 Or pick a leaf picture...", type=["jpg", "png", "jpeg"])

    if img_file is not None:
        image = Image.open(img_file).convert('RGB')
        st.image(image, caption='🔍 Scanning Sample...', use_container_width=True)
        
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

        # Run smart parser on predicted label
        parsed_plant, parsed_status = parse_label(raw_label)

        # Retrieve exact details from PLANT_DATABASE or use parsed fallback
        info = PLANT_DATABASE.get(raw_label, {
            "plant_name": f"{parsed_plant} Plant 🌿",
            "region": "Subtropical & Temperate Agricultural Zones.",
            "conditions": "Full sun exposure, well-draining organic soil, moderate watering.",
            "status": parsed_status,
            "remedy": "Inspect plant for stress signs, maintain consistent soil moisture, and balance organic nutrients."
        })

        is_healthy = "healthy" in raw_label.lower() or "healthy" in parsed_status.lower()
        badge_class = "status-badge-healthy" if is_healthy else "status-badge-diseased"

        # Glassmorphism Animated Result Card
        st.markdown(f"""
        <div class="result-card">
            <div class="{badge_class}">
                {info['status']} ({confidence:.1f}% Match)
            </div>
            
            <div class="info-header">🌱 Identified Plant Species</div>
            <div class="info-body">{info['plant_name']}</div>
            
            <div class="info-header">📍 Native / Primary Origin</div>
            <div class="info-body">{info['region']}</div>
            
            <div class="info-header">☀️ Ideal Growing Conditions</div>
            <div class="info-body">{info['conditions']}</div>
            
            <div class="info-header">💊 Recommended Care & Remedy</div>
            <div class="info-body">{info['remedy']}</div>
        </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"App initialization error: {e}")
    st.info("Ensure 'model.tflite' and 'labels.txt' are present in your GitHub repository root.")
