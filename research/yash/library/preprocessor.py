import glob
import numpy as np
import rasterio
from PIL import Image
import sqlite3
import os
from tqdm import tqdm

class PreProcessor:

    def __init__(self):
        pass

    def __convert_ms_to_rgb(self, input_path:str, output_folder:str,bands:list):
        file_name = input_path.split("/")[-1]
        # Open the tiff file
        with rasterio.open(input_path) as src:
            data = [src.read(band) for band in bands]
            composite = np.dstack(data)
            composite = (composite - composite.min()) / (composite.max() - composite.min()) * 255
            composite = composite.astype(np.uint8)
            image = Image.fromarray(composite)
            image.save(f"{output_folder}/{file_name}", format='TIFF')

    def convert_ms_to_rgb(self, input_path:str, output_folder:str,bands:list = [3,2,1]):
        
        # if the input path is a file, convert that file
        if os.path.isfile(input_path):
            self.__convert_ms_to_rgb(input_path,output_folder,bands)
            return

        # Get all tiff files in the folder even in subdirectories
        tiff_files = glob.glob(f"{input_path}/**/*.tif", recursive=True)

        # Create the output folder if it does not exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)

        for tiff_file in tqdm(tiff_files):
            self.__convert_ms_to_rgb(tiff_file,output_folder,bands)
