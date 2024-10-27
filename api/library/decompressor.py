import glob
import os
import sqlite3
import numpy as np
from tqdm import tqdm
from PIL import Image
import time
import json
from tensorflow import keras


class Decompressor:
    
    def __init__(self,connection:sqlite3.Connection):
        self.__connection = connection


    def __decompress_png(self,input_path:str, output_folder:str,run_id:str):
        file_name = input_path.split("/")[-1]
        start_time = time.perf_counter()
        with Image.open(input_path) as img:
            img.save(f"{output_folder}/{file_name}", "PNG")
            # self.__connection.execute(
            #     "CREATE TABLE IF NOT EXISTS image_data (id INTEGER PRIMARY KEY AUTOINCREMENT,run_id TEXT,input_image_path TEXT, compressed_image_path TEXT, noisy_image_path TEXT,decompressed_image_path TEXT, input_image_size INTEGER, compressed_image_size INTEGER, noisy_image_size INTEGER, decompressed_image_size INTEGER)"
            # )
            # Update the decompressed image path and size in the database
            end_time = time.perf_counter()
            with self.__connection:   
                self.__connection.execute(
                """UPDATE image_data 
                SET decompressed_image_path = ?, 
                    decompressed_image_size = ?,
                    decompression_time = ? 
                WHERE run_id = ? 
                AND (compressed_image_path = ? OR noisy_image_path = ?)""",
                (f"{output_folder}/{file_name}", 
                os.path.getsize(f"{output_folder}/{file_name}"), 
                (end_time - start_time) * 1_000_000,
                run_id, 
                input_path, 
                input_path)
            )
                
    
    def __decompress_dl_decoder(self,input_path:str, output_folder:str,run_id:str):
        file_name = input_path.split("/")[-1]
        start_time = time.perf_counter()
        with Image.open(input_path) as img:
            model = keras.models.load_model('decoder_output.h5')
            img = img.resize((256,256))
            img_array = np.array(img)
            img_array = img_array/255.0
            img_array = img_array.reshape(1,256,256,3)
            img_array = model.predict(img_array)
            img_array = img_array*255
            img_array = img_array.reshape(256,256,3)
            img_array = Image.fromarray(img_array.astype('uint8'))
            img_array.save(f"{output_folder}/{file_name.replace('.tif','')}.jpg", "JPEG")
            # self.__connection.execute(
            #     "CREATE TABLE IF NOT EXISTS image_data (id INTEGER PRIMARY KEY AUTOINCREMENT,run_id TEXT,input_image_path TEXT, compressed_image_path TEXT, noisy_image_path TEXT,decompressed_image_path TEXT, input_image_size INTEGER, compressed_image_size INTEGER, noisy_image_size INTEGER, decompressed_image_size INTEGER)"
            # )
            # Update the decompressed image path and size in the database
            end_time = time.perf_counter()
            with self.__connection:   
                self.__connection.execute(
                """UPDATE image_data 
                SET decompressed_image_path = ?, 
                    decompressed_image_size = ? ,
                    decompression_time = ? 
                WHERE run_id = ? 
                AND (compressed_image_path = ? OR noisy_image_path = ?)""",
                (f"{output_folder}/{file_name.replace('.jpg','')}.tif", 
                os.path.getsize(f"{output_folder}/{file_name.replace('.jpg','')}.tif"), 
                (end_time - start_time) * 1_000_000,
                run_id, 
                input_path, 
                input_path)
            )
        

    def decompress_jpeg(self, input_path:str, output_folder:str,run_id:str):
        
        # if the input path is a file, convert that file
        if os.path.isfile(input_path):
            self.__decompress_jpeg(input_path,output_folder,run_id)
            return

        # Get all tiff files in the folder even in subdirectories
        tiff_files = glob.glob(f"{input_path}/**/*.jpg", recursive=True)

        # Create the output folder if it does not exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)

        to_return = {
            "success":0,
            "failed":0,
            "total":len(tiff_files)
        }

        for tiff_file in tqdm(tiff_files):
            try:
                self.__decompress_jpeg(tiff_file,output_folder,run_id)
                to_return["success"] += 1
                yield json.dumps(to_return)
            except Exception as e:
                to_return["failed"] += 1
                yield json.dumps(to_return)
                continue

    def decompress_png(self, input_path:str, output_folder:str,run_id:str):
        
        # if the input path is a file, convert that file
        if os.path.isfile(input_path):
            self.__decompress_png(input_path,output_folder,run_id)
            return

        # Get all tiff files in the folder even in subdirectories
        tiff_files = glob.glob(f"{input_path}/**/*.png", recursive=True)

        # Create the output folder if it does not exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)

        to_return = {
            "success":0,
            "failed":0,
            "total":len(tiff_files)
        }

        for tiff_file in tqdm(tiff_files):
            try:
                self.__decompress_png(tiff_file,output_folder,run_id)
                to_return["success"] += 1
                yield json.dumps(to_return)
            except Exception as e:
                to_return["failed"] += 1
                yield json.dumps(to_return)
                continue
        
    def decompress_dl_decoder(self, input_path:str, output_folder:str,run_id:str):
        
        # if the input path is a file, convert that file
        if os.path.isfile(input_path):
            self.__decompress_dl_decoder(input_path,output_folder,run_id)
            return

        # Get all tiff files in the folder even in subdirectories
        tiff_files = glob.glob(f"{input_path}/**/*.jpg", recursive=True)

        # Create the output folder if it does not exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)

        to_return = {
            "success":0,
            "failed":0,
            "total":len(tiff_files)
        }

        for tiff_file in tqdm(tiff_files):
            try:
                self.__decompress_dl_decoder(tiff_file,output_folder,run_id)
                to_return["success"] += 1
                yield json.dumps(to_return)
            except Exception as e:
                to_return["failed"] += 1
                yield json.dumps(to_return)
                continue