import urllib.request
import zipfile
import os

url = "https://download.tiny.cloud/tinymce/community/tinymce_7.3.0.zip"
download_path = "tinymce.zip"
extract_path = "core/coreapp/static/coreapp/js"

print(f"Downloading TinyMCE from {url}...")
urllib.request.urlretrieve(url, download_path)
print("Download complete.")

print(f"Extracting to {extract_path}...")
with zipfile.ZipFile(download_path, 'r') as zip_ref:
    zip_ref.extractall(extract_path)
print("Extraction complete.")

if os.path.exists(download_path):
    os.remove(download_path)
    print("Cleaned up zip file.")
