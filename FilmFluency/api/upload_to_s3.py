import os
import boto3
import uuid
from django.conf import settings

def client_s3():
    session = boto3.session.Session()
    session.client('s3',
                            region_name='fra1',
                            endpoint_url='https://filmfluency.fra1.digitaloceanspaces.com',
                            aws_access_key_id=settings.SECRET_KEY,
                            aws_secret_access_key=settings.ACCESS_KEY)

def upload_to_s3(movie, video_name, filetype="mp4"):
    client = client_s3()
    file_path = os.path.join("MovieToClips", "cut_videos", movie, video_name)
    bucket_name = 'filmfluency'
    file_key = f"{movie}/{uuid.uuid4()}.{filetype}"
    client.upload_file(file_path, bucket_name, file_key,  ExtraArgs={'ACL': 'public-read'})
    os.remove(file_path)
    print(f"File {file_key} uploaded to {bucket_name} successfully.")
    
    
def serve_secure_media(file_key):
    client = client_s3()
    bucket_name = 'filmfluency'
    url = client.generate_presigned_url('get_object',
                                        Params={'Bucket': bucket_name,
                                                'Key': file_key},
                                        ExpiresIn=3600)
    return url

