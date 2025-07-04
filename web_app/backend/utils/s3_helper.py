import boto3
import os
from botocore.exceptions import ClientError
from dotenv import load_dotenv

class S3Helper:
    def __init__(self):
        load_dotenv()
        
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.bucket_name = os.getenv('AWS_BUCKET_NAME')
        self.region = os.getenv('AWS_REGION', 'ap-northeast-1')

        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region
        )

    def upload_file(self, file_path, s3_key):
        """
        Upload file to S3
        :param file_path: local file path
        :param s3_key: file path in S3
        :return: bool success status
        """
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
            print(f"Successfully uploaded {file_path} to {s3_key}")
            return True
        except ClientError as e:
            print(f"Error uploading file to S3: {e}")
            return False

    def download_file(self, s3_key, local_path):
        """
        Download file from S3
        :param s3_key: file path in S3
        :param local_path: local path to save file
        :return: bool success status
        """
        try:
            # Ensure target directory exists (only if local_path has a directory)
            dir_path = os.path.dirname(local_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
            print(f"Successfully downloaded {s3_key} to {local_path}")
            return True
        except ClientError as e:
            print(f"Error downloading file from S3: {e}")
            return False

    def file_exists(self, s3_key):
        """
        Check if file exists in S3
        :param s3_key: file path in S3
        :return: bool file existence
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError:
            return False 