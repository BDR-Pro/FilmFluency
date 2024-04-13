import oss2
import os
from dotenv import load_dotenv

load_dotenv()

def get_oss_bucket():
    auth = oss2.Auth(os.getenv('OSS_ACCESS_KEY_ID'), os.getenv('OSS_ACCESS_KEY_SECRET'))
    bucket = oss2.Bucket(auth, 'Your-OSS-Endpoint', 'Your-Bucket-Name')
    return bucket
