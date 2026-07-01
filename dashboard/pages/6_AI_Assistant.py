import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import datetime

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.app.database_manager import DatabaseManager
from src.app.navigation import render_sidebar

st.set_page_config(
    page_title="AI Assistant",
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
render_sidebar("AI Assistant")

st.title("💬 SmartRoad AI Assistant")
st.write("Query database statistics, estimate pavement maintenance priorities, and generate actionable road health reports.")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "👋 **Welcome to the SmartRoad AI Intelligence Assistant!**\n\n"
                "I operate offline directly on your inspection database to analyze road conditions. Here are queries you can ask me:\n"
                "* 📊 *'Give me an overall road health summary.'*\n"
                "* 🧱 *'How many potholes and cracks have we detected?'*\n"
                "* 🚨 *'Which road segments require immediate priority repairs?'*\n"
                "* 📈 *'What is our current Road Health Index (RHI)?'* \n"
                "* 📜 *'Show recent inspection reports.'*"
            )
        }
    ]

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# SQL-Aware Parsing Engine
def generate_response(query):
    query = query.lower().strip()
    db = DatabaseManager()
    rows = db.get_all_detections()
    
    if not rows:
        return "💡 The database is currently empty. Please seed simulated data on the **Home Portal** or run a scan in the **Detection Interface** so I can analyze statistics for you!"

    # Create DataFrame for calculations
    columns = [
        "id", "image_name", "potholes", "longitudinal_cracks", 
        "lateral_cracks", "alligator_cracks", "high_risk", 
        "medium_risk", "low_risk", "latitude", "longitude", "created_at"
    ]
    df = pd.DataFrame(rows, columns=columns)
    
    total_scans = len(df)
    potholes = int(df["potholes"].sum())
    long_cracks = int(df["longitudinal_cracks"].sum())
    lat_cracks = int(df["lateral_cracks"].sum())
    alli_cracks = int(df["alligator_cracks"].sum())
    total_defects = potholes + long_cracks + lat_cracks + alli_cracks
    
    high = int(df["high_risk"].sum())
    medium = int(df["medium_risk"].sum())
    low = int(df["low_risk"].sum())

    # --- Greeting or Help ---
    if any(k in query for k in ["hello", "hi", "hey", "help", "greetings"]):
        return (
            "Hello! I am your offline road analytics companion. I can run direct computations on your "
            "database. Try asking:\n"
            "1. *'potholes'* or *'defects'* (for counts)\n"
            "2. *'priority'* or *'repair first'* (for priority lists)\n"
            "3. *'health'* or *'status'* (for health index)\n"
            "4. *'summary'* or *'overview'* (for a complete report)"
        )

    # --- Potholes and defects details ---
    elif any(k in query for k in ["pothole", "defect", "crack", "count"]):
        return (
            f"### 🧱 Defect Census Summary\n\n"
            f"Across all **{total_scans}** registered scans, the AI has identified a total of **{total_defects}** pavement defects:\n"
            f"* 🧱 **Potholes**: `{potholes}`\n"
            f"* 📈 **Longitudinal Cracks**: `{long_cracks}`\n"
            f"* 📉 **Lateral Cracks**: `{lat_cracks}`\n"
            f"* 🐊 **Alligator Cracks**: `{alli_cracks}`\n\n"
            f"*Average defect density: **{total_defects/total_scans:.2f}** defects per inspection.*"
        )

    # --- Priority list ---
    elif any(k in query for k in ["priority", "repair first", "critical", "action", "worst", "schedule"]):
        high_risk_df = df[df["high_risk"] > 0].sort_values(by=["high_risk", "medium_risk"], ascending=False).head(5)
        
        if high_risk_df.empty:
            return "✅ **No critical action items.** None of the recorded scans contain high-severity defects. All roads look in monitorable condition."
        
        response = "### 🚨 Top Priority Road Repair Recommendations\n\n"
        response += "Here is the prioritized maintenance list based on high-severity defect count and density:\n\n"
        
        for idx, r in high_risk_df.iterrows():
            loc_str = f" (Lat/Lon: `{r['latitude']:.4f}, {r['longitude']:.4f}`)" if pd.notna(r['latitude']) else ""
            response += (
                f"1. 🔴 **Report #{r['id']}** - Image: `{r['image_name']}`{loc_str}\n"
                f"   * **High Risk (Critical)**: `{r['high_risk']}`\n"
                f"   * **Medium Risk (Alert)**: `{r['medium_risk']}`\n"
                f"   * *Recommendation: Immediate pavement patching and structural crack sealing.* \n\n"
            )
        return response

    # --- Road Health Index ---
    elif any(k in query for k in ["health", "status", "index", "condition"]):
        # Deduct health points for defects, weighting potholes & alligator cracks heavier
        deduction = ((potholes * 6 + alli_cracks * 5 + long_cracks * 3 + lat_cracks * 3) / total_scans) * 5 if total_scans > 0 else 0
        health_index = max(100.0 - deduction, 0.0)
        
        rating = ""
        color = ""
        if health_index >= 90:
            rating = "Excellent (Pavements show minor normal wear)"
            color = "🟢"
        elif health_index >= 75:
            rating = "Good (Minor cosmetic maintenance suggested)"
            color = "🟡"
        elif health_index >= 55:
            rating = "Fair (Action required to prevent alligator cracking extension)"
            color = "🟠"
        else:
            rating = "Critical (Immediate repaving of clusters required)"
            color = "🔴"
            
        return (
            f"### 📈 SmartRoad Health Assessment\n\n"
            f"Our calculated **SmartRoad Health Index (SRHI)** is: **{health_index:.1f}%**\n\n"
            f"**Current Status:** {color} **{rating}**\n\n"
            f"*Metrics factored:* \n"
            f"* High-severity defects: `{high}`\n"
            f"* Total potholes: `{potholes}`\n"
            f"* Total alligator cracks: `{alli_cracks}`"
        )

    # --- Summary Report ---
    elif any(k in query for k in ["summary", "overview", "report", "stats", "all"]):
        # Deduct health points for defects, weighting potholes & alligator cracks heavier
        deduction = ((potholes * 6 + alli_cracks * 5 + long_cracks * 3 + lat_cracks * 3) / total_scans) * 5 if total_scans > 0 else 0
        health_index = max(100.0 - deduction, 0.0)
        
        return (
            f"### 📊 Comprehensive Municipal Defect Report\n\n"
            f"**Reporting Period:** Year-to-Date\n"
            f"**Total Scan Reports:** `{total_scans}`\n"
            f"**Road Health Index:** `{health_index:.1f}%`\n"
            f"**Total Defects Detected:** `{total_defects}`\n\n"
            f"| Defect Type | Total Count | Average/Scan |\n"
            f"|---|---|---|\n"
            f"| 🧱 Potholes | {potholes} | {potholes/total_scans:.2f} |\n"
            f"| 📈 Longitudinal Cracks | {long_cracks} | {long_cracks/total_scans:.2f} |\n"
            f"| 📉 Lateral Cracks | {lat_cracks} | {lat_cracks/total_scans:.2f} |\n"
            f"| 🐊 Alligator Cracks | {alli_cracks} | {alli_cracks/total_scans:.2f} |\n\n"
            f"**Severity Summary:**\n"
            f"* 🔴 High Severity: `{high}` (Requires immediate attention)\n"
            f"* 🟡 Medium Severity: `{medium}` (Monitor / scheduled maintenance)\n"
            f"* 🟢 Low Severity: `{low}` (Routine inspection)"
        )

    # --- Recent Inspections ---
    elif any(k in query for k in ["recent", "latest", "inspect", "scans"]):
        response = "### 📜 Recent Road Inspections\n\n"
        recent_df = df.head(5)
        for idx, r in recent_df.iterrows():
            loc_str = f" (Coords: `{r['latitude']:.4f}, {r['longitude']:.4f}`)" if pd.notna(r['latitude']) else ""
            response += (
                f"* **Scanned at `{r['created_at']}`** | ID: `#{r['id']}`\n"
                f"  * Image: `{r['image_name']}`{loc_str}\n"
                f"  * Detections: `{r['potholes'] + r['longitudinal_cracks'] + r['lateral_cracks'] + r['alligator_cracks']}` total defects\n"
            )
        return response

    # --- Default ---
    else:
        return (
            "I could not understand that query. Since I run offline on rules-based semantic patterns, please ask about: \n"
            "* **'summary'** (for complete reports)\n"
            "* **'potholes'** or **'cracks'** (for counts)\n"
            "* **'health'** (for road index score)\n"
            "* **'priority'** (for repair lists)\n"
            "* **'recent'** (for latest scans)"
        )

# User Chat Input
if prompt := st.chat_input("Ask about road health index, defect counts, or priority repairs..."):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Generate response
    response_text = generate_response(prompt)
    
    # Add assistant response to state
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.markdown(response_text)
