from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
import base64
import cv2
import numpy as np

# Ensure to use a non-GUI backend
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from skimage.metrics import peak_signal_noise_ratio as psnr, structural_similarity as ssim

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/process-image', methods=['POST'])
def process_image():
    try:
        image_file = request.files['image']
        compression_type = request.form.get('compressionType')
        quality = int(request.form.get('quality'))

        # Convert image to a numpy array for processing
        image = Image.open(image_file)
        original = np.array(image)

        # Perform multiple compressions (e.g., JPEG and self-developed)
        compressed_images = []
        metrics = []

        # JPEG compression
        compressed_img = compress_jpeg(original, quality)
        compressed_images.append(encode_image(compressed_img))
        metrics.append({
            'technique': f'JPEG Quality {quality}',
            'psnr': psnr(original, compressed_img),
            'ssim': calculate_ssim(original, compressed_img)
        })

        # Self-developed compression technique (basic resizing)
        resized = cv2.resize(original, (25, 25))  # Downscale
        resized = cv2.resize(resized, (original.shape[1], original.shape[0]))  # Upscale back to original
        compressed_images.append(encode_image(resized))
        metrics.append({
            'technique': 'Self Developed (Downsample & Upsample)',
            'psnr': psnr(original, resized),
            'ssim': calculate_ssim(original, resized)
        })

        # Create statistics graph
        graph = create_statistics_graph(metrics)

        # Noise visualization
        noise_img = create_noise_image(original, decode_image(compressed_images[0]))  # Compare with first compressed image

        return jsonify({
            'compressed_images': compressed_images,
            'metrics': metrics,
            'graph': graph,
            'noise': noise_img
        })
    except Exception as e:
        print(f"An error occurred: {e}")  # Log the error to the console for debugging
        return jsonify({"error": "An error occurred while processing the image"}), 500

def compress_jpeg(image, quality):
    # Compress image to JPEG with a specified quality
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    _, compressed_img = cv2.imencode('.jpg', image, encode_param)
    return cv2.imdecode(compressed_img, 1)

def encode_image(image):
    # Encode image to base64 string
    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer).decode('utf-8')

def calculate_ssim(original, compressed_img):
    # Ensure images have a minimum size for SSIM calculation
    min_size = 7
    height, width = original.shape[:2]

    # If image is smaller than minimum size, resize it
    if height < min_size or width < min_size:
        original = cv2.resize(original, (max(width, min_size), max(height, min_size)))
        compressed_img = cv2.resize(compressed_img, (max(width, min_size), max(height, min_size)))

    # Calculate SSIM with a smaller window size
    return ssim(original, compressed_img, win_size=3, channel_axis=-1)

def create_statistics_graph(metrics):
    # Create a bar graph comparing PSNR values of different compression techniques
    techniques = [m['technique'] for m in metrics]
    psnr_values = [m['psnr'] for m in metrics]

    plt.figure()
    plt.bar(techniques, psnr_values)
    plt.title('PSNR Comparison of Compression Techniques')
    plt.xlabel('Techniques')
    plt.ylabel('PSNR')

    # Save the graph to a buffer and encode as base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    graph = base64.b64encode(buf.getvalue()).decode('utf-8')
    return graph

def create_noise_image(original, compressed_img):
    # Calculate and visualize noise between original and compressed image
    noise = cv2.absdiff(original, compressed_img)
    _, noise_encoded = cv2.imencode('.png', noise)
    return base64.b64encode(noise_encoded).decode('utf-8')

def decode_image(image_b64):
    # Decode base64 string to an OpenCV image
    image_data = base64.b64decode(image_b64)
    np_arr = np.frombuffer(image_data, np.uint8)
    return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

if __name__ == '__main__':
    app.run(debug=True)
