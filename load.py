import boto3
import datetime
from pathlib import Path
from settings.params import *
import os
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client('s3', aws_access_key_id=CREDENTIALS['aws_access_key_id'],
                  aws_secret_access_key=CREDENTIALS['aws_secret_access_key'])

file_path = Path(DATA_DIR, FINAL_DATASET_NAME)
if file_path.exists():
    current_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    object_key = f"{current_datetime}_{FINAL_DATASET_NAME}"

    s3.upload_file(file_path, BUCKET_NAME, object_key)
