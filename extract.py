import os
from pathlib import Path
import requests
import re
import zipfile

"""
    you can test by executing python extract.py
"""

urls_to_csv_files = [
    "https://databank.worldbank.org/data/download/Population-Estimates_CSV.zip"
]


def unzip_folder(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print("Extraction complete.")


def download_data(url, save_path):
    response = requests.get(url, stream=True)

    if response.status_code == 200:
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Download complete.")
        return save_path
    else:
        print(f"Failed to download. Status Code: {response.status_code}")


def getCsvData(url):
    pattern = r'/([^/]+\.zip)$'
    match = re.search(pattern, url)
    foldername = match.group(1)
    local_save_path = Path("data", foldername)
    download_data(url, local_save_path)
    extract_to = Path("data", ".".join(foldername.split('.')[:-1]))
    unzip_folder(local_save_path, extract_to)
    os.remove(local_save_path)
    return extract_to


if __name__ == "__main__":

    for url in urls_to_csv_files:
        getCsvData(url)
        # time.sleep(5)
