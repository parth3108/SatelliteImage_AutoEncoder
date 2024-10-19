import base64
from io import BytesIO
import sqlite3
import numpy as np
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import structural_similarity as ssim
from sklearn.metrics import mean_squared_error
import lpips
import torch
from torchvision import transforms
from PIL import Image
from tqdm import tqdm
import json
import pandas as pd

class Evaluator:

    def __init__(self,connection:sqlite3.Connection):
        self.__connection = connection

    def __calculate_psnr(self,img1, img2):
        """
        Calculate the Peak Signal-to-Noise Ratio (PSNR) between two images.

        PSNR is a metric used to measure the quality of reconstructed images compared to original images, 
        particularly in image compression and video encoding applications. It is defined as the ratio 
        between the maximum possible power of a signal (the original image) and the power of corrupting 
        noise (the difference between the original and reconstructed images).

        PSNR Formula:
            PSNR = 10 * log10(MAX_I^2 / MSE)

        Where:
            - MAX_I: Maximum possible pixel value of the image (255 for 8-bit images).
            - MSE: Mean Squared Error calculated as:
                MSE = (1/N) * sum((I(i) - K(i))^2)
                Where:
                - I: Original image.
                - K: Reconstructed image.
                - N: Number of pixels in the image.

        Interpreting PSNR Values:
            - Higher values indicate better quality.
            - Common thresholds:
                - Below 20 dB: Poor quality; noticeable distortion.
                - 20-30 dB: Fair to good quality; noticeable artifacts may be present.
                - 30-40 dB: Good quality; generally acceptable for most applications.
                - Above 40 dB: Excellent quality; often indistinguishable from the original image.

        Limitations:
            - PSNR may not correlate well with perceived visual quality.
            - It does not account for how humans perceive images; two images with the same PSNR might look 
                different to the human eye.
        
        Parameters:
            img1: np.ndarray - First image (original image).
            img2: np.ndarray - Second image (compressed or decompressed image).
        
        Returns:
            psnr_value: float - PSNR value.
        """

        if np.array_equal(img1, img2):
            return 50
        psnr_value = psnr(img1, img2,data_range=255)

        return psnr_value
    
    def __calculate_ssim(self,img1, img2):
        """
        Calculate the Structural Similarity Index (SSIM) between two images.

        SSIM is a perceptual metric that quantifies the similarity between two images. 
        It is based on the idea that the human visual system is highly sensitive to structural information 
        in an image. SSIM considers changes in structural information, luminance, and contrast, 
        providing a more accurate measure of perceived image quality than metrics like PSNR.

        SSIM Formula:
            SSIM(x, y) = (2 * μ_x * μ_y + C1) * (2 * σ_xy + C2) / ((μ_x^2 + μ_y^2 + C1) * (σ_x^2 + σ_y^2 + C2))

        Where:
            - μ_x and μ_y: Mean values of the two images.
            - σ_x^2 and σ_y^2: Variances of the two images.
            - σ_xy: Covariance between the two images.
            - C1 and C2: Constants to stabilize the division; typically C1 = (K1 * L)^2 and C2 = (K2 * L)^2, where K1 and K2 are small constants, and L is the dynamic range of the pixel values.

        Interpreting SSIM Values:
            - SSIM values range from -1 to 1.
            - A value of 1 indicates perfect structural similarity.
            - Values closer to 1 indicate higher similarity, while values closer to -1 indicate lower similarity.
            - Typical ranges:
                - 0.9 to 1.0: Excellent quality; very similar images.
                - 0.7 to 0.9: Good quality; noticeable but acceptable differences.
                - 0.5 to 0.7: Fair quality; significant differences.
                - Below 0.5: Poor quality; very different images.

        Limitations:
            - SSIM can be sensitive to alignment; images must be properly aligned to obtain accurate results.
            - It may not capture all perceptual differences, especially for images with significant variations in lighting or content.

        Parameters:
        img1: np.ndarray - First image (original image).
        img2: np.ndarray - Second image (compressed or decompressed image).
        
        Returns:
            ssim_value: float - SSIM value.
        """
        min_size = min(img1.shape[:2])  # Get the minimum dimension of the image (height or width)
    
        # Set win_size to a smaller odd value if the image is too small
        if min_size < 7:
            win_size = min_size if min_size % 2 != 0 else min_size - 1  # Make sure win_size is odd
            print(f"Image size is small. Using win_size = {win_size} for SSIM calculation.")
        else:
            win_size = 7  # Default win_size


        # Calculate SSIM
        ssim_value, _ = ssim(img1, img2, win_size=win_size, channel_axis=-1, full=True)

        return ssim_value
        

    def __calculate_mse(self,img1, img2):
        """

        Calculate the Mean Squared Error (MSE) between two images.

        MSE is a measure of the average squared differences between the original and 
        reconstructed images. It quantifies the error introduced by the compression or 
        reconstruction process, providing a numerical value that indicates how closely 
        the two images match.

        MSE Formula:
            MSE = (1/N) * sum((I(i) - K(i))^2)

        Where:
            - I(i): Pixel value of the original image at position i.
            - K(i): Pixel value of the reconstructed/compressed image at position i.
            - N: Total number of pixels in the image.

        Interpreting MSE Values:
            - Lower MSE values indicate better quality, as they represent less deviation 
                from the original image.
            - An MSE of 0 indicates perfect reconstruction, meaning the two images are identical.
            - Common interpretation ranges:
                - 0 to 10: Excellent quality; minimal differences.
                - 10 to 20: Good quality; slight differences may be noticeable.
                - 20 to 30: Fair quality; noticeable differences.
                - Above 30: Poor quality; significant differences.

        Limitations:
            - MSE does not account for perceptual differences; it treats all pixel differences 
                equally, which may not align with human visual perception.
            - It can be overly sensitive to noise and outliers.
        
        Parameters:
            img1: np.ndarray - First image (original image).
            img2: np.ndarray - Second image (compressed or decompressed image).
        
        Returns:
            mse_value: float - MSE value.
        """
        mse_value = mean_squared_error(img1.flatten(), img2.flatten())

        return mse_value
            

    def __calculate_lpips(self,img1, img2,model=lpips.LPIPS):
        """
        Calculate the Learned Perceptual Image Patch Similarity (LPIPS) between two images.

        LPIPS is a perceptual metric designed to measure the similarity between two images 
        based on deep learning features rather than pixel-wise differences. It captures 
        perceptual differences more effectively than traditional metrics like PSNR or MSE, 
        as it considers the way humans perceive visual content.

        LPIPS Metric:
            LPIPS compares the feature representations of two images as extracted from 
            a pretrained convolutional neural network (CNN). The differences in these features 
            are aggregated to provide a single score that reflects perceptual similarity.

        Interpreting LPIPS Values:
            - LPIPS values typically range from 0 to 1.
            - A value of **0** indicates that the two images are perceptually identical.
            - Higher values indicate greater perceptual dissimilarity.
            - Common interpretation ranges:
                - 0 to 0.1: Excellent similarity; nearly indistinguishable images.
                - 0.1 to 0.3: Good similarity; minor perceptual differences.
                - 0.3 to 0.5: Moderate similarity; noticeable differences.
                - Above 0.5: Poor similarity; significant perceptual differences.

        Advantages:
            - LPIPS is designed to align better with human perception than pixel-wise metrics.
            - It captures perceptual nuances and can effectively evaluate image quality 
            in various applications, such as image compression, style transfer, and super-resolution.

        Limitations:
            - LPIPS requires a pretrained model and may involve additional computational overhead.
            - The interpretation of LPIPS values can depend on the context and specific use case.
        
        Parameters:
            img1: np.ndarray - First image (original image).
            img2: np.ndarray - Second image (compressed or decompressed image).
            model: lpips.LPIPS - Pre-trained LPIPS model (default: AlexNet backbone).
        
        Returns:
            lpips_value: float - LPIPS distance (lower means more perceptually similar).
        """        
        # Convert images to torch tensors
        transform = transforms.ToTensor()
        
        img1_tensor = transform(img1).unsqueeze(0)
        img2_tensor = transform(img2).unsqueeze(0)
        
        # Calculate LPIPS
        lpips_value = model(img1_tensor, img2_tensor)

        return lpips_value.item()
    
    def __evaluate(self,input_file_path:str,output_file_path:str,lpips_model:lpips.LPIPS = None):
        """
        Evaluate the compressed image using various metrics.
        
        Parameters:
            run_id: str - Unique identifier for the current run.
            evaluation_id: str - Unique identifier for the evaluation.
            input_file: str - Path to the original image file.
            output_file: str - Path to the output image file.
            lpips_model: lpips.LPIPS - Pre-trained LPIPS model (default: AlexNet backbone).
        
        Returns:
            results: dict - Dictionary containing evaluation results.
        """
        # Load the original and decompressed images

        original_image = np.array(Image.open(input_file_path))
        output_image = np.array(Image.open(output_file_path))        
        
        # Calculate evaluation metrics
        psnr_value = self.__calculate_psnr(original_image, output_image)
        ssim_value = self.__calculate_ssim(original_image, output_image)
        mse_value = self.__calculate_mse(original_image, output_image)
        lpips_value = self.__calculate_lpips(original_image, output_image,lpips_model)
                
        # Return the evaluation results
        results = {
            'PSNR': psnr_value,
            'SSIM': ssim_value,
            'MSE': mse_value,
            'LPIPS': lpips_value
        }
        
        return results
    

    def evaluate(self,run_id:str,evaluation_id:str,input_type:str,output_type:str):
        """
        Evaluate the compressed images using various metrics.
        
        Parameters:
            run_id: str - Unique identifier for the current run.
            evaluation_id: str - Unique identifier for the evaluation.
            input_type: str - Type of input images ('original' or 'noisy').
            output_type: str - Type of output images ('compressed' or 'decompressed').        
        """
        # Get the input and output file paths
        lpips_model = lpips.LPIPS(net='alex')  # 'alex', 'vgg', or 'squeeze' are valid options
        with self.__connection:
            cursor = self.__connection.cursor()
            cursor.execute(
                f"""SELECT {input_type} as input_file, {output_type} as output_file, results, id
                FROM image_data
                WHERE run_id = '{run_id}'"""
            )
            result = cursor.fetchall()
            cursor.close()

        if len(result) == 0:
            raise ValueError("No images found for the specified run and evaluation.")
        
        to_return = {
            "success":0,
            "failed":0,
            "total":len(result)
        }
        
        for row in tqdm(result):
            input_file_path = row[0]
            output_file_path = row[1]            

            if input_file_path is None or output_file_path is None:
                continue

            id = row[3]
            
            if row[2] is None:
                results = {}            
            else:
                results = json.loads(row[2])
                    
            try:
                results[evaluation_id] = self.__evaluate(input_file_path,output_file_path,lpips_model)
                to_return["success"] += 1
                yield json.dumps(to_return)
            except Exception as e:
                results[evaluation_id] = str(e)
                to_return["failed"] += 1
                yield json.dumps(to_return)
                continue

            with self.__connection:
                self.__connection.execute(
                    """UPDATE image_data
                    SET results = ?
                    WHERE id = ?""",
                    (json.dumps(results), id)
                )


    def get_run_ids(self):
        """
        Get the unique run IDs from the database.
        
        Returns:
            run_ids: list - List of unique run IDs.
        """
        with self.__connection:
            cursor = self.__connection.cursor()
            cursor.execute(
                """SELECT DISTINCT run_id
                FROM image_data"""
            )
            run_ids = [row[0] for row in cursor.fetchall()]
            cursor.close()

        if len(run_ids) >= 1:
            return run_ids
        else:
            raise ValueError("No run IDs found in the database.")
            

    def get_evaluation_ids(self,run_id:str):
        """
        Get the unique evaluation IDs from the database.
        
        Returns:
            evaluation_ids: list - List of unique evaluation IDs.
        """
        with self.__connection:
            cursor = self.__connection.cursor()
            cursor.execute(
                """SELECT results
                FROM image_data WHERE run_id = ?""",
                (run_id,)
            )
            results = [row[0] for row in cursor.fetchall()]
            cursor.close()        

        evaluation_ids = set()        
        for result in results:
            if result is not None:
                evaluation_ids.update(json.loads(result).keys())

        if len(evaluation_ids) >= 1:
            return evaluation_ids
        else:
            raise ValueError("No evaluation IDs found in the database.")
            
    def get_results_by_run_id(self,run_id:str):
        """
        Get the evaluation results for a specific run ID.
        
        Parameters:
            run_id: str - Unique identifier for the current run.
        
        Returns:
            results: dict - Dictionary containing evaluation results for the run.
        """
        with self.__connection:
            df = pd.read_sql_query(f"""SELECT *
            FROM image_data
            WHERE run_id = '{run_id}'""", self.__connection)


        if df.empty:
            raise ValueError("No images found for the specified run.")
        
        df_filled = df.replace(to_replace=np.nan, value=None)
        
        return df_filled.to_dict(orient='records')
    
    def get_evalauation_fields(self):
        return [                        
            "input_image_path",
            "compressed_image_path",
            "decompressed_image_path",            
            "noisy_image_path"
        ]
        

    def get_image_by_path(self,path:str):
        """
        Get the image data from the database based on the file path.
        
        Parameters:
            path: str - File path of the image.

        """

        # get image from and return base64 no need to use database
        try:                                
            with open(path, "rb") as image_file:
                if path.lower().endswith('.tiff') or path.lower().endswith('.tif'):
                    image = Image.open(image_file)
                    with BytesIO() as buffer:
                        image.save(buffer, format="PNG")
                        base64_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
                        return base64_string
                # If image is in tiff format, convert it to PNG format and then encode                
                base64_string = base64.b64encode(image_file.read()).decode('utf-8')
                return base64_string
        except Exception as e:
            raise ValueError(f"Error reading image file: {str(e)}")            
            

            