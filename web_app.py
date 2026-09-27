import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np

st.set_page_config(page_title="SCERT AI Crop Health Scanner", page_icon="🌿", layout="centered")

st.title("🌿 SCERT AI Plant Health Scanner")
st.write("Take or upload a photo of a leaf sample for instant AI analysis & organic remedies.")

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

    REMEDIES = {
        "Healthy": "Crop is healthy! Maintain regular watering.",
        "Diseased": "Fungal/Bacterial infection! Apply organic neem oil spray.",
        "Nitrogen_Deficiency": "Nitrogen Shortage! Add urea, compost, or bio-fertilizers.",
        "Phosphorus_Deficiency": "Phosphorus Shortage! Apply bone meal or rock phosphate.",
        "Potassium_Deficiency": "Potassium Shortage! Add wood ash or potash fertilizer.",
        "Iron_Deficiency": "Iron Shortage! Apply iron chelate (Fe-EDTA) spray."
    }

    img_file = st.camera_input("Take a photo using phone camera") 
    if not img_file:
        img_file = st.file_uploader("Or upload an image file...", type=["jpg", "png", "jpeg"])

    if img_file is not None:
        image = Image.open(img_file).convert('RGB')
        st.image(image, caption='Captured Sample', use_container_width=True)
        
        # Preprocessing matching model input size
        size = (224, 224)
        image_resample = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
        img_array = np.asarray(image_resample).astype(np.float32) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # Inference
        interpreter.set_tensor(input_details[0]['index'], img_array)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])

        predicted_index = np.argmax(output_data[0])
        raw_label = labels[predicted_index]
        confidence = output_data[0][predicted_index] * 100

        remedy = REMEDIES.get(raw_label, "Check soil moisture and nutrient parameters.")

        st.markdown("---")
        st.subheader(f"Diagnosis: :green[{raw_label}] ({confidence:.1f}% Match)")
        st.info(f"**Recommended Remedy:** {remedy}")

except Exception as e:
    st.error(f"App initialization error: {e}")
    st.warning("Ensure 'model.tflite' and 'labels.txt' are in the root directory of your GitHub repository.")
