import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List

from azure.storage.blob import BlobServiceClient
from azure.storage.blob import BlobClient
from azure.storage.blob import generate_blob_sas
from azure.storage.blob import generate_container_sas
from azure.storage.blob import ContentSettings

from dotenv import load_dotenv


class AzureBlobStorageClient:

    def __init__(self, account_name: str = "", account_key: str = "", container_name: str = ""):

        load_dotenv()

        self.account_name: str = os.getenv('BLOB_STORAGE_ACCOUNT_NAME', account_name)
        self.account_key: str = os.getenv('BLOB_STORAGE_ACCOUNT_KEY', account_key)
        self.connect_str : str = f"DefaultEndpointsProtocol=https;AccountName={self.account_name};AccountKey={self.account_key};EndpointSuffix=core.windows.net"
        self.container_name = os.getenv('BLOB_STORAGE_CONTAINER_NAME', container_name)
        self.blob_service_client : BlobServiceClient = BlobServiceClient.from_connection_string(self.connect_str)
        
    def delete_file(self, file_name, container_name: Optional[str] = None):
        if container_name is None:
            container_name = self.container_name
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=file_name)
        blob_client.delete_blob(delete_snapshots="include")
    
    def upload_file(self, bytes_data, file_name: str, container_name: Optional[str] = None, content_type: Optional[str] = 'application/pdf', metadata: Optional[Dict] = {}):
        if not container_name:
            container_name = self.container_name

        #Create container if not exists
        if not self.blob_service_client.get_container_client(container_name).exists():
            self.blob_service_client.create_container(container_name)

        # Create a blob client using the local file name as the name for the blob
        blob_client = self.blob_service_client.get_blob_client(container=container_name,
                                                               blob=file_name)
        # Upload the created file
        blob_client.upload_blob(bytes_data, 
                                overwrite=True, 
                                content_settings=ContentSettings(content_type=content_type),
                                metadata=metadata)

        # Generate a SAS URL to the blob and return it
        return blob_client.url + '?' + generate_blob_sas(self.account_name, 
                                                         container_name, 
                                                         file_name,
                                                         account_key=self.account_key,  
                                                         permission="r", 
                                                         expiry=datetime.now() + timedelta(hours=3))


    def get_container_files(self, container_name: Optional[str] = None, folder_name: Optional[str] = None, full_path: bool = True):
        if container_name is None:
            container_name = self.container_name
        if folder_name is None:
            folder_name = ''
        container_client = self.blob_service_client.get_container_client(container_name)
        blob_list = container_client.list_blobs(include='metadata')
        files = [blob['name'] for blob in blob_list]
        if folder_name:
            files = [file for file in files if file.startswith(os.path.join(folder_name, '').replace("\\","/"))]
        # If full_path is True, get only the file name (without any folder or full path)
        if not full_path:
            files = [os.path.basename(file) for file in files]
        return files
            
    def get_container_sas(self):
        # Generate a SAS URL to the container and return it
        return "?" + generate_container_sas(account_name= self.account_name, container_name= self.container_name,account_key=self.account_key,  permission="r", expiry=datetime.utcnow() + timedelta(hours=1))

    def get_blob_sas(self, file_name):
        # Generate a SAS URL to the blob and return it
        return f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{file_name}" + "?" + generate_blob_sas(account_name= self.account_name, container_name=self.container_name, blob_name= file_name, account_key= self.account_key, permission='r', expiry=datetime.utcnow() + timedelta(hours=1))

    def get_file_from_sas(self, sas_url: str) -> bytes:
        """Get a file from blob storage given the file's SAS URL."""
        blob_client = BlobClient.from_blob_url(sas_url)
        download_stream = blob_client.download_blob()
        return download_stream.readall()
    
    def get_file(self, file_path: str, container_name: Optional[str] = None) -> bytes:
        """Get a file from blob storage given the file's path."""
        if container_name is None:
            container_name = self.container_name
        # If container does not exist, create it
        if not self.blob_service_client.get_container_client(container_name).exists():
            self.blob_service_client.create_container(container_name)
        # Check if file exists, if not create it
        if not self.blob_service_client.get_blob_client(container_name, file_path).exists():
            self.blob_service_client.get_blob_client(container_name, file_path).upload_blob(b'')
        
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=file_path)
        download_stream = blob_client.download_blob()
        return download_stream.readall()

    def list_cases(self, path: str, filter_by_word: str, full_path: bool = True, remove_items: List[str] = ['C0 - Información Común']) -> List[str]:
        """
        List all cases (folders only) in the given path, filter the list by a contained word and remove specific items. 
        """
        container_name = self.container_name
        folder_name = path
        files = self.get_container_files(container_name, folder_name, full_path=True)
        folders = sorted(list(set([os.path.basename(os.path.dirname(name)) for name in files if '/' in os.path.dirname(name)])))
        if filter_by_word and filter_by_word != "ALL":
            folders = [folder for folder in folders if filter_by_word in folder]
        if remove_items:
            folders = [folder for folder in folders if folder not in remove_items]
        if full_path:
            folders = [os.path.join(path, folder) for folder in folders]
        return folders
