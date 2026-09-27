import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np

st.set_page_config(page_title="SCERT AI Crop Health Scanner", page_icon="🌿")

st.title("🌿 SCERT AI Crop Disease & Deficiency Scanner")
st.write("Upload or take a photo of a leaf sample to get an instant diagnosis and organic remedy.")

@st.cache_resource
def load_model():
    interpreter = tf.lite.Interpreter(model_path="model.tflite")
    interpreter.allocate_tensors()
    return interpreter

try:
    interpreter = load_model()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    with open("labels.txt", "r") as f:
        labels = [line.strip().split(' ', 1)[-1] for line in f.readlines()]

    REMEDIES = {
        "Healthy": "Crop is healthy! Maintain regular watering.",
        "Diseased": "Fungal/Bacterial infection! Apply organic neem oil spray.",
        "Nitrogen_Deficiency": "Nitrogen Shortage! Add urea, compost, or bio-fertilizers.",
        "Phosphorus_Deficiency": "Phosphorus Shortage! Apply bone meal or rock phosphate.",
        "Potassium_Deficiency": "Potassium Shortage! Add wood ash or potash fertilizer.",
        "Iron_Deficiency": "Iron Shortage! Apply iron chelate (Fe-EDTA) spray."
    }

    img_file = st.camera_input("Take a picture of the leaf") or st.file_uploader("Or upload a leaf image...", type=["jpg", "png", "jpeg"])

    if img_file is not None:
        image = Image.open(img_file).convert('RGB')
        st.image(image, caption='Uploaded Sample', use_column_width=True)
        
        # Preprocess
        img = ImageOps.fit(image, (224, 224), Image.Resampling.LANCZOS)
        img_array = np.asarray(img).astype(np.float32) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
st.image(image, caption='Captured Sample', use_container_width=True)
        # Predict
        interpreter.set_tensor(input_details[0]['index'], img_array)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])

        predicted_index = np.argmax(output_data[0])
        raw_label = labels[predicted_index]
        confidence = output_data[0][predicted_index] * 100

        remedy = REMEDIES.get(raw_label, "Check soil and water parameters.")

        st.success(f"**Diagnosis:** {raw_label} ({confidence:.1f}% confidence)")
        st.info(f"**Organic Remedy:** {remedy}")

except Exception as e:
    st.error(f"Error loading model: {e}")
