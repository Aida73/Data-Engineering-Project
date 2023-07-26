import boto3

import os
from dotenv import load_dotenv

load_dotenv()

aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']

s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                  aws_secret_access_key=aws_secret_access_key)

bucket_name = 'worldbankdatabucket'
file_path = 'data/final_dataset.csv'
object_key = 'final_dataset.csv'

s3.upload_file(file_path, bucket_name, object_key)



