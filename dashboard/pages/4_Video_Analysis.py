import sys
from pathlib import Path
import streamlit as st
import tempfile
import cv2
import pandas as pd
import numpy as np
from PIL import Image
import time
import plotly.express as px

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.app.detector import RoadDamageDetector
from src.app.severity import SeverityAnalyzer
from src.app.image_utils import annotate_image
from src.app.database_manager import DatabaseManager
from src.app.navigation import render_sidebar

st.set_page_config(
    page_title="Video Analysis",
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

# Render Custom Sidebar
render_sidebar("Video Analysis")

st.title("🎥 Live Video Analysis")
st.write("Upload pavement survey recordings to scan and map structural defects frame-by-frame.")

# Expander for Video Analysis Settings
with st.expander("⚙️ Video Processing Settings", expanded=False):
    conf_threshold = st.slider(
        "🎯 Model Confidence Threshold",
        min_value=0.00,
        max_value=1.00,
        value=0.25,
        step=0.01,
        help="Model prediction confidence filter."
    )
    
    frame_skip = st.slider(
        "⚡ Frame Processing Interval",
        min_value=1,
        max_value=10,
        value=3,
        step=1,
        help="Process every Nth frame. Higher values significantly speed up processing by skipping redundant frames."
    )
    
    st.markdown("---")
    st.markdown("#### 📍 Video GPS Mapping Location")
    gps_option = st.radio(
        "GPS Tagging Mode",
        options=["Simulated Local Area (Delhi)", "Manual Input", "No GPS Tagging"],
        index=0
    )
    
    col_lat, col_lon = st.columns(2)
    if gps_option == "Manual Input":
        lat_val = col_lat.number_input("Latitude", value=28.6139, format="%.6f")
        lon_val = col_lon.number_input("Longitude", value=77.2090, format="%.6f")
    else:
        lat_val = None
        lon_val = None

uploaded_video = st.file_uploader(
    "Upload Road Video",
    type=["mp4", "avi", "mov", "mkv"]
)

if uploaded_video:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tfile.write(uploaded_video.read())
    tfile.close()
    
    cap = cv2.VideoCapture(tfile.name)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    st.info(f"📹 Video Loaded: **{uploaded_video.name}** | FPS: **{fps}** | Total Frames: **{total_frames}**")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        video_placeholder = st.empty()
        # Show initial frame
        ret, first_frame = cap.read()
        if ret:
            first_rgb = cv2.cvtColor(first_frame, cv2.COLOR_BGR2RGB)
            video_placeholder.image(first_rgb, use_container_width=True, caption="Video Preview")
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # reset to frame 0
        
    with col2:
        st.markdown("### 📊 Real-Time Video Stats")
        
        stat_metric1, stat_metric2 = st.columns(2)
        total_defects_metric = stat_metric1.metric("Defects Detected", "0")
        fps_metric = stat_metric2.metric("Proc Speed (FPS)", "0.0")
        
        st.markdown("#### Itemized Cumulative Counts")
        pot_metric = st.info("🧱 Potholes: **0**")
        long_metric = st.info("📈 Longitudinal Cracks: **0**")
        lat_metric = st.info("📉 Lateral Cracks: **0**")
        alli_metric = st.info("🐊 Alligator Cracks: **0**")
        
        chart_placeholder = st.empty()
        
    if st.button("🎥 Start Real-Time Scan", use_container_width=True):
        progress_bar = st.progress(0.0)
        status_text = st.empty()
        
        detector = RoadDamageDetector()
        
        # Cumulative trackers
        cumulative_counts = {"pothole": 0, "longitudinal_crack": 0, "lateral_crack": 0, "alligator_crack": 0}
        severity_counts = {"High": 0, "Medium": 0, "Low": 0}
        
        timeline_data = []
        
        frame_idx = 0
        processed_count = 0
        start_time = time.time()
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_idx % frame_skip == 0:
                processed_count += 1
                
                # Run YOLO prediction on frame
                # Convert BGR frame to RGB Image for YOLO/Pillow
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(frame_rgb)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_frame:
                    pil_img.save(tmp_frame.name)
                    detections = detector.detect(tmp_frame.name, conf=conf_threshold)
                
                # Annotate and show frame
                annotated_rgb = annotate_image(pil_img, detections)
                video_placeholder.image(annotated_rgb, use_container_width=True, caption=f"Scanning Frame {frame_idx}/{total_frames}")
                
                # Get frame stats
                frame_summary = detector.get_summary(detections)
                frame_severity = SeverityAnalyzer.summarize(detections)
                
                # Update cumulative counters
                for key in cumulative_counts:
                    cumulative_counts[key] += frame_summary.get(key, 0)
                for key in severity_counts:
                    severity_counts[key] += frame_severity.get(key, 0)
                    
                # Update live metric widgets
                total_defects_in_frame = sum(frame_summary.values())
                total_cumulative_defects = sum(cumulative_counts.values())
                
                elapsed = time.time() - start_time
                curr_fps = processed_count / elapsed if elapsed > 0 else 0.0
                
                # Update sidebar metrics in dashboard col2
                total_defects_metric.metric("Defects Detected", f"{total_cumulative_defects}")
                fps_metric.metric("Proc Speed (FPS)", f"{curr_fps:.1f}")
                
                pot_metric.info(f"🧱 Potholes: **{cumulative_counts['pothole']}**")
                long_metric.info(f"📈 Longitudinal Cracks: **{cumulative_counts['longitudinal_crack']}**")
                lat_metric.info(f"📉 Lateral Cracks: **{cumulative_counts['lateral_crack']}**")
                alli_metric.info(f"🐊 Alligator Cracks: **{cumulative_counts['alligator_crack']}**")
                
                # Add to timeline for chart
                seconds = frame_idx / fps if fps > 0 else 0
                timeline_data.append({
                    "Timestamp (s)": seconds,
                    "Potholes": cumulative_counts["pothole"],
                    "Longitudinal Cracks": cumulative_counts["longitudinal_crack"],
                    "Lateral Cracks": cumulative_counts["lateral_crack"],
                    "Alligator Cracks": cumulative_counts["alligator_crack"]
                })
                
                # Render line chart
                df_timeline = pd.DataFrame(timeline_data)
                fig_timeline = px.line(
                    df_timeline,
                    x="Timestamp (s)",
                    y=["Potholes", "Longitudinal Cracks", "Lateral Cracks", "Alligator Cracks"],
                    title="Defect Counts Timeline Scanned",
                    labels={"value": "Cumulative Count", "variable": "Defect Type"}
                )
                fig_timeline.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=20, r=20, t=30, b=20),
                    height=250
                )
                chart_placeholder.plotly_chart(fig_timeline, use_container_width=True)
                
            frame_idx += 1
            progress_bar.progress(min(frame_idx / total_frames, 1.0))
            status_text.text(f"Processed {frame_idx}/{total_frames} frames ({int(frame_idx/total_frames*100)}%)")
            
        cap.release()
        
        # Determine GPS location
        if gps_option == "Simulated Local Area (Delhi)":
            import random
            latitude = 28.6139 + random.uniform(-0.15, 0.15)
            longitude = 77.2090 + random.uniform(-0.15, 0.15)
        elif gps_option == "Manual Input":
            latitude = lat_val
            longitude = lon_val
        else:
            latitude = None
            longitude = None
            
        # Save to database
        db = DatabaseManager()
        db.insert_detection(
            image_name=f"[Video Scan] {uploaded_video.name}",
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
        
        st.balloons()
        st.success("✅ Video processing completed! Aggregate defect counts have been successfully stored in history.")
        if latitude is not None and longitude is not None:
            st.info(f"📍 GPS Location Logged: **{latitude:.6f}, {longitude:.6f}**")
