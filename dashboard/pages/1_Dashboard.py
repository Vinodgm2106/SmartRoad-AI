import streamlit as st
from pathlib import Path
import sys
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.app.database_manager import DatabaseManager
from src.app.navigation import render_sidebar
from src.app.ranking import RoadDamageRanker

st.set_page_config(
    page_title="Executive Dashboard",
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
render_sidebar("Dashboard")

st.title("📊 Executive Dashboard")

db = DatabaseManager()
rows = db.get_all_detections()

if not rows:
    st.info("💡 No inspection records found in the database. Please go to the **Home** page to seed simulated data or upload images on the **Detection** page.")
else:
    # Build dataframe
    columns = [
        "id", "image_name", "potholes", "longitudinal_cracks", 
        "lateral_cracks", "alligator_cracks", "high_risk", 
        "medium_risk", "low_risk", "latitude", "longitude", "created_at"
    ]
    df = pd.DataFrame(rows, columns=columns)
    
    total_images = len(df)
    total_potholes = df["potholes"].sum()
    total_long = df["longitudinal_cracks"].sum()
    total_lat = df["lateral_cracks"].sum()
    total_alligator = df["alligator_cracks"].sum()
    total_defects = total_potholes + total_long + total_lat + total_alligator
    
    total_high = df["high_risk"].sum()
    total_medium = df["medium_risk"].sum()
    total_low = df["low_risk"].sum()
    
    avg_defects = total_defects / total_images if total_images > 0 else 0
    high_risk_ratio = (total_high / total_defects * 100) if total_defects > 0 else 0
    
    # KPI metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Images Processed", f"{total_images}")
    with col2:
        st.metric("Total Defects Found", f"{total_defects}")
    with col3:
        st.metric("Avg Defects / Image", f"{avg_defects:.1f}")
    with col4:
        st.metric("Critical High Risk", f"{total_high}")
    with col5:
        st.metric("High Risk Ratio", f"{high_risk_ratio:.1f}%")
        
    st.write("")
    
    # Charts columns
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("### 📋 Defect Count by Category")
        defect_data = pd.DataFrame({
            "Defect Category": ["Pothole", "Longitudinal Crack", "Lateral Crack", "Alligator Crack"],
            "Count": [total_potholes, total_long, total_lat, total_alligator]
        })
        fig_bar = px.bar(
            defect_data,
            x="Defect Category",
            y="Count",
            color="Defect Category",
            color_discrete_map={
                "Pothole": "#3B82F6",
                "Longitudinal Crack": "#10B981",
                "Lateral Crack": "#F59E0B",
                "Alligator Crack": "#EF4444"
            },
            text_auto=True
        )
        fig_bar.update_layout(
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=10, b=20),
            height=350
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with chart_col2:
        st.markdown("### 🚨 Severity Risk Distribution")
        severity_data = pd.DataFrame({
            "Risk Severity": ["High Risk", "Medium Risk", "Low Risk"],
            "Count": [total_high, total_medium, total_low]
        })
        fig_pie = px.pie(
            severity_data,
            values="Count",
            names="Risk Severity",
            hole=0.4,
            color="Risk Severity",
            color_discrete_map={
                "High Risk": "#EF4444",
                "Medium Risk": "#F59E0B",
                "Low Risk": "#10B981"
            }
        )
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=10, b=20),
            height=350
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
    # Defect Location Map
    st.markdown("### 🗺️ Geographical Defect Location Map (Satellite View)")
    map_df = df.dropna(subset=["latitude", "longitude"])
    if not map_df.empty:
        # Center around mean coordinates
        center_lat = map_df["latitude"].mean()
        center_lon = map_df["longitude"].mean()
        
        # Create Folium Map with Google Hybrid Satellite View
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=12,
            tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
            attr="Google",
            attribution_control=False
        )
        
        # Add color-coded pins based on severity
        for _, r in map_df.iterrows():
            total_defect = int(r["potholes"] + r["longitudinal_cracks"] + r["lateral_cracks"] + r["alligator_cracks"])
            popup_html = f"""
            <div style="font-family: sans-serif; font-size: 12px; width: 180px; color: black !important;">
                <b style="color: #1e3a8a;">Report ID #{int(r['id'])}</b><br>
                🛣️ <code>{r['image_name']}</code><br><br>
                🧱 Potholes: <b>{int(r['potholes'])}</b><br>
                📈 Long Cracks: <b>{int(r['longitudinal_cracks'])}</b><br>
                📉 Lat Cracks: <b>{int(r['lateral_cracks'])}</b><br>
                🐊 Alligator Cracks: <b>{int(r['alligator_cracks'])}</b><br><br>
                🚨 Total Defects: <b>{total_defect}</b>
            </div>
            """
            color = "red" if r["high_risk"] > 0 else "orange" if r["medium_risk"] > 0 else "blue"
            folium.Marker(
                location=[r["latitude"], r["longitude"]],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"Report #{int(r['id'])} - {total_defect} defects",
                icon=folium.Icon(color=color, icon="exclamation-sign")
            ).add_to(m)
            
        st_folium(m, use_container_width=True, height=450, key="dashboard_satellite_map")
    else:
        st.info("💡 No geographical coordinates available for mapping yet. Seed simulated data or analyze images with GPS tagging to display them here.")
        
    st.divider()
    
    # Priority Alerts
    st.markdown("### 🚨 Urgent Pavement Action Items (Severity Ranked)")
    
    # Compute RDS for each row
    df["damage_score"] = df.apply(
        lambda r: RoadDamageRanker.calculate_damage_score(
            potholes=r["potholes"],
            long_cracks=r["longitudinal_cracks"],
            lat_cracks=r["lateral_cracks"],
            alligator_cracks=r["alligator_cracks"]
        ),
        axis=1
    )
    df["priority"] = df["damage_score"].apply(RoadDamageRanker.get_priority_category)
    
    # Sort descending
    ranked_reports = df.sort_values(by="damage_score", ascending=False)
    critical_reports = ranked_reports[ranked_reports["priority"] == "Critical"].head(5)
    
    if critical_reports.empty:
        st.success("✅ No critical-ranked road segments requiring immediate crew dispatch.")
        # Fallback to Medium priority
        medium_reports = ranked_reports[ranked_reports["priority"] == "Medium"].head(3)
        if not medium_reports.empty:
            st.markdown("#### ⚠️ Medium Priority Action Items")
            for idx, row in medium_reports.iterrows():
                gps_str = f" | GPS: **{row['latitude']:.6f}, {row['longitude']:.6f}**" if (pd.notna(row['latitude']) and pd.notna(row['longitude'])) else ""
                st.warning(
                    f"⚠️ **Medium Priority ID #{row['id']}** | `{row['image_name']}`{gps_str}\n\n"
                    f"* **Road Damage Score**: `{row['damage_score']}/100` (Medium Priority)\n"
                    f"* **Defects Count**: Potholes: **{int(row['potholes'])}** | Alligator: **{int(row['alligator_cracks'])}** | Long Cracks: **{int(row['longitudinal_cracks'])}** | Lat Cracks: **{int(row['lateral_cracks'])}**"
                )
    else:
        for idx, row in critical_reports.iterrows():
            gps_str = f" | GPS: **{row['latitude']:.6f}, {row['longitude']:.6f}**" if (pd.notna(row['latitude']) and pd.notna(row['longitude'])) else ""
            st.error(
                f"🚨 **Critical Segment ID #{row['id']}** | `{row['image_name']}`{gps_str}\n\n"
                f"* **Road Damage Score**: `{row['damage_score']}/100` (CRITICAL priority)\n"
                f"* **Defects Count**: Potholes: **{int(row['potholes'])}** | Alligator: **{int(row['alligator_cracks'])}** | Long Cracks: **{int(row['longitudinal_cracks'])}** | Lat Cracks: **{int(row['lateral_cracks'])}**\n"
                f"* **Survey Date**: {row['created_at']}"
            )
