import sys
from pathlib import Path
import streamlit as st
from PIL import Image
import tempfile

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.app.detector import RoadDamageDetector
from src.app.severity import SeverityAnalyzer
from src.app.image_utils import annotate_image
from src.app.database_manager import DatabaseManager
from src.app.navigation import render_sidebar

st.set_page_config(
    page_title="Detection Interface",
    layout="wide"
)

# Load CSS
css_file = Path("dashboard/styles/custom.css")
if css_file.exists():
    with open(css_file) as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

# Render Custom Ubuntu Sidebar
render_sidebar("Detection")

st.title("📷 Road Damage Detection")
st.write("Upload a high-resolution image of a road surface to analyze and identify structural defects.")

# Expander for Advanced Settings
with st.expander("⚙️ Advanced Detection Settings", expanded=False):
    conf_threshold = st.slider(
        "🎯 Model Confidence Threshold",
        min_value=0.00,
        max_value=1.00,
        value=0.25,
        step=0.01,
        help="Lower the threshold to detect more objects with lower confidence, or raise it to filter out uncertain detections."
    )
    st.markdown("---")
    st.markdown("#### 📍 Defect Location Mapping (GPS)")
    gps_option = st.radio(
        "GPS Tagging Mode",
        options=["Simulated Local Area (Delhi)", "Manual Input", "No GPS Tagging"],
        index=0,
        help="Simulate a municipal area survey coordinate or input custom coordinates."
    )
    
    col_lat, col_lon = st.columns(2)
    if gps_option == "Manual Input":
        lat_val = col_lat.number_input("Latitude", value=28.6139, format="%.6f")
        lon_val = col_lon.number_input("Longitude", value=77.2090, format="%.6f")
    else:
        lat_val = None
        lon_val = None

# Initialize session state for batch results
if "batch_results" not in st.session_state:
    st.session_state.batch_results = {}

uploaded_files = st.file_uploader(
    "Choose Road Images and Videos...",
    type=["jpg", "jpeg", "png", "mp4", "avi", "mov"],
    accept_multiple_files=True,
    help="Upload one or more road surface images or video recordings to scan."
)

