import requests
import os
from tqdm import tqdm
import zipfile

class DatasetLoader:
    base_dir:str

    def __init__(self, base_dir:str):
        # get current working directory
        cwd = os.getcwd()
        # set the base directory to the current working directory        
        self.base_dir = os.path.join(cwd, base_dir)

    def load_by_url(self, url: str, file_name: str):
    # Disable SSL certificate verification (for SSL errors)
        destination_path = os.path.join(self.base_dir, file_name)
        
        # Create the directory if it does not exist
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        # Get the response with streaming enabled
        response = requests.get(url, stream=True, verify=False)
        
        # Check if the request was successful
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))  # Total size in bytes
            
            # Use tqdm to show a progress bar
            with open(destination_path, 'wb') as f, tqdm(
                desc=file_name,
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:  # Filter out keep-alive chunks
                        f.write(chunk)
                        bar.update(len(chunk))
        else:
            print(f"Failed to download file. Status code: {response.status_code}")

    def list(self):
        datasets = []
        with os.scandir(self.base_dir) as entries:
            for entry in entries:
                if entry.is_file():
                    datasets.append(entry.name)

        return datasets
    
    def unzip_file(self, file_name: str):        
        file_path = os.path.join(self.base_dir, file_name)

        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(self.base_dir)
        print(f"Unzipped {file_name}")
        

