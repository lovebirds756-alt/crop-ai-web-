import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np

# Page configuration
st.set_page_config(page_title="Cellular Vision", page_icon="🍃", layout="centered")

# Custom CSS for App Styling & High-Visibility Plant Firework
st.markdown("""
<style>
    /* Gradient App Background */
    .stApp {
        background: linear-gradient(135deg, #0d1f2d 0%, #1d3557 50%, #112a46 100%);
        color: #f1faee;
    }

    /* Keyframe Animations for Header */
    @keyframes floatLeaf {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-10px) rotate(6deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }

    /* Header Logo */
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

    /* Firework Canvas Container */
    .firework-canvas-container {
        width: 100%;
        height: 250px;
        position: relative;
        overflow: hidden;
        margin-bottom: -40px;
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

try:
    interpreter = load_interpreter()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # Load and clean label names
    with open("labels.txt", "r") as f:
        labels = [line.strip().split(' ', 1)[-1].strip() for line in f.readlines()]

    # Database matching your model classes
    PLANT_DATABASE = {
        "Health": {
            "title": "Healthy Crop Sample ✨",
            "category": "Optimal Plant Health",
            "region": "Widespread across temperate, tropical, and subtropical farm zones.",
            "conditions": "Balanced soil nutrients (NPK), pH 6.0–7.0, adequate sunlight (6-8 hrs/day), consistent moisture.",
            "remedy": "Your plant is in optimal health! Maintain regular watering, balanced composting, and seasonal sunlight."
        },
        "Diseased": {
            "title": "Infected / Diseased Sample 🚨",
            "category": "Pathogenic Stress (Fungal or Bacterial)",
            "region": "Common in humid or waterlogged agricultural areas globally.",
            "conditions": "High moisture levels on foliage, poor air circulation, unsterilized soil or tools.",
            "remedy": "Isolate the plant, remove infected leaves immediately, avoid overhead watering, and apply broad-spectrum organic bio-fungicide or copper spray."
        },
        "Nitrogen_Deficiency": {
            "title": "Nitrogen (N) Deficiency 🟡",
            "category": "Macronutrient Deficiency",
            "region": "Frequently found in sandy, eroded, or heavily cropped soils lacking organic matter.",
            "conditions": "Symptom: Pale yellowing (chlorosis) starting on older lower leaves while upper leaves remain pale green.",
            "remedy": "Apply nitrogen-rich fertilizers such as composted manure, blood meal, ammonium sulfate, or organic fish emulsion."
        },
        "Phosphorus_Deficiency": {
            "title": "Phosphorus (P) Deficiency 🟣",
            "category": "Macronutrient Deficiency",
            "region": "Common in cold, wet, overly acidic (pH < 5.5) or alkaline soils.",
            "conditions": "Symptom: Stunted root growth with purplish or dark bronze discoloration on leaf undersides and stems.",
            "remedy": "Add bone meal, rock phosphate, or balanced high-phosphorus fertilizer. Ensure soil pH is between 6.0–7.0 for optimal absorption."
        },
        "Potassium_Deficiency": {
            "title": "Potassium (K) Deficiency 🟠",
            "category": "Macronutrient Deficiency",
            "region": "Prevalent in light sandy soils where potassium leaches out easily during heavy rains.",
            "conditions": "Symptom: Scorched, browned leaf margins (marginal chlorosis/necrosis) with curling leaf tips.",
            "remedy": "Apply muriate of potash, sulphate of potash, or wood ash. Keep soil moisture steady to prevent nutrient lockup."
        },
        "Iron_Deficiency": {
            "title": "Iron (Fe) Deficiency ⚪",
            "category": "Micronutrient Deficiency",
            "region": "Common in high pH (alkalinity > 7.5), overly calcareous, or compacted waterlogged soils.",
            "conditions": "Symptom: Interveinal chlorosis — young top leaves turn pale yellow or ivory while veins stay dark green.",
            "remedy": "Apply chelated iron (Fe-EDTA) as a foliar spray or soil drench. Lower soil pH using sulfur or peat moss."
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

        # Retrieve entry from PLANT_DATABASE
        info = PLANT_DATABASE.get(raw_label, {
            "title": raw_label.replace("_", " "),
            "category": "General Analysis",
            "region": "Subtropical & Temperate Agricultural Zones.",
            "conditions": "Full sun exposure, well-draining organic soil, moderate watering.",
            "remedy": "Inspect plant for stress signs, maintain consistent soil moisture, and balance organic nutrients."
        })

        st.markdown("---")

        # HTML5 Canvas Animation Shooting Plant Emojis UP like Fireworks
        firework_html = """
        <div class="firework-canvas-container">
            <canvas id="emojiCanvas"></canvas>
        </div>
        <script>
            (function() {
                const canvas = document.getElementById('emojiCanvas');
                const ctx = canvas.getContext('2d');
                
                canvas.width = canvas.parentElement.clientWidth;
                canvas.height = 250;
                
                const emojis = ['🍃', '✨', '🌱', '🌾', '🌿'];
                const particles = [];
                
                // Spawn 25 emoji particles with upward firework trajectory
                for (let i = 0; i < 25; i++) {
                    particles.push({
                        x: canvas.width / 2 + (Math.random() * 60 - 30),
                        y: canvas.height - 10,
                        vx: (Math.random() - 0.5) * 8,
                        vy: -(Math.random() * 8 + 8), // High upward velocity
                        size: Math.random() * 16 + 24, // Large visible font size
                        emoji: emojis[Math.floor(Math.random() * emojis.length)],
                        alpha: 1,
                        rotation: Math.random() * Math.PI * 2,
                        vRot: (Math.random() - 0.5) * 0.1
                    });
                }
                
                function animate() {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    
                    let active = false;
                    particles.forEach(p => {
                        if (p.alpha > 0.01) {
                            active = true;
                            p.x += p.vx;
                            p.y += p.vy;
                            p.vy += 0.25; // Simulated gravity pull
                            p.rotation += p.vRot;
                            p.alpha -= 0.012; // Gradual fade out
                            
                            ctx.save();
                            ctx.globalAlpha = Math.max(0, p.alpha);
                            ctx.translate(p.x, p.y);
                            ctx.rotate(p.rotation);
                            ctx.font = `${p.size}px serif`;
                            ctx.textAlign = 'center';
                            ctx.textBaseline = 'middle';
                            ctx.fillText(p.emoji, 0, 0);
                            ctx.restore();
                        }
                    });
                    
                    if (active) {
                        requestAnimationFrame(animate);
                    }
                }
                
                animate();
            })();
        </script>
        """
        st.markdown(firework_html, unsafe_allow_html=True)

        # Status Callout
        if "Health" in raw_label:
            st.success(f"### 🎉 {info['title']} ({confidence:.1f}% Match)")
        elif "Diseased" in raw_label:
            st.error(f"### 🚨 {info['title']} ({confidence:.1f}% Match)")
        else:
            st.warning(f"### ⚠️ {info['title']} ({confidence:.1f}% Match)")

        # Native Cards Container
        with st.container(border=True):
            st.subheader("🌱 Identified Condition / Profile")
            st.info(info["category"])

            st.subheader("📍 Common Geographic & Soil Regions")
            st.write(info["region"])

            st.subheader("☀️ Environmental Factors & Symptoms")
            st.write(info["conditions"])

            st.subheader("💊 Recommended Remedy & Treatment")
            st.success(info["remedy"])

except Exception as e:
    st.error(f"App initialization error: {e}")
    st.info("Ensure 'model.tflite' and 'labels.txt' are present in your GitHub repository root.")
