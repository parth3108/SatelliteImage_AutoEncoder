# Project Overview

This system simulates the end-to-end lifecycle of satellite image transmission:

1. Load raw datasets from satellites
2. Apply compression techniques
3. Inject artificial noise to simulate transmission errors
4. Decompress and evaluate image quality
5. Generate comprehensive reports using visual and statistical metrics

---
# Key Features

-  **Modular pipeline design** for flexibility and extensibility
-  **Simulated noise injection** to test real-world resilience
-  **Evaluation dashboard** with PSNR, SSIM, MSE, and LPIPS metrics
-  **SQLite database** to track results and manage runs
-  **Visual interface** for managing datasets and pipelines
-  **Custom pipeline execution** through configuration templates

---

⚙️ System Modules

| Module Name            | Functionality                                           |
|------------------------|---------------------------------------------------------|
| `DatasetLoader`        | Load datasets from URLs or local storage                |
| `PreProcessor`         | Convert multispectral to RGB images                     |
| `Compressor`           | Apply compression (e.g., JPEG, PNG, Autoencoder)        |
| `SimulatedNoiseInjector` | Add noise for signal degradation simulation           |
| `Decompressor`         | Restore image post-compression                          |
| `Evaluator`            | Compute evaluation metrics                              |
| `SatEval`              | Central orchestrator and database manager               |

---

🗂️ Dataset Management

- Upload datasets as `.zip` files or from URLs
- Automatically extract, preprocess, and store images
- Track metadata and execution history with RunIDs

---

## 🧪 Evaluation Metrics

| Metric     | Description                                            |
|------------|--------------------------------------------------------|
| `PSNR`     | Peak Signal-to-Noise Ratio (higher is better)         |
| `SSIM`     | Structural Similarity Index (closer to 1 is better)   |
| `MSE`      | Mean Squared Error (lower is better)                  |
| `LPIPS`    | Learned Perceptual Image Patch Similarity (lower is better) |

---

## 📊 Result Example

| RunID     | Input Size | Compressed Size | PSNR  | SSIM | MSE  |
|-----------|-------------|------------------|--------|------|------|
| `TestRun` | 2.4 MB      | 750 KB           | 41.25  | 0.89 | 12.3 |

Each execution is tracked and logged with its RunID. Metrics are stored in the database for comparison and reporting.

---

## Technologies Used

- **Python 3.9+**
- `Pillow` – image loading and saving
- `NumPy` – numerical computations
- `rasterio` – geospatial raster data
- `SQLite3` – embedded relational database
- `requests` – dataset download handling
- `tqdm` – progress tracking
- `zipfile` – archive extraction

---

## 🔄 Sample Pipeline Configuration

```python
config = [
  {
    "execution_path": "dataset_loader:load_by_url",
    "params": {
      "url": "https://example.com/dataset.zip",
      "file_name": "satellite_data.zip"
    }
  },
  {
    "execution_path": "preprocessor:convert_ms_to_rgb",
    "params": {
      "input_path": "input/",
      "output_folder": "output/",
      "bands": [3, 2, 1]
    }
  }
]
