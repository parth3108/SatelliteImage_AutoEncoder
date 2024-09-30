from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import structural_similarity as ssim
import cv2

original = cv2.imread('C:/workspace/Masters/Assignments/TIP/orignal.jpg', cv2.IMREAD_GRAYSCALE)
compressed = cv2.imread('C:/workspace/Masters/Assignments/TIP/compressed.jpg', cv2.IMREAD_GRAYSCALE)


psnr_value = psnr(original, compressed)
ssim_value, _ = ssim(original, compressed, full=True)

print(f"PSNR: {psnr_value}, SSIM: {ssim_value}")
