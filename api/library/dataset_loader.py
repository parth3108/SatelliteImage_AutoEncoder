import sqlite3
import requests
import os
from tqdm import tqdm
import zipfile
import json
import time

class DatasetLoader:
    base_dir:str

    def __init__(self, base_dir:str,connection:sqlite3.Connection):
        # get current working directory
        cwd = os.getcwd()
        # set the base directory to the current working directory        
        self.base_dir = os.path.join(cwd, base_dir)
        self.__connection = connection

    def load_by_url(self, url: str, file_name: str):
    # Disable SSL certificate verification (for SSL errors)
        destination_path = os.path.join(self.base_dir, file_name)
        
        # Create the directory if it does not exist
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        # Check if the file already exists
        if os.path.exists(destination_path):
            yield str(f"File {file_name} already exists")
            return

        # Get the response with streaming enabled
        response = requests.get(url, stream=True, verify=False)
                

        # Check if the request was successful
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))  # Total size in bytes
            to_return = {
            "success":0,
            "failed":0,
            "total":total_size
        }
            
            yield json.dumps(to_return)

            
            # Use tqdm to show a progress bar
            with open(destination_path, 'wb') as f, tqdm(
                desc=file_name,
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for chunk in response.iter_content(chunk_size=2048000):
                    if chunk:  # Filter out keep-alive chunks
                        f.write(chunk)
                        bar.update(len(chunk))
                        to_return["success"] += len(chunk)
                        yield json.dumps(to_return)

            yield "{} File Downloaded".format(file_name)

            # Create a sqlite table if not exists and insert metadata of the downloaded file into the table
            with self.__connection:                
                self.__connection.execute(
                    "INSERT INTO datasets (name, path) VALUES (?, ?)", (file_name, destination_path)
                )            

        else:
            yield str(f"Error in downloading file. Status code: {response.status_code}")

    def list(self):
        datasets = []
        # list all the folders recursively in the base directory
        for root, dirs, files in os.walk(self.base_dir):
            # only directories with files are considered
            if len(files) > 0:
                # add the directory to the list of datasets create hirearchy in the form of a dictionary
                if "__MACOSX" not in root:
                    datasets.append(
                        {
                            "name": os.path.basename(root),
                            "path": root,
                            "files": files
                        }
                    )

        return datasets
    
    def unzip_file(self, zip_file_path_or_name: str,destination_folder:str):               

        cwd = os.getcwd()
        try:
        
            if cwd in zip_file_path_or_name:
                file_path = zip_file_path_or_name
            else:
                file_path = os.path.join(self.base_dir, zip_file_path_or_name)

            destination_path = os.path.join(self.base_dir, destination_folder)
            print(destination_path)

            if not os.path.exists(file_path):
                yield (f"File {file_path} does not exist")
                return
            
            if not os.path.exists(destination_path):
                os.makedirs(destination_path, exist_ok=True)

            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(destination_path)
                yield str(f"Unzipped {file_path} to {destination_path}")
            
            # Create a sqlite table if not exists and insert metadata of the downloaded file into the table
            with self.__connection:            
                self.__connection.execute(
                    "INSERT INTO extracted_datasets (zip_file_path, destination_folder) VALUES (?, ?)", (file_path, destination_path)
                )

        except Exception as e:
            return f"Exception: {str(e)}"
        

        

