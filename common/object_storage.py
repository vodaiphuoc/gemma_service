import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
import json
import os
from typing import Union, Tuple, Literal, Dict

from .components_settings import OBJS_SETTINGS

class Firebase_Client(object):
    def __init__(self, service_name:str) -> None:
        cred = credentials.Certificate(OBJS_SETTINGS.ACCOUNT_KEY_FILE)
        
        self.app = firebase_admin.initialize_app(
            credential = cred, 
            options = {
                'databaseURL': OBJS_SETTINGS.DB_URL, 
                'storageBucket': OBJS_SETTINGS.StorageBucketURL,
                'projectID': OBJS_SETTINGS.PROJECT_ID
            },
            name = service_name
        )

    def upload_pdf(
            self,
            user_id:int,
            file_name: str,
            file_content: bytes
        )->Dict[str, str]:

        _blob_name = "bucket_"+str(user_id)
        bucket = storage.bucket(name = _blob_name, app = self.app)

        _source_blob_name = os.path.join("CVs",file_name)
        blob = bucket.blob(_source_blob_name)
        blob.upload_from_string(file_content)
        
        return {
            "bucket_name": _blob_name,
            "blob_name": _source_blob_name
        }

    def download_blob(
            self,
            bucket_name: str,
            source_blob_name: str,
            destination_file_name: str
        )->None:
        bucket = storage.bucket(bucket_name, app= self.app)
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)
        return None