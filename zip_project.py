import os
import zipfile
from pathlib import Path

def create_colab_zip():
    project_root = Path(__file__).resolve().parent
    zip_filename = "smartroad_colab.zip"
    zip_path = project_root / zip_filename
    
    # Folders required for training
    required_folders = ["data/merged", "models", "src"]
    
    print("📦 Starting to package project for Google Colab...")
    
    # Remove existing zip if it exists
    if zip_path.exists():
        os.remove(zip_path)
        print(f"🗑️ Cleaned up existing {zip_filename}")
        
    count = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for folder_rel in required_folders:
            folder_path = project_root / folder_rel
            if not folder_path.exists():
                print(f"⚠️ Warning: Folder {folder_rel} does not exist at {folder_path}!")
                continue
                
            print(f"📁 Packaging {folder_rel}...")
            for root, dirs, files in os.walk(folder_path):
                # Exclude __pycache__ folders
                if "__pycache__" in dirs:
                    dirs.remove("__pycache__")
                    
                for file in files:
                    file_path = Path(root) / file
                    # Avoid adding massive runs/ logs if any somehow nested
                    if "runs" in file_path.parts:
                        continue
                    
                    archive_name = file_path.relative_to(project_root)
                    zipf.write(file_path, archive_name)
                    count += 1
                    
    print(f"\n🎉 Packaging complete! Created: {zip_path.name} (Contains {count} files)")
    print("👉 File size: {:.2f} MB".format(zip_path.stat().st_size / (1024 * 1024)))
    print("➡️ Ready to upload to Google Colab!")

if __name__ == "__main__":
    create_colab_zip()
