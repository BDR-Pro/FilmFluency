import boto3
from django.conf import settings
import random
from botocore.client import Config
from urllib.parse import unquote

from boto3.s3.transfer import S3Transfer
from botocore.exceptions import ClientError
def client_s3():
    try:
        print("Connecting to S3...")
                
        
        SECRET_KEY = settings.SECRET_KEY
        ACCESS_KEY = settings.ACCESS_KEY
        # Create a session using DigitalOcean Spaces or AWS credentials
        print("Creating session...s3")
        
        session = boto3.session.Session()
        s3_client = session.client(
            's3',
            region_name='fra1',  # Adjust region if necessary
            endpoint_url='https://fra1.digitaloceanspaces.com',  # Adjust endpoint URL if necessary
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


def upload_to_s3(file_name,key=""):
    key = key + file_name if not key else key
    print("Uploading file to S3...")
    bucket = 'filmfluency'
    client = client_s3()
    transfer = S3Transfer(client)
    try:
        transfer.upload_file(file_name, bucket, key, extra_args={'ACL': 'public-read'})
        print("File uploaded successfully")
        return True
    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        return False


def hex_decode(encoded_string):
    # Convert the hexadecimal representation back to the original string
    decoded_string = bytes.fromhex(encoded_string).decode('utf-8')
    return decoded_string


def serve_secure_media(file_key):
    client = client_s3()
    bucket_name = 'filmfluency'
    unquoted_file_key = hex_decode(unquote(file_key))
    print(f"Unqouted file key: {unquoted_file_key}")
    # IF the file does not exist, return None
    try:
        client.head_object(Bucket=bucket_name, Key=unquoted_file_key)
    except ClientError as e:
        print(f"Error getting file: {e}")
        return None
    
    url = client.generate_presigned_url('get_object',
                                        Params={'Bucket': bucket_name,
                                                'Key': unquoted_file_key},
                                        ExpiresIn=3600)
    
    return url


def get_random_file(folder_path="avatars/"):
    # Setup S3 client
    s3_client = client_s3()
    response = s3_client.list_objects_v2(Bucket="filmfluency", Prefix=folder_path)

    # Extract file names
    files = [file['Key'] for file in response.get('Contents', []) if '/' not in file['Key'][len(folder_path):]]

    # Choose a random file
    if files:
        random_file = random.choice(files)
        print("Randomly selected file:", random_file)
        return random_file
    else:
        print("No files found in the specified folder.")
        return None
    
def download_from_s3(key, extension=""):
    client = client_s3()
    bucket_name = 'filmfluency'
    file_name = key.split('/')[-1]
    if extension:
        file_name += extension
    try:
        client.download_file(bucket_name, key, file_name)
        print("Download successful.")
        return file_name
    except ClientError as e:
        print(f"Error downloading file: {e}")
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise