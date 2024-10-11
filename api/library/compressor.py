import glob
import os
import sqlite3
from tqdm import tqdm
from PIL import Image
import time


class Compressor:
    
    def __init__(self,connection:sqlite3.Connection):
        self.__connection = connection


    def __compress_png(self,input_path:str, output_folder:str,quality:int,run_id:str):
        file_name = input_path.split("/")[-1]
        input_file_size = os.path.getsize(input_path)
        # start time
        start_time = time.perf_counter()
        with Image.open(input_path) as img:     
            with self.__connection:      
                self.__connection.execute(
                    """INSERT INTO image_data (run_id, input_image_path, input_image_size) VALUES (?, ?, ?)""",
                    (run_id, input_path,input_file_size )
                )                
            img.save(f"{output_folder}/{file_name.replace('.tif','')}.png", "PNG", optimize=True, quality=quality)
            end_time = time.perf_counter()
            # Update the compressed image path and size in the database
            with self.__connection:   
                self.__connection.execute(
                    """UPDATE image_data 
                    SET compressed_image_path = ?,
                    compressed_image_size = ?,
                    compression_time = ? 
                    WHERE input_image_path = ? AND run_id = ?""",
                    (f"{output_folder}/{file_name.replace('.tif', '')}.png", 
                     os.path.getsize(f"{output_folder}/{file_name.replace('.tif', '')}.png"), 
                     (end_time - start_time) * 1_000_000,
                     input_path, 
                     run_id)
                )

    def __compress_jpeg(self,input_path:str, output_folder:str,quality:int,run_id:str):
        file_name = input_path.split("/")[-1]
        input_file_size = os.path.getsize(input_path)
        start_time = time.perf_counter()
        with Image.open(input_path) as img:     
            with self.__connection:      
                self.__connection.execute(
                    """INSERT INTO image_data (run_id, input_image_path, input_image_size) VALUES (?, ?, ?)""",
                    (run_id, input_path,input_file_size )
                )                
            img.save(f"{output_folder}/{file_name.replace('.tif','')}.jpg", "JPEG", quality=quality)
            # Update the compressed image path and size in the database
            end_time = time.perf_counter()
            with self.__connection:   
                self.__connection.execute(
                    """UPDATE image_data 
                    SET compressed_image_path = ?, 
                    compressed_image_size = ?,
                    compression_time = ? 
                    WHERE input_image_path = ? AND run_id = ?""",
                    (f"{output_folder}/{file_name.replace('.tif', '')}.jpg", 
                     os.path.getsize(f"{output_folder}/{file_name.replace('.tif', '')}.jpg"), 
                     (end_time - start_time) * 1_000_000,
                     input_path, 
                     run_id)
                )
        
    def compress_png(self,input_path:str, output_folder:str,quality:int,run_id:str):
        
        # if the input path is a file, convert that file
        if os.path.isfile(input_path):
            self.__compress_png(input_path,output_folder,quality,run_id)
            return
        # Get all tiff files in the folder even in subdirectories
        tiff_files = glob.glob(f"{input_path}/**/*.tif", recursive=True)

        # Create the output folder if it does not exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)

        for tiff_file in tqdm(tiff_files):
            self.__compress_png(tiff_file,output_folder,quality,run_id)

    def compress_jpeg(self,input_path:str, output_folder:str,quality:int,run_id:str):
        
        # if the input path is a file, convert that file
        if os.path.isfile(input_path):
            self.__compress_jpeg(input_path,output_folder,quality,run_id)
            return
        # Get all tiff files in the folder even in subdirectories
        tiff_files = glob.glob(f"{input_path}/**/*.tif", recursive=True)

        # Create the output folder if it does not exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)

        for tiff_file in tqdm(tiff_files):
            self.__compress_jpeg(tiff_file,output_folder,quality,run_id)
