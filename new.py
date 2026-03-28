# smart_bin_streamlit.py
import streamlit as st
import cv2
from ultralytics import YOLO
import numpy as np

# -----------------------------
# Load YOLO model
# -----------------------------
@st.cache_resource
def load_model():
    # Make sure yolov8n.pt is in the same folder as this script
    model = YOLO("yolov8n.pt")
    return model

model = load_model()

# -----------------------------
# Waste guidelines
# -----------------------------
WASTE_INFO = {
    "bottle": "Plastic bottle → Yellow bin (clean). Rinse before disposal.",
    "book": "Paper → Blue bin. Recycle after removing bindings if possible.",
    "laptop": "Electronic → Special e-waste collection.",
    "cup": "Plastic/Disposable cup → Yellow bin (if clean), else trash.",
    "metal": "Metal → Red bin. Clean metals only.",
    "paper": "Paper → Blue bin.",
    "can": "Metal can → Red bin.",
    "other": "Unknown item → Dispose as per local waste rules."
}

# -----------------------------
# Helper: Ignore people
# -----------------------------
IGNORED_CLASSES = ["person"]

# -----------------------------
# Check contamination
# -----------------------------
def check_contamination(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mean_val = np.mean(gray)
    if mean_val < 80:
        return "Wet/Dirty"
    elif mean_val < 150:
        return "Mildly dirty"
    else:
        return "Dry/Clean"

# -----------------------------
# Streamlit App
# -----------------------------
st.title("♻️ Smart Bin AI - One-shot Detection")

st.write(
    "Click the button below to capture a frame from your webcam and detect waste items."
)

# Unique key ensures no Streamlit duplicate element errors
if st.button("Capture & Detect Waste", key="capture_waste_btn"):
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()  # Close camera immediately

    if not ret:
        st.error("Failed to capture image from camera.")
    else:
        # Show captured frame
        st.image(frame[..., ::-1], channels="RGB", caption="Captured Image")

        # -----------------------------
        # Run YOLO detection
        # -----------------------------
        results = model(frame)
        result = results[0]

        detected_items = []
        for box, cls in zip(result.boxes.xyxy, result.boxes.cls):
            item_name = model.names[int(cls)]
            if item_name.lower() not in IGNORED_CLASSES:
                detected_items.append(item_name.lower())

        if not detected_items:
            st.warning("No valid waste items detected.")
        else:
            contamination = check_contamination(frame)
            st.subheader("Detected Items & Disposal Guidelines")

            for item in detected_items:
                info = WASTE_INFO.get(item, WASTE_INFO["other"])
                st.markdown(f"**Item:** {item.capitalize()}")
                st.markdown(f"- **Contamination:** {contamination}")
                st.markdown(f"- **Guidelines:** {info}")

        st.success("Detection complete. Camera closed.")