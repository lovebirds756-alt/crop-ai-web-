import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np

# Page configuration
st.set_page_config(page_title="Cellular Vision", page_icon="🔬", layout="centered")

st.title("🔬 Cellular Vision: AI Plant Diagnostics & Botanical Intelligence")
st.write("Scan or upload a leaf sample to identify the plant species, native origin, ideal growing conditions, and disease diagnostics.")

@st.cache_resource
def load_interpreter():
    interpreter = tf.lite.Interpreter(model_path="model.tflite")
    interpreter.allocate_tensors()
    return interpreter

try:
    interpreter = load_interpreter()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # Read model class labels
    with open("labels.txt", "r") as f:
        labels = [line.strip().split(' ', 1)[-1] for line in f.readlines()]

    # Extended botanical & diagnostic database
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

    # Camera & Upload Inputs
    img_file = st.camera_input("Take a photo using camera") 
    if not img_file:
        img_file = st.file_uploader("Or upload a leaf image file...", type=["jpg", "png", "jpeg"])

    if img_file is not None:
        image = Image.open(img_file).convert('RGB')
        st.image(image, caption='Processed Sample', use_container_width=True)
        
        # Image Preprocessing
        size = (224, 224)
        image_resample = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
        img_array = np.asarray(image_resample).astype(np.float32) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # Run AI Inference
        interpreter.set_tensor(input_details[0]['index'], img_array)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])

        predicted_index = np.argmax(output_data[0])
        raw_label = labels[predicted_index]
        confidence = output_data[0][predicted_index] * 100

        # Retrieve botanical info from dict or fallback
        info = PLANT_DATABASE.get(raw_label, {
            "plant_name": raw_label.split("___")[0].replace("_", " "),
            "region": "Subtropical & Temperate Agricultural Zones.",
            "conditions": "Full sun exposure, well-draining soil, moderate watering.",
            "status": raw_label.replace("_", " "),
            "remedy": "Inspect plant for signs of stress, maintain moisture levels, and balance soil nutrients."
        })

        st.markdown("---")
        
        # Display Botanical & Geographic Context
        st.subheader(f"🌱 Plant Species: {info['plant_name']}")
        st.write(f"**📍 Native / Primary Region:** {info['region']}")
        st.write(f"**☀️ Ideal Growing Conditions:** {info['conditions']}")
        
        st.markdown("---")
        
        # Display Health & Remedial Actions
        if "healthy" in raw_label.lower():
            st.success(f"**Health Status:** {info['status']} ({confidence:.1f}% Match)")
            st.info(f"**Action:** {info['remedy']}")
        else:
            st.error(f"**Health Status:** {info['status']} ({confidence:.1f}% Match)")
            st.warning(f"**Recommended Remedy:** {info['remedy']}")

except Exception as e:
    st.error(f"App initialization error: {e}")
    st.info("Ensure 'model.tflite' and 'labels.txt' are present in your GitHub repository root.")
