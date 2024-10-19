import glob
import json
import os
import sqlite3
import numpy as np
import cv2 
from PIL import Image
import time

from tqdm import tqdm


class SimulatedNoiseInjector:

    def __init__(self,connection:sqlite3.Connection):
        self.__connection = connection

    def __add_gaussian_noise(self,image, mean=0, var=0.01):
        """
        Add Gaussian noise to an image.
        
        Parameters:
        image (numpy array): The input image.
        mean (float): Mean of the Gaussian noise.
        var (float): Variance of the Gaussian noise.
        
        Returns:
        numpy array: Image with added Gaussian noise.
        """
        sigma = var ** 0.5
        gauss = np.random.normal(mean, sigma, image.shape).astype('float32')
        noisy_image = cv2.addWeighted(image.astype('float32'), 1.0, gauss, 1.0, 0)
        return np.clip(noisy_image, 0, 255).astype('uint8')

    def __add_salt_and_pepper_noise(self,image, salt_prob=0.01, pepper_prob=0.01):
        """
        Add salt and pepper noise to an image.
        
        Parameters:
        image (numpy array): The input image.
        salt_prob (float): Probability of salt noise (white pixels).
        pepper_prob (float): Probability of pepper noise (black pixels).
        
        Returns:
        numpy array: Image with added salt and pepper noise.
        """
        noisy_image = np.copy(image)
        total_pixels = image.size
        
        # Salt noise
        num_salt = int(salt_prob * total_pixels)
        coords = [np.random.randint(0, i - 1, num_salt) for i in image.shape]
        noisy_image[coords[0], coords[1], ...] = 255
        
        # Pepper noise
        num_pepper = int(pepper_prob * total_pixels)
        coords = [np.random.randint(0, i - 1, num_pepper) for i in image.shape]
        noisy_image[coords[0], coords[1], ...] = 0
        
        return noisy_image

    def __add_poisson_noise(self,image):
        """
        Add Poisson noise to an image.
        
        Parameters:
        image (numpy array): The input image.
        
        Returns:
        numpy array: Image with added Poisson noise.
        """
        # Normalize image to range 0-1 for Poisson noise
        noisy_image = np.random.poisson(image / 255.0 * 100) / 100 * 255
        return np.clip(noisy_image, 0, 255).astype('uint8')

    def __add_speckle_noise(self,image, mean=0, var=0.01):
        """
        Add speckle noise to an image.
        
        Parameters:
        image (numpy array): The input image.
        mean (float): Mean of the speckle noise.
        var (float): Variance of the speckle noise.
        
        Returns:
        numpy array: Image with added speckle noise.
        """
        sigma = var ** 0.5
        speckle = np.random.normal(mean, sigma, image.shape)
        noisy_image = image + image * speckle
        return np.clip(noisy_image, 0, 255).astype('uint8')

    def __add_uniform_noise(self,image, low=-10, high=10):
        """
        Add uniform noise to an image.
        
        Parameters:
        image (numpy array): The input image.
        low (int): Lower bound of the noise.
        high (int): Upper bound of the noise.
        
        Returns:
        numpy array: Image with added uniform noise.
        """
        uniform_noise = np.random.uniform(low, high, image.shape)
        noisy_image = image + uniform_noise
        return np.clip(noisy_image, 0, 255).astype('uint8')

    def __add_periodic_noise(self,image, frequency=10, amplitude=20):
        """
        Add periodic noise to an image.
        
        Parameters:
        image (numpy array): The input image.
        frequency (int): Frequency of the periodic noise.
        amplitude (int): Amplitude of the noise.
        
        Returns:
        numpy array: Image with added periodic noise.
        """
        rows, cols = image.shape[:2]
        x = np.arange(cols)
        y = np.sin(2 * np.pi * frequency * x / cols) * amplitude
        periodic_noise = np.tile(y, (rows, 1))
        
        if len(image.shape) == 3:
            periodic_noise = np.repeat(periodic_noise[..., np.newaxis], 3, axis=2)
            
        noisy_image = image.astype('float32') + periodic_noise
        return np.clip(noisy_image, 0, 255).astype('uint8')

    def __add_impulse_noise(self,image, prob=0.01):
        """
        Add impulse noise to an image.
        
        Parameters:
        image (numpy array): The input image.
        prob (float): Probability of an impulse noise (randomly changing a pixel).
        
        Returns:
        numpy array: Image with added impulse noise.
        """
        noisy_image = np.copy(image)
        impulse_mask = np.random.choice([0, 255], size=image.shape, p=[1 - prob, prob])
        noisy_image[impulse_mask == 255] = np.random.choice([0, 255], size=(impulse_mask == 255).sum())
        
        return noisy_image
    
    def __log(self,path:str,size:int,duration:float,run_id:str,input_path:str):
        with self.__connection:   
                self.__connection.execute(
                """UPDATE image_data 
                SET noisy_image_path = ?, 
                    noisy_image_size = ?
                WHERE run_id = ? 
                AND (compressed_image_path = ? OR noisy_image_path = ?)""",
                (f"{path}", 
                size, 
                run_id, 
                input_path, 
                input_path)
            )
                
    def __cv2pil(self,opencv_image):
        """
        Convert an OpenCV image to a PIL image.
        
        Parameters:
        opencv_image (numpy array): The OpenCV image.
        
        Returns:
        PIL image: The converted PIL image.
        """
        return Image.fromarray(cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB))
    
    def __pil2cv(self,pil_image):
        """
        Convert a PIL image to an OpenCV image.
        
        Parameters:
        pil_image (PIL image): The PIL image.
        
        Returns:
        numpy array: The converted OpenCV image.
        """
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
                
    def add_gaussian_noise(self, input_path:str, file_type:str,output_folder:str,mean:int,var:float,run_id:str):
        
        # if the input path is a file, convert that file
        if os.path.isfile(input_path):
            file_name = input_path.split("/")[-1]
            start_time = time.perf_counter()
            with Image.open(input_path) as img:
                opencv_image = self.__pil2cv(img)
                noisy_image = self.__add_gaussian_noise(opencv_image,mean=mean,var=var)
                noisy_image = self.__cv2pil(noisy_image)
                noisy_image.save(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}")
                start_time = time.perf_counter()
                self.__log(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}",os.path.getsize(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}"),(start_time - time.perf_counter()),run_id,input_path)
            return

        # Get all tiff files in the folder even in subdirectories
        tiff_files = glob.glob(f"{input_path}/**/*.{file_type}", recursive=True)

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
                file_name = tiff_file.split("/")[-1]
                start_time = time.perf_counter()
                with Image.open(tiff_file) as img:
                    opencv_image = np.array(img)

                    # Convert RGB to BGR format, as OpenCV uses BGR
                    opencv_image = self.__pil2cv(img)
                    noisy_image = self.__add_gaussian_noise(opencv_image,mean=mean,var=var)
                    noisy_image = self.__cv2pil(noisy_image)
                    noisy_image.save(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}")
                    start_time = time.perf_counter()
                    self.__log(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}",os.path.getsize(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}"),(start_time - time.perf_counter()),run_id,tiff_file)

                    to_return["success"] += 1
                    yield json.dumps(to_return)
            except Exception as e:
                to_return["failed"] += 1
                yield json.dumps(to_return)
                continue

    def add_salt_and_pepper_noise(self, input_path:str, file_type:str,output_folder:str,salt_prob:float,pepper_prob:float,run_id:str):
        
        # if the input path is a file, convert that file
        if os.path.isfile(input_path):
            file_name = input_path.split("/")[-1]
            start_time = time.perf_counter()
            with Image.open(input_path) as img:
                opencv_image = self.__pil2cv(img)
                noisy_image = self.__add_salt_and_pepper_noise(opencv_image,salt_prob=salt_prob,pepper_prob=pepper_prob)
                noisy_image = self.__cv2pil(noisy_image)
                noisy_image.save(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}")
                start_time = time.perf_counter()
                self.__log(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}",os.path.getsize(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}"),(start_time - time.perf_counter()),run_id,input_path)
            return

        # Get all tiff files in the folder even in subdirectories
        tiff_files = glob.glob(f"{input_path}/**/*.{file_type}", recursive=True)

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
                file_name = tiff_file.split("/")[-1]
                start_time = time.perf_counter()
                with Image.open(tiff_file) as img:
                    opencv_image = np.array(img)

                    # Convert RGB to BGR format, as OpenCV uses BGR
                    opencv_image = self.__pil2cv(img)
                    noisy_image = self.__add_salt_and_pepper_noise(opencv_image,salt_prob=salt_prob,pepper_prob=pepper_prob)
                    noisy_image = self.__cv2pil(noisy_image)
                    noisy_image.save(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}")
                    start_time = time.perf_counter()
                    self.__log(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}",os.path.getsize(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}"),(start_time - time.perf_counter()),run_id,tiff_file)

                    to_return["success"] += 1
                    yield json.dumps(to_return)
            except Exception as e:
                to_return["failed"] += 1
                yield json.dumps(to_return)
                continue

    def add_poisson_noise(self, input_path:str, file_type:str,output_folder:str,run_id:str):
        
        # if the input path is a file, convert that file
        if os.path.isfile(input_path):
            file_name = input_path.split("/")[-1]
            start_time = time.perf_counter()
            with Image.open(input_path) as img:
                opencv_image = self.__pil2cv(img)
                noisy_image = self.__add_poisson_noise(opencv_image)
                noisy_image = self.__cv2pil(noisy_image)
                noisy_image.save(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}")
                start_time = time.perf_counter()
                self.__log(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}",os.path.getsize(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}"),(start_time - time.perf_counter()),run_id,input_path)
            return

        # Get all tiff files in the folder even in subdirectories
        tiff_files = glob.glob(f"{input_path}/**/*.{file_type}", recursive=True)

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
                file_name = tiff_file.split("/")[-1]
                start_time = time.perf_counter()
                with Image.open(tiff_file) as img:
                    opencv_image = np.array(img)

                    # Convert RGB to BGR format, as OpenCV uses BGR
                    opencv_image = self.__pil2cv(img)
                    noisy_image = self.__add_poisson_noise(opencv_image)
                    noisy_image = self.__cv2pil(noisy_image)
                    noisy_image.save(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}")
                    start_time = time.perf_counter()
                    self.__log(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}",os.path.getsize(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}"),(start_time - time.perf_counter()),run_id,tiff_file)

                    to_return["success"] += 1
                    yield json.dumps(to_return)
            except Exception as e:
                to_return["failed"] += 1
                yield json.dumps(to_return)
                continue

    def add_speckle_noise(self, input_path:str, file_type:str,output_folder:str,mean:float, var:float,run_id:str):
        
        # if the input path is a file, convert that file
        if os.path.isfile(input_path):
            file_name = input_path.split("/")[-1]
            start_time = time.perf_counter()
            with Image.open(input_path) as img:
                opencv_image = self.__pil2cv(img)
                noisy_image = self.__add_speckle_noise(opencv_image,mean=mean,var=var)
                noisy_image = self.__cv2pil(noisy_image)
                noisy_image.save(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}")
                start_time = time.perf_counter()
                self.__log(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}",os.path.getsize(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}"),(start_time - time.perf_counter()),run_id,input_path)
            return

        # Get all tiff files in the folder even in subdirectories
        tiff_files = glob.glob(f"{input_path}/**/*.{file_type}", recursive=True)

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
                file_name = tiff_file.split("/")[-1]
                start_time = time.perf_counter()
                with Image.open(tiff_file) as img:
                    opencv_image = np.array(img)

                    # Convert RGB to BGR format, as OpenCV uses BGR
                    opencv_image = self.__pil2cv(img)
                    noisy_image = self.__add_speckle_noise(opencv_image,mean=mean,var=var)
                    noisy_image = self.__cv2pil(noisy_image)
                    noisy_image.save(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}")
                    start_time = time.perf_counter()
                    self.__log(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}",os.path.getsize(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}"),(start_time - time.perf_counter()),run_id,tiff_file)

                    to_return["success"] += 1
                    yield json.dumps(to_return)
            except Exception as e:
                to_return["failed"] += 1
                yield json.dumps(to_return)
                continue

    def add_uniform_noise(self, input_path:str, file_type:str,output_folder:str,low:float, high:float,run_id:str):
        
        # if the input path is a file, convert that file
        if os.path.isfile(input_path):
            file_name = input_path.split("/")[-1]
            start_time = time.perf_counter()
            with Image.open(input_path) as img:
                opencv_image = self.__pil2cv(img)
                noisy_image = self.__add_uniform_noise(opencv_image,low=low,high=high)
                noisy_image = self.__cv2pil(noisy_image)
                noisy_image.save(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}")
                start_time = time.perf_counter()
                self.__log(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}",os.path.getsize(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}"),(start_time - time.perf_counter()),run_id,input_path)
            return

        # Get all tiff files in the folder even in subdirectories
        tiff_files = glob.glob(f"{input_path}/**/*.{file_type}", recursive=True)

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
                file_name = tiff_file.split("/")[-1]
                start_time = time.perf_counter()
                with Image.open(tiff_file) as img:
                    opencv_image = np.array(img)

                    # Convert RGB to BGR format, as OpenCV uses BGR
                    opencv_image = self.__pil2cv(img)
                    noisy_image = self.__add_uniform_noise(opencv_image,low=low,high=high)
                    noisy_image = self.__cv2pil(noisy_image)
                    noisy_image.save(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}")
                    start_time = time.perf_counter()
                    self.__log(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}",os.path.getsize(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}"),(start_time - time.perf_counter()),run_id,tiff_file)

                    to_return["success"] += 1
                    yield json.dumps(to_return)
            except Exception as e:
                to_return["failed"] += 1
                yield json.dumps(to_return)
                continue

    def add_periodic_noise(self, input_path:str, file_type:str,output_folder:str,frequency:int, amplitude:int,run_id:str):
        
        # if the input path is a file, convert that file
        if os.path.isfile(input_path):
            file_name = input_path.split("/")[-1]
            start_time = time.perf_counter()
            with Image.open(input_path) as img:
                opencv_image = self.__pil2cv(img)
                noisy_image = self.__add_periodic_noise(opencv_image,frequency=frequency,amplitude=amplitude)
                noisy_image = self.__cv2pil(noisy_image)
                noisy_image.save(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}")
                start_time = time.perf_counter()
                self.__log(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}",os.path.getsize(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}"),(start_time - time.perf_counter()),run_id,input_path)
            return

        # Get all tiff files in the folder even in subdirectories
        tiff_files = glob.glob(f"{input_path}/**/*.{file_type}", recursive=True)

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
                file_name = tiff_file.split("/")[-1]
                start_time = time.perf_counter()
                with Image.open(tiff_file) as img:
                    opencv_image = np.array(img)

                    # Convert RGB to BGR format, as OpenCV uses BGR
                    opencv_image = self.__pil2cv(img)
                    noisy_image = self.__add_periodic_noise(opencv_image,frequency=frequency,amplitude=amplitude)
                    noisy_image = self.__cv2pil(noisy_image)
                    noisy_image.save(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}")
                    start_time = time.perf_counter()
                    self.__log(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}",os.path.getsize(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}"),(start_time - time.perf_counter()),run_id,tiff_file)

                    to_return["success"] += 1
                    yield json.dumps(to_return)
            except Exception as e:
                to_return["failed"] += 1
                yield json.dumps(to_return)
                continue

    def add_impulse_noise(self, input_path:str, file_type:str,output_folder:str,prob:float,run_id:str):
        
        # if the input path is a file, convert that file
        if os.path.isfile(input_path):
            file_name = input_path.split("/")[-1]
            start_time = time.perf_counter()
            with Image.open(input_path) as img:
                opencv_image = self.__pil2cv(img)
                noisy_image = self.__add_impulse_noise(opencv_image,prob=prob)
                noisy_image = self.__cv2pil(noisy_image)
                noisy_image.save(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}")
                start_time = time.perf_counter()
                self.__log(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}",os.path.getsize(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}"),(start_time - time.perf_counter()),run_id,input_path)
            return

        # Get all tiff files in the folder even in subdirectories
        tiff_files = glob.glob(f"{input_path}/**/*.{file_type}", recursive=True)

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
                file_name = tiff_file.split("/")[-1]
                start_time = time.perf_counter()
                with Image.open(tiff_file) as img:
                    opencv_image = np.array(img)

                    # Convert RGB to BGR format, as OpenCV uses BGR
                    opencv_image = self.__pil2cv(img)
                    noisy_image = self.__add_impulse_noise(opencv_image,prob=prob)
                    noisy_image = self.__cv2pil(noisy_image)
                    noisy_image.save(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}")
                    start_time = time.perf_counter()
                    self.__log(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}",os.path.getsize(f"{output_folder}/{file_name.replace(f'.{file_type}','')}.{file_type}"),(start_time - time.perf_counter()),run_id,tiff_file)

                    to_return["success"] += 1
                    yield json.dumps(to_return)
            except Exception as e:
                to_return["failed"] += 1
                yield json.dumps(to_return)
                continue

        