if uploaded_files:
    # Action button on top
    if st.button("🔍 Run Analysis on All Files", use_container_width=True):
        st.session_state.batch_results = {}  # Clear previous results
        
        db = DatabaseManager()
        detector = RoadDamageDetector()
        
        # Outer progress tracking
        progress_bar = st.progress(0.0)
        status_text = st.empty()
        
        for idx, file in enumerate(uploaded_files):
            file_name = file.name
            file_ext = Path(file_name).suffix.lower()
            status_text.text(f"Processing ({idx+1}/{len(uploaded_files)}): {file_name}...")
            
            # --- IMAGE PROCESSING BRANCH ---
            if file_ext in [".jpg", ".jpeg", ".png"]:
                try:
                    file.seek(0)
                    image = Image.open(file)
                    valid_image = True
                except Exception:
                    try:
                        import numpy as np
                        import cv2
                        file.seek(0)
                        file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
                        img_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                        if img_bgr is not None:
                            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
                            image = Image.fromarray(img_rgb)
                            valid_image = True
                        else:
                            valid_image = False
                    except Exception:
                        valid_image = False
                
                if valid_image:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                        image_to_save = image.convert("RGB") if image.mode in ("RGBA", "P", "LA") else image
                        image_to_save.save(tmp.name)
                        detections = detector.detect(tmp.name, conf=conf_threshold)
                    
                    annotated_img = annotate_image(image, detections)
                    summary = detector.get_summary(detections)
                    severity_summary = SeverityAnalyzer.summarize(detections)
                    
                    # Determine GPS Coordinates
                    import random
                    if gps_option == "Simulated Local Area (Delhi)":
                        latitude = 28.6139 + random.uniform(-0.15, 0.15)
                        longitude = 77.2090 + random.uniform(-0.15, 0.15)
                    elif gps_option == "Manual Input":
                        latitude = lat_val
                        longitude = lon_val
                    else:
                        latitude = None
                        longitude = None
                    
                    # Save to Database
                    db.insert_detection(
                        image_name=file_name,
                        potholes=summary.get("pothole", 0),
                        longitudinal=summary.get("longitudinal_crack", 0),
                        lateral=summary.get("lateral_crack", 0),
                        alligator=summary.get("alligator_crack", 0),
                        high=severity_summary.get("High", 0),
                        medium=severity_summary.get("Medium", 0),
                        low=severity_summary.get("Low", 0),
                        latitude=latitude,
                        longitude=longitude
                    )
                    
                    st.session_state.batch_results[file_name] = {
                        "type": "image",
                        "original_image": image,
                        "annotated_image": annotated_img,
                        "summary": summary,
                        "severity": severity_summary,
                        "latitude": latitude,
                        "longitude": longitude
                    }
            
            # --- VIDEO PROCESSING BRANCH ---
            elif file_ext in [".mp4", ".avi", ".mov"]:
                tfile = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
                tfile.write(file.read())
                tfile.close()
                
                import cv2
                cap = cv2.VideoCapture(tfile.name)
                
                cumulative_counts = {"pothole": 0, "longitudinal_crack": 0, "lateral_crack": 0, "alligator_crack": 0}
                severity_counts = {"High": 0, "Medium": 0, "Low": 0}
                
                frame_idx = 0
                processed_count = 0
                last_annotated_frame = None
                step_interval = 10  # Speed up processing during batches by checking every 10th frame
                
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    if frame_idx % step_interval == 0:
                        processed_count += 1
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        pil_img = Image.fromarray(frame_rgb)
                        
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_frame:
                            pil_img.save(tmp_frame.name)
                            detections = detector.detect(tmp_frame.name, conf=conf_threshold)
                        
                        frame_summary = detector.get_summary(detections)
                        frame_severity = SeverityAnalyzer.summarize(detections)
                        
                        for k in cumulative_counts:
                            cumulative_counts[k] += frame_summary.get(k, 0)
                        for k in severity_counts:
                            severity_counts[k] += frame_severity.get(k, 0)
                        
                        if len(detections) > 0 or last_annotated_frame is None:
                            last_annotated_frame = annotate_image(pil_img, detections)
                            
                    frame_idx += 1
                
                cap.release()
                
                # Determine GPS Coordinates
                import random
                if gps_option == "Simulated Local Area (Delhi)":
                    latitude = 28.6139 + random.uniform(-0.15, 0.15)
                    longitude = 77.2090 + random.uniform(-0.15, 0.15)
                elif gps_option == "Manual Input":
                    latitude = lat_val
                    longitude = lon_val
                else:
                    latitude = None
                    longitude = None
                
                # Save to Database
                db.insert_detection(
                    image_name=f"[Video Batch] {file_name}",
                    potholes=cumulative_counts["pothole"],
                    longitudinal=cumulative_counts["longitudinal_crack"],
                    lateral=cumulative_counts["lateral_crack"],
                    alligator=cumulative_counts["alligator_crack"],
                    high=severity_counts["High"],
                    medium=severity_counts["Medium"],
                    low=severity_counts["Low"],
                    latitude=latitude,
                    longitude=longitude
                )
                
                st.session_state.batch_results[file_name] = {
                    "type": "video",
                    "annotated_image": last_annotated_frame,
                    "summary": cumulative_counts,
                    "severity": severity_counts,
                    "latitude": latitude,
                    "longitude": longitude
                }
            
            progress_bar.progress((idx + 1) / len(uploaded_files))
            
        status_text.success("🎉 Batch analysis completed successfully!")
        st.balloons()
        
    st.markdown("---")
    st.markdown("### 📋 Upload Queue & Results")
    
    # Create dynamic tabs for each uploaded file
    tabs = st.tabs([f.name for f in uploaded_files])
    
    for idx, (tab, file) in enumerate(zip(tabs, uploaded_files)):
        with tab:
            file_name = file.name
            file_ext = Path(file_name).suffix.lower()
            
            # Render results if they exist in session state
            if file_name in st.session_state.batch_results:
                res = st.session_state.batch_results[file_name]
                col_left, col_right = st.columns(2)
                
                with col_left:
                    st.success("✅ Analysis completed!")
                    if res["type"] == "image":
                        st.image(res["original_image"], caption="Uploaded Original Image", use_container_width=True)
                    else:
                        st.info("📹 Video scan successfully processed.")
                        
                with col_right:
                    if res["annotated_image"] is not None:
                        st.image(res["annotated_image"], caption="Annotated Detections Output", use_container_width=True)
                    
                    st.markdown("### 🚨 Findings Details")
                    summary = res["summary"]
                    severity = res["severity"]
                    total_defects = sum(summary.values())
                    
                    metric_c1, metric_c2 = st.columns(2)
                    with metric_c1:
                        st.metric("Total Defects", f"{total_defects}")
                    with metric_c2:
                        st.metric("High Severity Alerts", f"{severity.get('High', 0)}")
                        
                    if res["latitude"] is not None and res["longitude"] is not None:
                        st.caption(f"📍 GPS Location Logged: **{res['latitude']:.6f}, {res['longitude']:.6f}**")
                    
                    st.info(f"🧱 Potholes: **{summary.get('pothole', 0)}**")
                    st.info(f"📈 Longitudinal Cracks: **{summary.get('longitudinal_crack', 0)}**")
                    st.info(f"📉 Lateral Cracks: **{summary.get('lateral_crack', 0)}**")
                    st.info(f"🐊 Alligator Cracks: **{summary.get('alligator_crack', 0)}**")
                    
                    high_count = severity.get("High", 0)
                    med_count = severity.get("Medium", 0)
                    low_count = severity.get("Low", 0)
                    
                    if high_count > 0:
                        st.error(f"🚨 High Risk: **{high_count}** defect(s) detected. Requires immediate intervention!")
                    if med_count > 0:
                        st.warning(f"⚠️ Medium Risk: **{med_count}** defect(s) detected. Plan repairs soon.")
                    if low_count > 0:
                        st.success(f"✅ Low Risk: **{low_count}** defect(s) detected. Keep monitoring.")
            else:
                st.warning("⏳ Click 'Run Analysis on All Files' to process this item.")
                if file_ext in [".jpg", ".jpeg", ".png"]:
                    st.image(file, caption="Preview Image", use_container_width=True)
                else:
                    st.info("📹 Video loaded and ready for scanning.")