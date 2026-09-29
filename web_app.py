import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(page_title="Cellular Vision", page_icon="🍃", layout="centered")

# Initialize Session State for Page Navigation & Results
if "page" not in st.session_state:
    st.session_state.page = "upload"
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

# Custom Global Styling
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
        margin-top: 5px;
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
        margin-bottom: 1.5rem;
    }

    /* Card styling */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(120, 255, 214, 0.2);
        border-radius: 12px;
        padding: 15px;
    }
</style>
""", unsafe_allow_html=True)


# Full-Screen Parent Canvas Overlay Component
def render_fullscreen_firework():
    html_code = """
    <!DOCTYPE html>
    <html>
    <head></head>
    <body>
        <script>
            (function() {
                try {
                    // Access top window document to bypass Streamlit iframe restriction
                    const parentDoc = window.top.document;
                    let canvas = parentDoc.getElementById('globalEmojiCanvas');

                    if (!canvas) {
                        canvas = parentDoc.createElement('canvas');
                        canvas.id = 'globalEmojiCanvas';
                        canvas.style.position = 'fixed';
                        canvas.style.top = '0';
                        canvas.style.left = '0';
                        canvas.style.width = '100vw';
                        canvas.style.height = '100vh';
                        canvas.style.pointerEvents = 'none';
                        canvas.style.zIndex = '999999';
                        parentDoc.body.appendChild(canvas);
                    }

                    const ctx = canvas.getContext('2d');
                    canvas.width = window.top.innerWidth;
                    canvas.height = window.top.innerHeight;

                    const emojis = ['🍃', '✨', '🌱', '🌾', '🌿', '🌸', '💫'];
                    const particles = [];

                    // Launch 70 emoji particles across the entire viewport width
                    for (let i = 0; i < 70; i++) {
                        particles.push({
                            x: Math.random() * canvas.width,
                            y: canvas.height + 30,
                            vx: (Math.random() - 0.5) * 16,
                            vy: -(Math.random() * 18 + 14), // High upward velocity
                            size: Math.floor(Math.random() * 26 + 32),
                            emoji: emojis[Math.floor(Math.random() * emojis.length)],
                            alpha: 1,
                            rotation: Math.random() * Math.PI * 2,
                            vRot: (Math.random() - 0.5) * 0.25
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
                                p.vy += 0.32; // Natural gravity curve
                                p.rotation += p.vRot;
                                p.alpha -= 0.008; // Smooth screen transition fade

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
                        } else {
                            ctx.clearRect(0, 0, canvas.width, canvas.height);
                        }
                    }
                    animate();
                } catch(e) {
                    console.log("Iframe security restricted parent canvas injection.", e);
                }
            })();
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=0, width=0)


@st.cache_resource
def load_interpreter():
    interpreter = tf.lite.Interpreter(model_path="model.tflite")
    interpreter.allocate_tensors()
    return interpreter


# Expanded Botanical & Agricultural Database
PLANT_DATABASE = {
    "Health": {
        "title": "Optimal Crop Health ✨",
        "category": "Healthy Foliage — No Pathogenic or Nutritional Stress Detected",
        "region": "Globally distributed across well-managed agricultural, greenhouse, and residential zones.",
        "conditions": "Sustained by optimal solar irradiance (6–8 hrs/day), balanced root-zone hydration, non-compacted soil aeration, and balanced N-P-K nutrient uptake.",
        "remedy": "• Maintain current irrigation cycle (water deeply at soil base, avoiding leaf moisture).\n• Perform routine soil testing every 6 months to monitor pH (aim for 6.0–6.8).\n• Apply thin organic compost layer during active growing seasons to sustain microbial health."
    },
    "Diseased": {
        "title": "Pathogenic Stress / Infection 🚨",
        "category": "Fungal, Bacterial, or Viral Foliar Infection",
        "region": "Prevalent in high-humidity microclimates, poorly ventilated canopy zones, and waterlogged fields.",
        "conditions": "Triggered by prolonged leaf wetness, high ambient humidity (>80%), air stagnation, or infected plant debris.",
        "remedy": "• **Isolation:** Quarantining affected crops to prevent spore transmission across adjacent rows.\n• **Sanitation:** Prune infected leaves using shears sanitized with 70% isopropyl alcohol.\n• **Treatment:** Apply copper octanoate, neem oil extract, or sulfur-based bio-fungicide early morning or late evening."
    },
    "Nitrogen_Deficiency": {
        "title": "Nitrogen (N) Deficiency 🟡",
        "category": "Mobile Macronutrient Shortage (Chlorosis)",
        "region": "Common in heavily leached sandy soils, low organic matter soils, or fields under intensive monoculture cropping.",
        "conditions": "Manifests as progressive yellowing starting on mature lower leaves (chlorosis) due to plant reallocating mobile N to new upper growth.",
        "remedy": "• **Immediate Action:** Apply fast-acting foliar spray with organic fish hydrolysate or liquid amino acid kelp meal.\n• **Soil Amendment:** Incorporate blood meal, composted poultry manure, or feather meal into root zone.\n• **Long-term Strategy:** Plant leguminous cover crops (clover, vetch) to naturally fix atmospheric nitrogen into the soil matrix."
    },
    "Phosphorus_Deficiency": {
        "title": "Phosphorus (P) Deficiency 🟣",
        "category": "Energy Transfer & Root-Zone Macronutrient Impairment",
        "region": "Prevalent in cold, wet spring soils, highly acidic soils (pH < 5.5), or alkaline soils (pH > 7.5) where P binds tightly.",
        "conditions": "Symptom: Stunted shoot growth, delayed maturity, and distinct purplish or reddish pigmentation along leaf veins and undersides due to anthocyanin accumulation.",
        "remedy": "• **Soil Adjustment:** Adjust soil pH to optimal range (6.0–7.0) to unbind trapped phosphorus.\n• **Fertilization:** Drench root area with soft rock phosphate, bone meal, or concentrated mono-potassium phosphate.\n• **Root Support:** Inoculate soil with Mycorrhizal fungi to expand effective root surface area for P absorption."
    },
    "Potassium_Deficiency": {
        "title": "Potassium (K) Deficiency 🟠",
        "category": "Osmotic & Enzymatic Regulation Deficit",
        "region": "Frequent in light sandy soils subject to heavy rainfall, as well as highly acidic or heavily limed soils.",
        "conditions": "Symptom: Marginal chlorosis and scorch (browning/necrosis along leaf edges), downward leaf curling, and weakened structural stems.",
        "remedy": "• **Immediate Treatment:** Apply potassium sulfate or kelp meal solution to soil base.\n• **Organic Option:** Top-dress soil with hardwood ash (wood ash) in controlled quantities.\n• **Water Management:** Maintain uniform moisture levels; drought exacerbates potassium uptake blockage."
    },
    "Iron_Deficiency": {
        "title": "Iron (Fe) Deficiency ⚪",
        "category": "Immobile Micronutrient Chlorosis",
        "region": "Common in calcareous soils (high calcium carbonate), alkaline soils (pH > 7.5), over-watered soils, or soils high in heavy metals.",
        "conditions": "Symptom: Interveinal chlorosis appearing strictly on newest young leaves — tissue between veins turns pale yellow/ivory while main veins remain dark green.",
        "remedy": "• **Foliar Spray:** Apply chelated iron (Fe-EDTA for pH < 6.5 or Fe-EDDHA for alkaline soils pH > 7.5) directly onto leaf foliage.\n• **Soil Acidification:** Incorporate elemental sulfur or peat moss to lower soil alkalinity into 6.0–6.8 range.\n• **Aeration:** Reduce over-watering and improve soil drainage to allow root respiration."
    }
}


