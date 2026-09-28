import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np

# Page configuration
st.set_page_config(page_title="Cellular Vision", page_icon="🔬", layout="centered")

# Custom CSS for Leaf Styling & Background Doodles
st.markdown("""
<style>
    /* Main Background Pattern with Botanical Motifs */
    .stApp {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        color: #e2e8f0;
    }
    
    /* Header Styling */
    .title-text {
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(120deg, #a8ff78, #78ffd6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    
    .subtitle-text {
        text-align: center;
        color: #cbd5e1;
        font-size: 1.05rem;
        margin-bottom: 2rem;
    }

    /* Result Container with Leaf Doodle Background Pattern */
    .result-card {
        position: relative;
        background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 20px;
        padding: 28px;
        margin-top: 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        
        /* Subtle Leaf Doodle SVG Background Overlay */
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 100 100' opacity='0.08'%3E%3Cpath fill='%23a8ff78' d='M50 10 C30 30 10 60 50 90 C90 60 70 30 50 10 Z M50 20 L50 80 M50 40 L35 30 M50 55 L65 45 M50 70 L35 60' stroke='%23a8ff78' stroke-width='2' fill-none'/%3E%3C/svg%3E");
        background-repeat: repeat;
    }

    /* Info Field Styling */
    .info-header {
        color: #a8ff78;
        font-size: 1.25rem;
        font-weight: 700;
        margin-top: 10px;
        margin-bottom: 5px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .info-body {
        color: #f1f5f9;
        font-size: 1.02rem;
        line-height: 1.6;
        margin-bottom: 15px;
    }

    /* Status Badges */
    .status-badge-healthy {
        background: linear-gradient(135deg, #11998e, #38ef7d);
        color: #052e16;
        padding: 12px 20px;
        border-radius: 12px;
        font-weight: 800;
        font-size: 1.15rem;
        text-align: center;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(56, 239, 125, 0.3);
    }

    .status-badge-diseased {
        background: linear-gradient(135deg, #ff416c, #ff4b2b);
        color: #ffffff;
        padding: 12px 20px;
        border-radius: 12px;
        font-weight: 800;
        font-size: 1.15rem;
        text-align: center;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(255, 65, 108, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Custom Header
st.markdown('<div class="title-text">🍃 Cellular Vision</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">AI Plant Diagnostics & Botanical Intelligence</div>', unsafe_allow_html=True)

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
            "plant_name": "Apple (*Malus domestica*)",
            "region": "Central Asia (Tian Shan Mountains), cultivated globally in temperate zones.",
            "conditions": "Full sun, well-drained loamy soil, pH 6.0–7.0, cold chilling hours (700–1000 hrs < 7°C).",
            "status": "Diseased: Apple Scab (*Venturia inaequalis*)",
            "remedy": "Apply sulfur or copper-based fungicide spray. Clear fallen autumn leaves to prevent fungal spore overwintering."
        },
        "Apple___Black_rot": {
            "plant_name": "Apple (*Malus domestica*)",
            "region": "Central Asia, grown widely across Europe, North America, and Asia.",
            "conditions": "Moderate to cool climates, full sun exposure, fertile, moisture-retentive soil.",
            "status": "Diseased: Black Rot (*Botryosphaeria obtusa*)",
            "remedy": "Prune out dead or infected branches during dormant season. Remove mummified fruit from trees."
        },
        "Apple___healthy": {
            "plant_name": "Apple (*Malus domestica*)",
            "region": "Central Asia, widely cultivated across temperate regions.",
            "conditions": "Full sun, deep fertile soil, consistent moisture with good drainage.",
            "status": "Healthy Sample",
            "remedy": "Plant is healthy. Maintain regular watering and seasonal pruning schedule."
        },
        "Corn_(maize)___Common_rust_": {
            "plant_name": "Corn / Maize (*Zea mays*)",
            "region": "Mesoamerica (Southern Mexico), grown in tropical, subtropical, and temperate agricultural zones worldwide.",
            "conditions": "Full sunlight (8+ hrs/day), warm soil (18°C–32°C), high nitrogen requirement, moderate rainfall.",
            "status": "Diseased: Common Rust (*Puccinia sorghi*)",
            "remedy": "Plant resistant hybrids. Apply systemic fungicides if rust appears before tassels emerge in moist conditions."
        },
        "Corn_(maize)___healthy": {
            "plant_name": "Corn / Maize (*Zea mays*)",
            "region": "Mesoamerica (Southern Mexico), now grown globally in agricultural belts.",
            "conditions": "Warm temperatures (20°C–30°C), rich organic soil, consistent moisture during pollination.",
            "status": "Healthy Sample",
            "remedy": "Crop is healthy. Ensure adequate nitrogen fertilization during growth spikes."
        },
        "Potato___Early_blight": {
            "plant_name": "Potato (*Solanum tuberosum*)",
            "region": "South American Andes (Peru & Bolivia), cultivated in cool-temperate regions globally.",
            "conditions": "Cool climates (15°C–20°C), loose acidic soil (pH 5.0–6.0), moderate watering.",
            "status": "Diseased: Early Blight (*Alternaria solani*)",
            "remedy": "Spray mancozeb or chlorothalonil fungicide. Maintain proper plant spacing to increase airflow."
        },
        "Potato___Late_blight": {
            "plant_name": "Potato (*Solanum tuberosum*)",
            "region": "South American Andes, now cultivated across global temperate zones.",
            "conditions": "Cool temperatures, high humidity (>90%), moist well-drained soil.",
            "status": "Diseased: Late Blight (*Phytophthora infestans*)",
            "remedy": "Apply copper oxide or systemic fungicides. Immediately remove and destroy affected foliage."
        },
        "Potato___healthy": {
            "plant_name": "Potato (*Solanum tuberosum*)",
            "region": "South American Andes, grown widely in temperate regions.",
            "conditions": "Cool weather, light sandy-loam soil, moderate moisture without waterlogging.",
            "status": "Healthy Sample",
            "remedy": "Plant is healthy. Hill soil around stems to protect developing tubers."
        },
        "Tomato___Bacterial_spot": {
            "plant_name": "Tomato (*Solanum lycopersicum*)",
            "region": "Western South America (Andean region), cultivated globally in warm climates.",
            "conditions": "Full sun, warm temperatures (21°C–29°C), rich sandy-loam soil (pH 6.2–6.8).",
            "status": "Diseased: Bacterial Spot (*Xanthomonas*)",
            "remedy": "Apply copper-based sprays combined with mancozeb. Avoid overhead watering to reduce foliage moisture."
        },
        "Tomato___healthy": {
            "plant_name": "Tomato (*Solanum lycopersicum*)",
            "region": "Western South America, grown globally in home gardens and commercial farms.",
            "conditions": "Warm sunny weather (6–8 hrs sun daily), moist soil, calcium-rich fertilizer.",
            "status": "Healthy Sample",
            "remedy": "Plant is in good health. Keep soil evenly moist to prevent blossom end rot."
        }
    }

    img_file = st.camera_input("📷 Take a photo using camera") 
    if not img_file:
        img_file = st.file_uploader("📁 Or upload a leaf image file...", type=["jpg", "png", "jpeg"])

    if img_file is not None:
        image = Image.open(img_file).convert('RGB')
        st.image(image, caption='Captured Sample', use_container_width=True)
        
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

        info = PLANT_DATABASE.get(raw_label, {
            "plant_name": raw_label.split("___")[0].replace("_", " "),
            "region": "Subtropical & Temperate Agricultural Zones.",
            "conditions": "Full sun exposure, well-draining soil, moderate watering.",
            "status": raw_label.replace("_", " "),
            "remedy": "Inspect plant for signs of stress, maintain moisture levels, and balance soil nutrients."
        })

        is_healthy = "healthy" in raw_label.lower()
        badge_class = "status-badge-healthy" if is_healthy else "status-badge-diseased"

        # Glassmorphism Result Card with Doodle Background
        st.markdown(f"""
        <div class="result-card">
            <div class="{badge_class}">
                {info['status']} ({confidence:.1f}% Confidence)
            </div>
            
            <div class="info-header">🌱 Identified Plant Species</div>
            <div class="info-body">{info['plant_name']}</div>
            
            <div class="info-header">📍 Native / Primary Region</div>
            <div class="info-body">{info['region']}</div>
            
            <div class="info-header">☀️ Ideal Growing Conditions</div>
            <div class="info-body">{info['conditions']}</div>
            
            <div class="info-header">💊 Recommended Action / Remedy</div>
            <div class="info-body">{info['remedy']}</div>
        </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"App initialization error: {e}")
    st.info("Ensure 'model.tflite' and 'labels.txt' are present in your GitHub repository root.")
