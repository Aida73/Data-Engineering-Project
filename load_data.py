import boto3
from dotenv import load_dotenv
from settings.params import CREDENTIALS, BUCKET_NAME
import os


load_dotenv()


def load_bucket_data():
    s3 = boto3.client('s3', aws_access_key_id=CREDENTIALS['aws_access_key_id'],
                      aws_secret_access_key=CREDENTIALS['aws_secret_access_key'])

    response = s3.list_objects_v2(Bucket=BUCKET_NAME)

    if 'Contents' in response:
        local_directory = "s3savedData"
        os.makedirs(local_directory, exist_ok=True)

        # Download each object in the S3 bucket
        for object_info in response['Contents']:
            object_key = object_info['Key']
            local_file_path = os.path.join(
                local_directory, os.path.basename(object_key))
            s3.download_file(BUCKET_NAME, object_key, local_file_path)
            print(f"Downloaded {object_key} to {local_file_path}")
    else:
        print("No objects found in the S3 bucket.")


load_bucket_data()
