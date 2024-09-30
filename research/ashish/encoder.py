import cv2
import numpy as np
from keras.models import load_model
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import structural_similarity as ssim
import matplotlib.pyplot as plt

# Load the model
autoencoder = load_model('autoencoder_model.h5')

# Load and preprocess the image
original_img = cv2.imread('orignal.jpg', cv2.IMREAD_GRAYSCALE)
if original_img is None:
    raise FileNotFoundError("Image not found. Ensure the file path is correct.")

# Resize the image to 28x28 (assumed input size for training) and normalize
resized_img = cv2.resize(original_img, (28, 28)).astype('float32') / 255.0
flattened_img = resized_img.flatten()
flattened_img = np.expand_dims(flattened_img, axis=0)  # Add batch dimension

# Predict using the autoencoder
compressed_img = autoencoder.predict(flattened_img)
decompressed_img = autoencoder.predict(compressed_img)
decompressed_img_reshaped = decompressed_img.reshape((28, 28))

# Calculate PSNR and SSIM
psnr_value = psnr(resized_img, decompressed_img_reshaped, data_range=resized_img.max() - resized_img.min())
ssim_value, _ = ssim(resized_img, decompressed_img_reshaped, full=True, data_range=resized_img.max() - resized_img.min())

# Visualize original, compressed, and decompressed images
fig, axes = plt.subplots(1, 3, figsize=(10, 5))
axes[0].imshow(original_img, cmap='gray')
axes[0].set_title('Original Image')
axes[0].axis('off')

axes[1].imshow(resized_img, cmap='gray')
axes[1].set_title('Resized Image')
axes[1].axis('off')

axes[2].imshow(decompressed_img_reshaped, cmap='gray')
axes[2].set_title('Decompressed Image')
axes[2].axis('off')

plt.show()

# Calculate and show the error image
error_image = np.abs(resized_img - decompressed_img_reshaped)
plt.figure(figsize=(5, 5))
plt.imshow(error_image, cmap='hot')
plt.colorbar()
plt.title('Error Image')
plt.show()

print(f"Autoencoder PSNR: {psnr_value}, SSIM: {ssim_value}")
