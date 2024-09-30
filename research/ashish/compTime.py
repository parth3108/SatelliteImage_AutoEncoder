from PIL import Image
import time

# Load the original image
image = Image.open('C:/workspace/Masters/Assignments/TIP/orignal.jpg')

# Compress using JPEG
start_time = time.time()
image.save('compressed_jpeg.jpg', format='JPEG', quality=30, optimize=True)
end_time = time.time()
jpeg_time = end_time - start_time
print(f"JPEG Compression time: {jpeg_time} seconds")

# Compress using WebP
start_time = time.time()
image.save('compressed_webp.webp', format='WEBP', quality=30, optimize=True)
end_time = time.time()
webp_time = end_time - start_time
print(f"WebP Compression time: {webp_time} seconds")

# Compress using PNG (lossless)
start_time = time.time()
image.save('compressed_png.png', format='PNG', optimize=True)
end_time = time.time()
png_time = end_time - start_time
print(f"PNG Compression time: {png_time} seconds")

# Summary of times
print(f"\nSummary of Compression Times:")
print(f"JPEG Compression: {jpeg_time:.4f} seconds")
print(f"WebP Compression: {webp_time:.4f} seconds")
print(f"PNG Compression: {png_time:.4f} seconds")