# ==================== SCREEN 1: UPLOAD PAGE ====================
if st.session_state.page == "upload":
    st.markdown('<div class="cute-logo">🍃🌱🔬</div>', unsafe_allow_html=True)
    st.markdown('<div class="title-text">Cellular Vision</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">✨ AI Botanical Explorer & Plant Care Companion ✨</div>', unsafe_allow_html=True)

    try:
        interpreter = load_interpreter()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        with open("labels.txt", "r") as f:
            labels = [line.strip().split(' ', 1)[-1].strip() for line in f.readlines()]

        img_file = st.camera_input("📷 Snap a leaf photo")
        if not img_file:
            img_file = st.file_uploader("📁 Or pick a leaf picture...", type=["jpg", "png", "jpeg"])

        if img_file is not None:
            image = Image.open(img_file).convert('RGB')
            st.image(image, caption='🔍 Leaf Sample Loaded', use_container_width=True)

            if st.button("🚀 Analyze Plant Health", use_container_width=True, type="primary"):
                # Run Inference
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
                    "title": raw_label.replace("_", " "),
                    "category": "General Plant Analysis Profile",
                    "region": "Widespread temperate and tropical growing zones.",
                    "conditions": "Moderate lighting, well-draining soil, regular watering.",
                    "remedy": "Inspect plant foliage for signs of physical stress or pests. Maintain steady moisture and temperature."
                })

                # Store analysis results and trigger page swap
                st.session_state.analysis_result = {
                    "info": info,
                    "confidence": confidence,
                    "raw_label": raw_label,
                    "image": image
                }
                st.session_state.page = "results"
                st.rerun()

    except Exception as e:
        st.error(f"App initialization error: {e}")
        st.info("Ensure 'model.tflite' and 'labels.txt' are present in your GitHub repository root.")


# ==================== SCREEN 2: RESULTS PAGE ====================
elif st.session_state.page == "results":
    # Trigger Full-Screen Transition Overlay via Parent Window Injection
    render_fullscreen_firework()

    res = st.session_state.analysis_result
    info = res["info"]
    confidence = res["confidence"]
    raw_label = res["raw_label"]

    # Header with Navigation Back Button
    col_nav, col_title = st.columns([1, 4])
    with col_nav:
        if st.button("⬅️ Back"):
            st.session_state.page = "upload"
            st.session_state.analysis_result = None
            st.rerun()

    with col_title:
        st.markdown("<h3 style='margin:0; padding:0;'>🔬 Analysis Report</h3>", unsafe_allow_html=True)

    st.markdown("---")

    # Status Match Banner
    if "Health" in raw_label:
        st.success(f"### 🎉 {info['title']} ({confidence:.1f}% Confidence)")
    elif "Diseased" in raw_label:
        st.error(f"### 🚨 {info['title']} ({confidence:.1f}% Confidence)")
    else:
        st.warning(f"### ⚠️ {info['title']} ({confidence:.1f}% Confidence)")

    # Detailed Botanical & Agricultural Card
    with st.container(border=True):
        st.subheader("🌱 Identified Condition & Profile")
        st.info(info["category"])

        st.subheader("📍 Common Geographic & Soil Regions")
        st.write(info["region"])

        st.subheader("☀️ Environmental Factors & Diagnostic Symptoms")
        st.write(info["conditions"])

        st.subheader("💊 Recommended Remedy & Agricultural Treatment Plan")
        st.success(info["remedy"])
