# 🚀 Google Colab Fine-Tuning Guide for SmartRoad AI

Because training YOLOv8 on a CPU can overheat your system, freeze your screen, and take an extremely long time, we have designed a pipeline to offload the training to a free **T4 GPU** on Google Colab. 

This guide details how to perform the training and download your new weights back to this machine.

---

## 🛠️ Step 1: Package the Files
We have automated the packing process. Running the local script `zip_project.py` creates a lightweight zip archive called:
`smartroad_colab.zip`

This file is stored in your project root directory and contains **only** the folders necessary for training (`data/merged/`, `models/`, and `src/`), keeping the size small so it uploads to Colab in seconds.

---

## 💻 Step 2: Set Up Google Colab
1. Open [Google Colab](https://colab.research.google.com/).
2. Click **New Notebook** (or select **Upload** if you want to import a notebook directly).
3. **Change the Runtime to GPU**:
   * In the top menu, go to **Runtime** > **Change runtime type**.
   * Under *Hardware accelerator*, select **T4 GPU** (this is free).
   * Click **Save**.

---

## 📤 Step 3: Upload the Package (Choose One Option)

### Option A: Via Google Drive (Recommended - Fast & 100% Stable)
Browser-based uploads inside the Google Colab sidebar often corrupt files larger than 100MB due to network timeouts. Uploading via Google Drive is extremely fast, uses integrity checks, and is 100% stable:
1. Go to [Google Drive](https://drive.google.com/).
2. Upload the `smartroad_colab.zip` file to your drive.
3. In Google Colab, create a cell and run this to mount your drive:
   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   ```
4. Copy the file directly from your Google Drive into the Colab workspace:
   ```python
   !cp "/content/drive/MyDrive/smartroad_colab.zip" .
   print("✅ File copied from Drive successfully!")
   ```

### Option B: Direct Browser Sidebar Upload
1. On the left sidebar of the Google Colab interface, click the **Files (folder icon)** tab.
2. Drag and drop `smartroad_colab.zip` from your local computer into the files pane.
3. Wait for the upload progress ring at the bottom-left of the sidebar to complete.

---

## 🏃‍♂️ Step 4: Run the Training Steps
Create and run the following code blocks in your Colab notebook:

### Cell 1: Extract the Project Zip (Using Robust Python Extractor)
Instead of standard `!unzip` (which fails when browser upload corruption introduces extra offset bytes or padding), use Python's built-in zip library:
```python
import zipfile
import os

zip_path = "smartroad_colab.zip"
if not os.path.exists(zip_path):
    print("❌ Error: smartroad_colab.zip not found! Please check your upload path.")
else:
    print("📦 Extracting project files...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(".")
    print("✅ Project extracted successfully!")
```


### Cell 2: Install Ultralytics
```python
!pip install -q ultralytics
print("✅ YOLOv8 packages installed successfully!")
```

### Cell 3: Start Fine-Tuning
```python
!python3 src/training/fine_tune.py
```
*This script automatically detects the Colab GPU, loads your baseline models/best.pt weights, and trains for 50 epochs using our aggressive data augmentations (Mosaic, Mixup, scale, rotation, and perspective) to generalize on Google search/out-of-distribution images.*

---

## 📥 Step 5: Download and Deploy the Fine-Tuned Weights
Once training is complete, download the new weights back to your machine.

### Cell 4: Download Weights
```python
from google.colab import files
files.download('runs/train/smartroad_finetuned/weights/best.pt')
```

### Local Deployment
1. Locate the downloaded file (usually named `best.pt` or `best (1).pt` in your downloads folder).
2. Rename it exactly to `best.pt`.
3. Copy/Move it to your local project directory under `models/best.pt` (replace the existing one).
4. Restart or refresh your Streamlit dashboard and test detection on new images!
