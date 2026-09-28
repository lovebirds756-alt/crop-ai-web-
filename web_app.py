import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np

# Page configuration
st.set_page_config(page_title="Cellular Vision", page_icon="🍃", layout="centered")

# Custom CSS for Animations, Cute Styling & Floating Leaves
st.markdown("""
<style>
    /* Cute Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #0d1f2d 0%, #1d3557 50%, #112a46 100%);
        color: #f1faee;
    }

    /* Keyframe Animations */
    @keyframes floatLeaf {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-12px) rotate(8deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }

    @keyframes popIn {
        0% { transform: scale(0.85); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }

    @keyframes pulseGlow {
        0% { box-shadow: 0 0 15px rgba(168, 255, 120, 0.2); }
        50% { box-shadow: 0 0 30px rgba(168, 255, 120, 0.5); }
        100% { box-shadow: 0 0 15px rgba(168, 255, 120, 0.2); }
    }

    /* Floating Bouncing Leaf Logo */
    .cute-logo {
        font-size: 3.8rem;
        text-align: center;
        display: inline-block;
        width: 100%;
        animation: floatLeaf 3s ease-in-out infinite;
        margin-top: 10px;
    }

    /* Header Styling */
    .title-text {
        font-family: 'Comic Sans MS', 'Chalkboard SE', 'Fredoka', sans-serif;
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
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 1.8rem;
    }

    /* Result Container with Animated Pop-in & Leaf Pattern */
    .result-card {
        animation: popIn 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards, pulseGlow 4s infinite;
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 2px solid rgba(168, 255, 120, 0.3);
        border-radius: 25px;
        padding: 30px;
        margin-top: 20px;
        
        /* Cute Repeating Leaf Doodle Pattern Background */
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='80' viewBox='0 0 100 100' opacity='0.12'%3E%3Cpath fill='%23a8ff78' d='M50 15 C30 35 15 60 50 85 C85 60 70 35 50 15 Z M50 25 L50 75 M50 45 L38 35 M50 58 L62 48' stroke='%23a8ff78' stroke-width='3' stroke-linecap='round' fill='none'/%3E%3C/svg%3E");
        background-repeat: repeat;
    }

    /* Cute Info Headers & Sections */
    .info-header {
        color: #a8ff78;
        font-family: 'Fredoka', sans-serif;
        font-size: 1.25rem;
        font-weight: 700;
        margin-top: 14px;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .info-body {
        color: #f1faee;
        font-size: 1.05rem;
        background: rgba(0, 0, 0, 0.25);
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

# Cute Floating Title Header
st.markdown('<div class="cute-logo">🍃🌱🔬</div>', unsafe_allow_html=True)
st.markdown('<div class="title-text">Cellular Vision</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">✨ AI Botanical Explorer & Plant Care Companion ✨</div>', unsafe_allow_html=True)

@st.cache_resource
def load_interpreter():
    interpreter = tf.lite.Interpreter(model_path="model.tflite")
    interpreter.allocate_tensors()
    return interpreter

try:
    interpreter = load_interpreter()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    with open("labels.txt", "r") as f:
        labels = [line.strip().split(' ', 1)[-1] for line in f.readlines()]

    PLANT_DATABASE = {
        "Apple___Apple_scab": {
            "plant_name": "Apple Tree (*Malus domestica*) 🍎",
            "region": "Central Asian Mountains (Tian Shan), cultivated worldwide in cool zones.",
            "conditions": "Full sunshine (6+ hrs/day), rich soil with good drainage, temperate climate.",
            "status": "Infected with Apple Scab 🍂",
            "remedy": "Spray organic copper or sulfur fungicide. Clear fallen autumn leaves to keep roots clean!"
        },
        "Apple___Black_rot": {
            "plant_name": "Apple Tree (*Malus domestica*) 🍎",
            "region": "Central Asia, grown across Europe, Asia & North America.",
            "conditions": "Cool to moderate climates, organic rich loamy soil.",
            "status": "Infected with Black Rot 🥀",
            "remedy": "Prune away infected twigs in winter and remove old dried fruit from branches."
        },
        "Apple___healthy": {
            "plant_name": "Apple Tree (*Malus domestica*) 🍎",
            "region": "Central Asian Mountains, cultivated globally.",
            "conditions": "Full sun exposure, deep moist soil, seasonal winter cooling.",
            "status": "Super Healthy Leaf! ✨",
            "remedy": "Your apple plant is thriving! Keep watering regularly and give it lots of sunshine."
        },
        "Corn_(maize)___Common_rust_": {
            "plant_name": "Corn / Maize (*Zea mays*) 🌽",
            "region": "Mesoamerica (Southern Mexico), grown globally in sunny farm fields.",
            "conditions": "Warm weather (20°C–32°C), lots of sunlight, rich nitrogen soil.",
            "status": "Infected with Common Rust 🌽🍂",
            "remedy": "Ensure proper field spacing for air circulation. Spray sulfur-based organic treatment."
        },
        "Corn_(maize)___healthy": {
            "plant_name": "Corn / Maize (*Zea mays*) 🌽",
            "region": "Mesoamerica (Mexico), grown in warm belts worldwide.",
            "conditions": "Warm temperature, high humidity, full direct sunlight.",
            "status": "Super Healthy Leaf! ✨",
            "remedy": "Looking great! Keep providing balanced nitrogen nutrients during active growth."
        },
        "Potato___Early_blight": {
            "plant_name": "Potato Plant (*Solanum tuberosum*) 🥔",
            "region": "South American Andes Mountains (Peru & Bolivia).",
            "conditions": "Cool temperate climates, loose sandy-loam soil (pH 5.0–6.0).",
            "status": "Infected with Early Blight 🥔🍂",
            "remedy": "Spray neem oil or bio-fungicide. Avoid over-watering the leaves directly."
        },
        "Potato___Late_blight": {
            "plant_name": "Potato Plant (*Solanum tuberosum*) 🥔",
            "region": "South American Andes, grown in cool regions around the globe.",
            "conditions": "Cool moist weather, high humidity, light organic soil.",
            "status": "Infected with Late Blight 🚨",
            "remedy": "Remove affected leaves immediately to protect neighboring plants. Keep soil dry on top."
        },
        "Potato___healthy": {
            "plant_name": "Potato Plant (*Solanum tuberosum*) 🥔",
            "region": "South American Andes Mountains.",
            "conditions": "Cool weather, well-draining soil, moderate watering.",
            "status": "Super Healthy Leaf! ✨",
            "remedy": "Healthy plant! Pile extra soil around the lower stem to help bigger potatoes grow."
        },
        "Tomato___Bacterial_spot": {
            "plant_name": "Tomato Plant (*Solanum lycopersicum*) 🍅",
            "region": "Western South America (Andean region).",
            "conditions": "Warm sunshine, rich sandy soil, gentle watering at root level.",
            "status": "Infected with Bacterial Spot 🍅🦠",
            "remedy": "Apply organic copper spray. Water only at the base/roots to keep leaves completely dry."
        },
        "Tomato___healthy": {
            "plant_name": "Tomato Plant (*Solanum lycopersicum*) 🍅",
            "region": "South American Andes, cultivated worldwide.",
            "conditions": "6-8 hours of direct sunlight, warm temperature, calcium-rich soil.",
            "status": "Super Healthy Leaf! ✨",
            "remedy": "Plant is super happy! Maintain steady watering to encourage juicy sweet tomatoes."
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

        # Smart fallback parsing so raw text never displays as "Health"
        clean_parts = raw_label.replace("___", " - ").replace("_", " ").split(" - ")
        parsed_plant = clean_parts[0] if len(clean_parts) > 0 else "Unknown Crop"
        parsed_status = clean_parts[1] if len(clean_parts) > 1 else "Analyzed"

        info = PLANT_DATABASE.get(raw_label, {
            "plant_name": f"{parsed_plant} 🌿",
            "region": "Subtropical & Temperate Agricultural Zones.",
            "conditions": "Full sun exposure, well-draining soil, moderate watering.",
            "status": parsed_status,
            "remedy": "Inspect plant for signs of stress, maintain moisture levels, and balance soil nutrients."
        })

        is_healthy = "healthy" in raw_label.lower()
        badge_class = "status-badge-healthy" if is_healthy else "status-badge-diseased"

        # Cute Glassmorphism Result Card with Animated Pop-in
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
