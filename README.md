# 🛣️ SmartRoad-AI: Intelligent Pothole \& Defect Detection System

SmartRoad-AI is a high-performance computer vision and municipal reporting dashboard designed to detect, track, rank, and report structural road damage (potholes, longitudinal cracks, lateral cracks, and alligator fatigue cracking) from inspection images and videos.

Built using **Streamlit**, **YOLOv8**, **OpenCV**, and **SQLite**, it provides a complete municipal survey solution with prioritized action plans and automated PDF inspection reports.

---

## ✨ Key Features

1. **AI-Powered Batch Scan Portal**: Upload multiple road images and video files simultaneously. Process frames in optimized pipelines with dynamic confidence sliders (`0.00` to `1.00`).
2. **Pavement Severity Ranking Algorithm**: Computes a mathematical **Road Damage Score (RDS)** from `0` to `100` based on defect threat parameters to categorize road segments as *Low*, *Medium*, or *Critical* priority.
3. **Urgent Intervention Executive Dashboard**: Displays ranked KPI metrics, severity distribution charts, and the top 5 urgent repair dispatch locations featuring exact GPS satellite map quick-links.
4. **Deep-Dive Trend Analytics**: Renders high-resolution trend timelines (auto-scaling to chronological inspection timestamps for single-day scans), stacked risk distributions, and color-coded interactive Google Satellite Map pins.
5. **Municipal Reports Download Center**:
   * **CSV / Excel Export**: One-click download of the active filtered survey log.
   * **Automated PDF Generator**: Prints official municipal surveys complete with defect totals, prioritized repair orders, and clean tabular logs.
6. **SQL-Aware AI Chatbot Assistant**: An offline natural-language chatbot that translates user queries into direct database calculations to compute network health statistics or suggest repairs.

---

## 📊 Pavement Severity Ranking Formula (RDS)

The **Road Damage Score (RDS)** is calculated out of 100 based on standard engineering defect weights:
* **Alligator fatigue cracks** (indicates base structure failure): `20 pts` each
* **Potholes** (high-impact safety hazard): `15 pts` each
* **Longitudinal & Lateral Cracks**: `5 pts` each

$$\text{RDS} = \min(100, \, (15 \times \text{Potholes}) + (20 \times \text{Alligator}) + (5 \times \text{Longitudinal}) + (5 \times \text{Lateral}))$$

### Priority Categorization:
* 🚨 **Critical Priority (51–100 RDS)**: Urgent maintenance dispatch required.
* ⚠️ **Medium Priority (21–50 RDS)**: Scheduled intervention needed.
* 🟢 **Low Priority (0–20 RDS)**: Standard routine maintenance.

---

## 📂 Project Directory Structure

```
SmartRoad-AI/
├── .streamlit/           # Streamlit app layout configuration
├── dashboard/            # Front-End Web Application
│   ├── app.py            # Home / Navigation Hub
│   ├── pages/            # Dashboard page modules (1-6)
│   └── styles/           # Custom CSS stylesheets
├── database/             # Inspection SQLite database file
├── data/                 # Sample videos and image assets for testing
├── models/               # Pre-trained YOLOv8 weights (.pt files)
├── src/                  # Back-End Logic & AI training modules
│   ├── app/              # Navigation, database, detector, and ranking modules
│   └── training/         # Custom YOLOv8 training/fine-tuning scripts
├── .gitignore            # Tells Git which files to ignore
├── requirements.txt      # Python libraries list
└── README.md             # Project documentation (this file)
```

---

## 🚀 Installation & Setup

Follow these simple steps to set up and run the dashboard locally:

### Prerequisites
Make sure you have **Python 3.8+** installed.

### 1. Clone the Repository
```bash
git clone https://github.com/Vinodgm2106/SmartRoad-AI.git
cd SmartRoad-AI
```

### 2. Set Up a Virtual Environment
* **Linux/macOS**:
  ```bash
  python -m venv venv
  source venv/bin/activate
  ```
* **Windows**:
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit Dashboard
```bash
streamlit run dashboard/app.py
```

---

## 🛠️ Model Training (Google Colab)
If you wish to fine-tune the model weights on custom datasets, check the [COLLAB_GUIDE.md](COLLAB_GUIDE.md) and use the [zip_project.py](zip_project.py) utility to prepare your files for cloud GPU processing.
