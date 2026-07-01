import streamlit as st
from pathlib import Path
import sys

# Ensure root directory is on the path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.app.database_manager import DatabaseManager
from src.app.detector import RoadDamageDetector
from src.app.navigation import render_sidebar

st.set_page_config(
    page_title="SmartRoad AI - Home",
    page_icon="🛣️",
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
render_sidebar("Home")

# Header
st.markdown("""
<div style="
display:flex;
justify-content:space-between;
align-items:center;
padding:24px 32px;
background:linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
color:white;
border-radius:15px;
margin-bottom:25px;
box-shadow:0 4px 20px rgba(59, 130, 246, 0.15);
">
    <div>
        <h1 style="margin:0; font-weight:700; font-size:2.2rem; color:white;">🛣️ SmartRoad AI</h1>
        <p style="margin:5px 0 0 0; opacity:0.9; font-size:1rem; color:white;">AI-Powered Infrastructure Defect & Damage Intelligence Portal</p>
    </div>
    <div style="text-align:right; margin-left:20px;">
        <span style="background:rgba(255,255,255,0.2); padding:8px 16px; border-radius:30px; font-size:0.85rem; font-weight:600; border:1px solid rgba(255,255,255,0.3); color:white; white-space:nowrap;">
            System Status: Online
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# Database check & Model check
db = DatabaseManager()
detector = RoadDamageDetector()

# Seed Mock Data Function
def seed_mock_data(num_records):
    import random
    from datetime import datetime, timedelta
    
    db.clear_database()
    image_prefixes = ["road_scan", "route_pavement", "expressway_A", "highway_inf", "street_det", "urban_transit"]
    now = datetime.now()
    
    for i in range(num_records):
        days_ago = random.uniform(0, 30)
        timestamp = now - timedelta(days=days_ago)
        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        image_name = f"{random.choice(image_prefixes)}_{random.randint(100, 999)}.jpg"
        potholes = random.choice([0, 0, 1, 2, 3, 4])
        longitudinal = random.choice([0, 1, 2])
        lateral = random.choice([0, 1, 2])
        alligator = random.choice([0, 0, 1])
        
        total_defects = potholes + longitudinal + lateral + alligator
        
        high = 0
        medium = 0
        low = 0
        
        for _ in range(total_defects):
            area = random.randint(1000, 35000)
            if area < 5000:
                low += 1
            elif area < 20000:
                medium += 1
            else:
                high += 1
                
        # Generate coordinates centered around Delhi, India
        lat = 28.6139 + random.uniform(-0.15, 0.15)
        lon = 77.2090 + random.uniform(-0.15, 0.15)
                
        cursor = db.conn.cursor()
        cursor.execute("""
        INSERT INTO detections (
            image_name, potholes, longitudinal_cracks, lateral_cracks, alligator_cracks,
            high_risk, medium_risk, low_risk, latitude, longitude, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (image_name, potholes, longitudinal, lateral, alligator, high, medium, low, lat, lon, timestamp_str))
        
    db.conn.commit()

# Live Stats Calculation
detections = db.get_all_detections()
total_reports = len(detections)

total_defects = 0
total_high = 0
total_potholes = 0

for d in detections:
    total_defects += d[2] + d[3] + d[4] + d[5]
    total_high += d[6]
    total_potholes += d[2]

# Left Column: Information & Navigation
# Right Column: System Diagnostics & Simulator
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("### 🔍 System Overview")
    st.write(
        "SmartRoad AI uses advanced computer vision and convolutional neural networks to detect, "
        "measure, and assess structural road defects. It automatically classifies defects into potholes, "
        "cracks, and computes risk levels based on geometric sizes (defect areas) to help prioritize road maintenance operations."
    )
    
    st.markdown("### 🧭 Quick Navigation Portal")
    
    nav_col1, nav_col2, nav_col3 = st.columns(3)
    
    with nav_col1:
        st.markdown(
            '<a href="/Detection" target="_self" style="text-decoration: none; color: inherit; display: block; height: 100%;">'
            '<div class="card" style="min-height: 180px; display: flex; flex-direction: column; justify-content: space-between;">'
            '<div>'
            '<h4 class="card-title" style="margin-top:0; font-family:\'Plus Jakarta Sans\', sans-serif; font-weight: 600;">🔍 Detection</h4>'
            '<p class="card-desc" style="font-size:0.9rem; margin-bottom:15px; font-family:\'Plus Jakarta Sans\', sans-serif; line-height: 1.4;">Upload road images, execute model inference, analyze severity levels, and visualize annotated bounding boxes.</p>'
            '</div>'
            '<div><span class="btn-grad" style="margin: 0; width: 100%;">Open Detection</span></div>'
            '</div>'
            '</a>',
            unsafe_allow_html=True
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown(
            '<a href="/History" target="_self" style="text-decoration: none; color: inherit; display: block; height: 100%;">'
            '<div class="card" style="min-height: 180px; display: flex; flex-direction: column; justify-content: space-between;">'
            '<div>'
            '<h4 class="card-title" style="margin-top:0; font-family:\'Plus Jakarta Sans\', sans-serif; font-weight: 600;">📜 History</h4>'
            '<p class="card-desc" style="font-size:0.9rem; margin-bottom:15px; font-family:\'Plus Jakarta Sans\', sans-serif; line-height: 1.4;">Search and inspect past road inspection reports, filter by severity risk levels, and examine itemized counts.</p>'
            '</div>'
            '<div><span class="btn-grad" style="margin: 0; width: 100%;">Open History</span></div>'
            '</div>'
            '</a>',
            unsafe_allow_html=True
        )
        
    with nav_col2:
        st.markdown(
            '<a href="/Dashboard" target="_self" style="text-decoration: none; color: inherit; display: block; height: 100%;">'
            '<div class="card" style="min-height: 180px; display: flex; flex-direction: column; justify-content: space-between;">'
            '<div>'
            '<h4 class="card-title" style="margin-top:0; font-family:\'Plus Jakarta Sans\', sans-serif; font-weight: 600;">🖥️ Dashboard</h4>'
            '<p class="card-desc" style="font-size:0.9rem; margin-bottom:15px; font-family:\'Plus Jakarta Sans\', sans-serif; line-height: 1.4;">Examine high-level metrics, pie charts, interactive GPS maps, and defect frequency distributions across all inspections.</p>'
            '</div>'
            '<div><span class="btn-grad" style="margin: 0; width: 100%;">Open Dashboard</span></div>'
            '</div>'
            '</a>',
            unsafe_allow_html=True
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown(
            '<a href="/Analytics" target="_self" style="text-decoration: none; color: inherit; display: block; height: 100%;">'
            '<div class="card" style="min-height: 180px; display: flex; flex-direction: column; justify-content: space-between;">'
            '<div>'
            '<h4 class="card-title" style="margin-top:0; font-family:\'Plus Jakarta Sans\', sans-serif; font-weight: 600;">📈 Analytics</h4>'
            '<p class="card-desc" style="font-size:0.9rem; margin-bottom:15px; font-family:\'Plus Jakarta Sans\', sans-serif; line-height: 1.4;">Deep-dive into chronological defect trends, time-series composition, and defect area correlations.</p>'
            '</div>'
            '<div><span class="btn-grad" style="margin: 0; width: 100%;">Open Analytics</span></div>'
            '</div>'
            '</a>',
            unsafe_allow_html=True
        )

    with nav_col3:
        st.markdown(
            '<a href="/Video_Analysis" target="_self" style="text-decoration: none; color: inherit; display: block; height: 100%;">'
            '<div class="card" style="min-height: 180px; display: flex; flex-direction: column; justify-content: space-between;">'
            '<div>'
            '<h4 class="card-title" style="margin-top:0; font-family:\'Plus Jakarta Sans\', sans-serif; font-weight: 600;">🎥 Video Analysis</h4>'
            '<p class="card-desc" style="font-size:0.9rem; margin-bottom:15px; font-family:\'Plus Jakarta Sans\', sans-serif; line-height: 1.4;">Upload raw pavement videos, perform real-time model inference, track dynamic defect counts, and save analysis logs.</p>'
            '</div>'
            '<div><span class="btn-grad" style="margin: 0; width: 100%;">Open Video</span></div>'
            '</div>'
            '</a>',
            unsafe_allow_html=True
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown(
            '<a href="/AI_Assistant" target="_self" style="text-decoration: none; color: inherit; display: block; height: 100%;">'
            '<div class="card" style="min-height: 180px; display: flex; flex-direction: column; justify-content: space-between;">'
            '<div>'
            '<h4 class="card-title" style="margin-top:0; font-family:\'Plus Jakarta Sans\', sans-serif; font-weight: 600;">💬 AI Assistant</h4>'
            '<p class="card-desc" style="font-size:0.9rem; margin-bottom:15px; font-family:\'Plus Jakarta Sans\', sans-serif; line-height: 1.4;">Interact with our database-aware offline AI to generate summary reports, query stats, and receive maintenance planning alerts.</p>'
            '</div>'
            '<div><span class="btn-grad" style="margin: 0; width: 100%;">Open Chat</span></div>'
            '</div>'
            '</a>',
            unsafe_allow_html=True
        )

with col_right:
    st.markdown("### 💻 System Diagnostics")
    
    model_status_html = ""
    if detector.mock_mode:
        model_status_html = '<span style="color:#D97706; font-weight:600;">⚠️ Mock Simulator Active</span><br><small style="color:#6B7280;">(YOLO weights not found. Running synthetic detection)</small>'
    else:
        model_status_html = '<span style="color:#059669; font-weight:600;">✅ YOLO Model Active</span><br><small style="color:#6B7280;">(best.pt loaded successfully)</small>'
        
    st.markdown(
        f'<div class="card" style="margin-bottom:20px; font-family:\'Plus Jakarta Sans\', sans-serif;">'
        f'<p style="margin:5px 0;"><strong>Database Connection:</strong> <span style="color:#059669; font-weight:600;">✅ Connected</span></p>'
        f'<p style="margin:5px 0;"><strong>Database File:</strong> <code style="font-size:0.8rem; background:#F1F5F9; padding:2px 5px; border-radius:4px;">database/detections.db</code></p>'
        f'<p style="margin:5px 0;"><strong>YOLO Model Status:</strong> {model_status_html}</p>'
        f'<p style="margin:5px 0; margin-bottom:0;"><strong>Database Records:</strong> <span style="font-weight:600;">{total_reports}</span></p>'
        f'</div>',
        unsafe_allow_html=True
    )
    
    # st.markdown("### 🧪 Database Simulator")
    # st.write("Since I Don't have any Road images,I'm using the controls below to seed mock data and test the charts immediately.")
    
    # seed_count = st.slider("Records to Generate", 10, 100, 50)
    
    # col_btn1, col_btn2 = st.columns(2)
    # with col_btn1:
    #     if st.button("🌱 Seed Mock Data", use_container_width=True):
    #         with st.spinner("Seeding database..."):
    #             seed_mock_data(seed_count)
    #         st.success(f"Seeded {seed_count} records!")
    #         st.rerun()
            
    # with col_btn2:
    #     if st.button("🗑️ Clear DB", use_container_width=True):
    #         db.clear_database()
    #         st.warning("All records deleted!")
    #         st.rerun()

st.divider()

# Live KPI Summary Grid
st.markdown("### 📊 Live Statistics Overview")
stat1, stat2, stat3, stat4 = st.columns(4)

with stat1:
    st.metric("Total Reports Analyzed", f"{total_reports}")
with stat2:
    st.metric("Total Defects Identified", f"{total_defects}")
with stat3:
    st.metric("High Severity Cases", f"{total_high}")
with stat4:
    st.metric("Inference Engine Mode", "Simulator" if detector.mock_mode else "YOLO GPU/CPU")