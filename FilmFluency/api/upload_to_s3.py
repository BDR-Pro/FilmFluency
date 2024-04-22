import os
import boto3
import uuid
from django.conf import settings
from botocore.client import Config

def client_s3():
    try:
        print("Connecting to S3...")
                
        
        SECRET_KEY = settings.SECRET_KEY
        ACCESS_KEY = settings.ACCESS_KEY
        # Create a session using DigitalOcean Spaces or AWS credentials
        session = boto3.session.Session()
        s3_client = session.client(
            's3',
            region_name='fra1',  # Adjust region if necessary
            endpoint_url='https://filmfluency.fra1.digitaloceanspaces.com',  # Adjust endpoint URL if necessary
            aws_access_key_id=ACCESS_KEY,  # Use dedicated settings for AWS access key
            aws_secret_access_key=SECRET_KEY,  # Use dedicated settings for AWS secret key
            config=Config(signature_version='s3v4')
        )
        
        # Test the connection
        response = s3_client.list_buckets()  # Ensure this method is called on the client
        print("Buckets:", response)  # Print the list of buckets

    except Exception as e:
        print(f"Failed to connect to S3: {e}")
        raise Exception("Could not connect to S3") from e  # Raise the original exception as well to provide stack trace

    return s3_client


def upload_to_s3(movie, video_name, filetype="mp4"):
    client = client_s3()
    file_path = os.path.join("MovieToClips", "cut_videos", movie, video_name)
    bucket_name = 'filmfluency'
    file_key = f"{movie}/{uuid.uuid4()}.{filetype}"
    client.upload_file(file_path, bucket_name, file_key,  ExtraArgs={'ACL': 'public-read'})
    os.remove(file_path)
    print(f"File {file_key} uploaded to {bucket_name} successfully.")
    return file_key
    
    
def serve_secure_media(file_key):
    client = client_s3()
    bucket_name = 'filmfluency'
    url = client.generate_presigned_url('get_object',
                                        Params={'Bucket': bucket_name,
                                                'Key': file_key},
                                        ExpiresIn=3600)
    return url

