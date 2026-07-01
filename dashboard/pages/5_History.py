import sys
from pathlib import Path
import pandas as pd
import streamlit as st
import io
import datetime
from fpdf import FPDF

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.app.database_manager import DatabaseManager
from src.app.navigation import render_sidebar
from src.app.ranking import RoadDamageRanker

st.set_page_config(
    page_title="History Logs",
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
render_sidebar("History")

st.title("📜 Detection History Logs")
st.write("Browse, search, and audit past road defect inspection reports.")

def generate_pdf_report(df_data):
    pdf = FPDF()
    pdf.add_page()
    
    # Title Block
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(30, 58, 138)  # Dark Blue (#1E3A8A)
    pdf.cell(0, 10, text="SmartRoad AI - Municipal Inspection Report", ln=True, align="C")
    
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, text=f"Generated On: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
    pdf.ln(10)
    
    # Executive Summary Metrics
    total_segments = len(df_data)
    total_potholes = int(df_data["potholes"].sum())
    total_alligator = int(df_data["alligator_cracks"].sum())
    total_long = int(df_data["longitudinal_cracks"].sum())
    total_lat = int(df_data["lateral_cracks"].sum())
    total_defects = total_potholes + total_alligator + total_long + total_lat
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 8, text="1. Executive Pavement Inspection Summary", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    
    summary_text = (
        f"This report compiles pavement inspection logs captured by the SmartRoad AI automated "
        f"vision scanning pipeline. A total of {total_segments} road segments were surveyed. "
        f"Across these segments, {total_defects} total road defects were detected. The itemized "
        f"counts are summarized below:\n"
        f"- Potholes Detected: {total_potholes}\n"
        f"- Alligator Fatigue Cracks: {total_alligator}\n"
        f"- Longitudinal Cracks: {total_long}\n"
        f"- Lateral Cracks: {total_lat}"
    )
    pdf.multi_cell(0, 6, text=summary_text)
    pdf.ln(5)
    
    # Pavement Priority Ranking Analysis
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 8, text="2. Urgent Action Items (Severity Ranked)", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    
    # Add ranking fields to dataframe
    df_data["damage_score"] = df_data.apply(
        lambda r: RoadDamageRanker.calculate_damage_score(
            r["potholes"], r["longitudinal_cracks"], r["lateral_cracks"], r["alligator_cracks"]
        ),
        axis=1
    )
    df_data["priority"] = df_data["damage_score"].apply(RoadDamageRanker.get_priority_category)
    
    critical_items = df_data[df_data["priority"] == "Critical"].sort_values(by="damage_score", ascending=False)
    
    if critical_items.empty:
        pdf.cell(0, 6, text="No critical-ranked road segments detected. Keep monitoring.", ln=True)
    else:
        pdf.set_text_color(239, 68, 68)  # Red text
        pdf.cell(0, 6, text="CRITICAL ROAD REPAIR PRIORITY ITEMS (Urgent Repair Crew Dispatch):", ln=True)
        pdf.set_text_color(0, 0, 0)
        
        for _, r in critical_items.head(5).iterrows():
            loc_str = f"GPS: {r['latitude']:.6f}, {r['longitude']:.6f}" if (pd.notna(r['latitude']) and pd.notna(r['longitude'])) else "No Coordinates"
            pdf.cell(0, 6, text=f"- ID #{r['id']} | Score: {r['damage_score']}/100 (CRITICAL) | {r['image_name']} ({loc_str})", ln=True)
            pdf.cell(0, 6, text=f"  Potholes: {int(r['potholes'])} | Alligator: {int(r['alligator_cracks'])} | Cracks: {int(r['longitudinal_cracks'] + r['lateral_cracks'])}", ln=True)
            
    pdf.ln(5)
    
    # Complete Log Table
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 8, text="3. Complete Pavement Inspection Table Logs", ln=True)
    pdf.ln(2)
    
    # Table headers
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(255, 255, 255)
    pdf.set_fill_color(30, 58, 138)
    
    pdf.cell(10, 6, text="ID", border=1, align="C", fill=True)
    pdf.cell(50, 6, text="Image / Segment Name", border=1, align="L", fill=True)
    pdf.cell(15, 6, text="Potholes", border=1, align="C", fill=True)
    pdf.cell(15, 6, text="Alligator", border=1, align="C", fill=True)
    pdf.cell(20, 6, text="Long Cracks", border=1, align="C", fill=True)
    pdf.cell(20, 6, text="Lat Cracks", border=1, align="C", fill=True)
    pdf.cell(18, 6, text="RDS Score", border=1, align="C", fill=True)
    pdf.cell(18, 6, text="Priority", border=1, align="C", fill=True)
    pdf.ln()
    
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(245, 247, 250)
    
    fill = False
    for _, r in df_data.head(30).iterrows():
        pdf.cell(10, 6, text=str(r['id']), border=1, align="C", fill=fill)
        img_name = str(r['image_name'])
        if len(img_name) > 25:
            img_name = img_name[:22] + "..."
        pdf.cell(50, 6, text=img_name, border=1, align="L", fill=fill)
        pdf.cell(15, 6, text=str(int(r['potholes'])), border=1, align="C", fill=fill)
        pdf.cell(15, 6, text=str(int(r['alligator_cracks'])), border=1, align="C", fill=fill)
        pdf.cell(20, 6, text=str(int(r['longitudinal_cracks'])), border=1, align="C", fill=fill)
        pdf.cell(20, 6, text=str(int(r['lateral_cracks'])), border=1, align="C", fill=fill)
        pdf.cell(18, 6, text=str(int(r['damage_score'])), border=1, align="C", fill=fill)
        pdf.cell(18, 6, text=str(r['priority']), border=1, align="C", fill=fill)
        pdf.ln()
        fill = not fill
        
    if len(df_data) > 30:
        pdf.set_font("Helvetica", "I", 8)
        pdf.cell(0, 6, text=f"... and {len(df_data) - 30} more records (use CSV export for full dataset)", ln=True)
        
    return bytes(pdf.output())

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
    
    # Calculate Severity Ranking
    df["damage_score"] = df.apply(
        lambda r: RoadDamageRanker.calculate_damage_score(
            r["potholes"], r["longitudinal_cracks"], r["lateral_cracks"], r["alligator_cracks"]
        ),
        axis=1
    )
    df["priority"] = df["damage_score"].apply(RoadDamageRanker.get_priority_category)
    
    # Page Filters (placed directly on the page in columns)
    col_search, col_date, col_severity = st.columns(3)
    
    with col_search:
        search_q = st.text_input("🔍 Search Image Name", "").strip()
        
    with col_date:
        min_date = df['date'].min()
        max_date = df['date'].max()
        date_range = st.date_input(
            "📅 Date Range Selection",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
    with col_severity:
        severity_filter = st.selectbox(
            "🚨 Filter by Risk Severity",
            options=["All", "High Risk Reports", "Medium Risk Reports", "Low Risk Reports"]
        )
    
    # Perform filters
    df_filtered = df
    
    if search_q:
        df_filtered = df_filtered[df_filtered["image_name"].str.contains(search_q, case=False, na=False)]
        
    if len(date_range) == 2:
        start_date, end_date = date_range
        df_filtered = df_filtered[(df_filtered['date'] >= start_date) & (df_filtered['date'] <= end_date)]
        
    if severity_filter == "High Risk Reports":
        df_filtered = df_filtered[df_filtered["high_risk"] > 0]
    elif severity_filter == "Medium Risk Reports":
        df_filtered = df_filtered[df_filtered["medium_risk"] > 0]
    elif severity_filter == "Low Risk Reports":
        df_filtered = df_filtered[df_filtered["low_risk"] > 0]
        
    # Render table
    st.markdown(f"### 📋 Log Records ({len(df_filtered)} items)")
    
    # Reports Download Center
    with st.expander("📥 Pavement Reports Download ", expanded=False):
        st.write("Export your active filtered inspection logs database to spreadsheet or PDF formats.")
        
        # Calculate RDS for the filtered logs to include in report
        df_export = df_filtered.copy()
        df_export["damage_score"] = df_export.apply(
            lambda r: RoadDamageRanker.calculate_damage_score(
                r["potholes"], r["longitudinal_cracks"], r["lateral_cracks"], r["alligator_cracks"]
            ),
            axis=1
        )
        df_export["priority"] = df_export["damage_score"].apply(RoadDamageRanker.get_priority_category)
        
        col_csv, col_excel, col_pdf = st.columns(3)
        
        # 1. CSV Download
        csv_data = df_export.to_csv(index=False).encode('utf-8')
        col_csv.download_button(
            label="📄 Export to CSV",
            data=csv_data,
            file_name=f"smartroad_inspection_report_{datetime.date.today()}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        # 2. Excel Download
        excel_buffer = io.BytesIO()
        try:
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df_export.to_excel(writer, index=False, sheet_name='Surveys')
            excel_data = excel_buffer.getvalue()
            col_excel.download_button(
                label="📊 Export to Excel",
                data=excel_data,
                file_name=f"smartroad_inspection_report_{datetime.date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except Exception as e:
            col_excel.error("Excel module error")
        
        # 3. PDF Download
        try:
            pdf_bytes = generate_pdf_report(df_export)
            col_pdf.download_button(
                label="📕 Export to PDF",
                data=pdf_bytes,
                file_name=f"smartroad_inspection_report_{datetime.date.today()}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            col_pdf.error(f"PDF generation error: {str(e)}")
            
    if df_filtered.empty:
        st.warning("⚠️ No logs matched the search criteria.")
    else:
        # Display data frame cleanly
        df_display = df_filtered.copy()
        
        # Rename columns for presentation
        df_display = df_display.rename(columns={
            "id": "Report ID",
            "image_name": "Image Name",
            "potholes": "Potholes Count",
            "longitudinal_cracks": "Longitudinal Cracks",
            "lateral_cracks": "Lateral Cracks",
            "alligator_cracks": "Alligator Cracks",
            "high_risk": "High Risk Defects",
            "medium_risk": "Medium Risk Defects",
            "low_risk": "Low Risk Defects",
            "latitude": "Latitude",
            "longitude": "Longitude",
            "damage_score": "Road Damage Score",
            "priority": "Priority Rank",
            "created_at": "Inspection Date & Time"
        })
        
        # Drop temporary 'date'
        if 'date' in df_display.columns:
            df_display = df_display.drop(columns=['date'])
            
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True
        )
        
        st.divider()
        
        # Report Detail Inspector
        st.markdown("### 🔍 Report Inspector")
        st.write("Select a specific Report ID to inspect individual defect counts and risks.")
        
        report_ids = sorted(df_filtered["id"].tolist(), reverse=True)
        selected_id = st.selectbox("Select Report ID to Inspect", options=report_ids)
        
        if selected_id:
            report_row = df_filtered[df_filtered["id"] == selected_id].iloc[0]
            
            # Print card details
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                gps_text = f"{report_row['latitude']:.6f}, {report_row['longitude']:.6f}" if pd.notna(report_row["latitude"]) else "N/A"
                st.markdown(
                    f'<div style="background:white; padding:20px; border-radius:12px; border:1px solid #E2E8F0; box-shadow:0 4px 6px rgba(0,0,0,0.02);">'
                    f'<h4 style="margin-top:0; color:#1E3A8A;">📋 General Details</h4>'
                    f'<p style="margin:5px 0;color:#374151;"><strong>Report ID:</strong> #{report_row["id"]}</p>'
                    f'<p style="margin:5px 0;color:#374151;"><strong>Image File Name:</strong> <code>{report_row["image_name"]}</code></p>'
                    f'<p style="margin:5px 0;color:#374151;"><strong>GPS Location:</strong> {gps_text}</p>'
                    f'<p style="margin:5px 0;color:#374151;"><strong>Inspected On:</strong> {report_row["created_at"]}</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                
            with col_d2:
                tot_def = report_row["potholes"] + report_row["longitudinal_cracks"] + report_row["lateral_cracks"] + report_row["alligator_cracks"]
                priority_color = "#EF4444" if report_row["priority"] == "Critical" else "#F59E0B" if report_row["priority"] == "Medium" else "#10B981"
                st.markdown(
                    f'<div style="background:white; padding:20px; border-radius:12px; border:1px solid #E2E8F0; box-shadow:0 4px 6px rgba(0,0,0,0.02);">'
                    f'<h4 style="margin-top:0; color:#1E3A8A;">🚨 Summary of Findings</h4>'
                    f'<p style="margin:5px 0;color:#374151;"><strong>Damage Score:</strong> {report_row["damage_score"]}/100 (<span style="color:{priority_color}; font-weight:bold;">{report_row["priority"]}</span>)</p>'
                    f'<p style="margin:5px 0;color:#374151;"><strong>Total Defects:</strong> {tot_def}</p>'
                    f'<p style="margin:5px 0;color:#374151;"><strong>Potholes:</strong> {report_row["potholes"]} | <strong>Alligator Cracks:</strong> {report_row["alligator_cracks"]}</p>'
                    f'<p style="margin:5px 0;color:#374151;"><strong>Longitudinal Cracks:</strong> {report_row["longitudinal_cracks"]} | <strong>Lateral Cracks:</strong> {report_row["lateral_cracks"]}</p>'
                    f'<p style="margin:5px 0;color:#374151;"><strong>Risk Levels:</strong> '
                    f'<span style="color:#EF4444; font-weight:600;">{report_row["high_risk"]} High</span> | '
                    f'<span style="color:#F59E0B; font-weight:600;">{report_row["medium_risk"]} Med</span> | '
                    f'<span style="color:#10B981; font-weight:600;">{report_row["low_risk"]} Low</span>'
                    f'</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
        
        st.divider()
        st.markdown("### ⚠️ Danger Zone")
        confirm_del = st.checkbox("Confirm I want to delete all historical logs permanently")
        if st.button("🗑️ Reset and Clear All Records", type="secondary", disabled=not confirm_del):
            db.clear_database()
            st.success("Database cleared!")
            st.rerun()
