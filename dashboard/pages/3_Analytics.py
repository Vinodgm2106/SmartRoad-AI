import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
import folium
from streamlit_folium import st_folium

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.app.database_manager import DatabaseManager
from src.app.analytics import Analytics
from src.app.navigation import render_sidebar

st.set_page_config(
    page_title="Deep Analytics",
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
render_sidebar("Analytics")

st.title("📊 Deep-Dive Analytics")
st.write("Track defect trend cycles, risk composition over time, and inspect geometric area metrics.")

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
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['date'] = df['created_at'].dt.date
    
    # Filters (placed directly on the page)
    min_date = df['date'].min()
    max_date = df['date'].max()
    
    col_filter, _ = st.columns([1, 2])
    with col_filter:
        date_range = st.date_input(
            "📅 Select Date Range Selection",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    
    # Perform filtering
    if len(date_range) == 2:
        start_date, end_date = date_range
        df_filtered = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    else:
        df_filtered = df
        
    if df_filtered.empty:
        st.warning("⚠️ No data matches the selected date range.")
    else:
        # Aggregated stats
        total_reports = len(df_filtered)
        total_potholes = df_filtered["potholes"].sum()
        total_long = df_filtered["longitudinal_cracks"].sum()
        total_lat = df_filtered["lateral_cracks"].sum()
        total_alligator = df_filtered["alligator_cracks"].sum()
        total_defects = total_potholes + total_long + total_lat + total_alligator
        
        # 1. Defect Trend Over Time
        st.markdown("### 📈 Damage Frequency Trend Over Time")
        
        # Sort chronologically
        df_trend = df_filtered.sort_values(by="created_at").copy()
        num_unique_dates = len(df_trend["date"].unique())
        
        if num_unique_dates > 1:
            # Multiple days: group daily
            df_trend["date_str"] = df_trend["date"].astype(str)
            df_chart_data = df_trend.groupby("date_str")[['potholes', 'longitudinal_cracks', 'lateral_cracks', 'alligator_cracks']].sum().reset_index()
            x_col = "date_str"
            x_title = "Date"
        else:
            # Single day: show individual logs chronologically to draw trend lines with highs/lows
            df_trend["time_str"] = df_trend["created_at"].dt.strftime("%H:%M:%S")
            df_trend["time_label"] = df_trend.apply(
                lambda r: f"{r['time_str']} (ID #{r['id']})", axis=1
            )
            df_chart_data = df_trend
            x_col = "time_label"
            x_title = "Inspection Time (ID)"
            
        daily_melted = df_chart_data.melt(
            id_vars=[x_col],
            value_vars=['potholes', 'longitudinal_cracks', 'lateral_cracks', 'alligator_cracks'],
            var_name='Defect Type',
            value_name='Count'
        )
        
        daily_melted['Defect Type'] = daily_melted['Defect Type'].replace({
            'potholes': 'Pothole',
            'longitudinal_cracks': 'Longitudinal Crack',
            'lateral_cracks': 'Lateral Crack',
            'alligator_cracks': 'Alligator Crack'
        })
        
        fig_trend = px.line(
            daily_melted,
            x=x_col,
            y='Count',
            color='Defect Type',
            markers=True,
            color_discrete_map={
                "Pothole": "#3B82F6",
                "Longitudinal Crack": "#10B981",
                "Lateral Crack": "#F59E0B",
                "Alligator Crack": "#EF4444"
            }
        )
        fig_trend.update_layout(
            xaxis_title=x_title,
            yaxis_title="Detections Count",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=10, b=20),
            height=380
        )
        fig_trend.update_xaxes(type='category', showgrid=True, gridcolor='#E2E8F0')
        fig_trend.update_yaxes(showgrid=True, gridcolor='#E2E8F0')
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # 2. Risk Level Composition Over Time (Stacked Bar Chart)
        st.divider()
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown("### 🧬 Stacked Daily Risk Levels")
            
            if num_unique_dates > 1:
                daily_risk = df_trend.groupby('date_str')[['high_risk', 'medium_risk', 'low_risk']].sum().reset_index()
                x_col_risk = "date_str"
                x_title_risk = "Date"
            else:
                daily_risk = df_trend
                x_col_risk = "time_label"
                x_title_risk = "Inspection Time (ID)"
                
            daily_risk_melted = daily_risk.melt(
                id_vars=[x_col_risk],
                value_vars=['high_risk', 'medium_risk', 'low_risk'],
                var_name='Risk Severity',
                value_name='Count'
            )
            daily_risk_melted['Risk Severity'] = daily_risk_melted['Risk Severity'].replace({
                'high_risk': 'High Risk',
                'medium_risk': 'Medium Risk',
                'low_risk': 'Low Risk'
            })
            
            fig_risk = px.bar(
                daily_risk_melted,
                x=x_col_risk,
                y='Count',
                color='Risk Severity',
                color_discrete_map={
                    "High Risk": "#EF4444",
                    "Medium Risk": "#F59E0B",
                    "Low Risk": "#10B981"
                },
                barmode='stack'
            )
            fig_risk.update_layout(
                xaxis_title=x_title_risk,
                yaxis_title="Total Risks Counts",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=10, b=20),
                height=350
            )
            fig_risk.update_xaxes(type='category')
            st.plotly_chart(fig_risk, use_container_width=True)
            
        with chart_col2:
            st.markdown("### 📊 Average Damage Densities")
            defect_totals = pd.DataFrame({
                "Category": ["Potholes", "Longitudinal", "Lateral", "Alligator"],
                "Average Per Image": [
                    total_potholes / total_reports,
                    total_long / total_reports,
                    total_lat / total_reports,
                    total_alligator / total_reports
                ]
            })
            fig_avg = px.bar(
                defect_totals,
                x="Category",
                y="Average Per Image",
                color="Category",
                color_discrete_sequence=px.colors.qualitative.Pastel,
                text_auto='.2f'
            )
            fig_avg.update_layout(
                showlegend=False,
                xaxis_title="Defect Category",
                yaxis_title="Avg Detections/Image",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=10, b=20),
                height=350
            )
            st.plotly_chart(fig_avg, use_container_width=True)
            
        # 3. Defect Location Analysis
        st.divider()
        st.markdown("### 🗺️ Geographical Defect Location Map (Satellite View - Filtered)")
        map_df = df_filtered.dropna(subset=["latitude", "longitude"])
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
                
            st_folium(m, use_container_width=True, height=450, key="analytics_satellite_map")
        else:
            st.info("💡 No geographical coordinates available for mapping in this date range.")