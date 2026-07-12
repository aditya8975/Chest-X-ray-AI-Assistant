"""
Loads a chest X-ray (DICOM, JPEG, or PNG) and produces two things:

 1. A normalized 8-bit grayscale PNG for display in the UI and as the
    base image for Grad-CAM overlays.
 2. A model-ready tensor following torchxrayvision's expected
    preprocessing: normalize to roughly [-1024, 1024], center-crop to a
    square, resize to the model's input resolution, add batch/channel
    dims.

torchxrayvision models were trained on this specific normalization, so
skipping it (e.g. feeding a plain 0-1 tensor) silently produces meaningless
predictions -- getting this exactly right matters more than almost
anything else in this pipeline.
"""
import io
import numpy as np
from PIL import Image
import torch
import torchvision
from app.config import settings


def _read_pixels(raw_bytes: bytes, filename: str) -> np.ndarray:
    """Returns a 2D (grayscale) or 3D (RGB) numpy array of raw pixel
    intensities, without any normalization applied yet."""
    if filename.lower().endswith(".dcm"):
        import pydicom
        ds = pydicom.dcmread(io.BytesIO(raw_bytes))
        arr = ds.pixel_array.astype(np.float32)
        # Apply DICOM rescale slope/intercept if present (converts stored
        # pixel values to real-world intensity units).
        slope = float(getattr(ds, "RescaleSlope", 1))
        intercept = float(getattr(ds, "RescaleIntercept", 0))
        arr = arr * slope + intercept
        # MONOCHROME1 means low values = bright; invert so display is consistent.
        if getattr(ds, "PhotometricInterpretation", "") == "MONOCHROME1":
            arr = arr.max() - arr
        return arr
    else:
        img = Image.open(io.BytesIO(raw_bytes))
        return np.array(img)


def to_display_png(raw_bytes: bytes, filename: str) -> Image.Image:
    """Converts any supported input into a normalized 8-bit grayscale PIL
    image suitable for viewing and for use as the Grad-CAM overlay base."""
    arr = _read_pixels(raw_bytes, filename)
    arr = arr.astype(np.float32)
    if arr.ndim == 3:
        arr = arr.mean(axis=2)
    lo, hi = np.percentile(arr, 0.5), np.percentile(arr, 99.5)
    if hi <= lo:
        lo, hi = arr.min(), arr.max() or 1.0
    arr = np.clip((arr - lo) / (hi - lo + 1e-6), 0, 1)
    arr = (arr * 255).astype(np.uint8)
    return Image.fromarray(arr, mode="L").convert("RGB")


def to_model_tensor(display_image: Image.Image) -> torch.Tensor:
    """Takes the normalized 8-bit display image and produces the
    (1, 1, H, W) tensor torchxrayvision's model expects."""
    import torchxrayvision as xrv

    arr = np.array(display_image.convert("L")).astype(np.float32)
    arr = xrv.datasets.normalize(arr, 255)  # -> roughly [-1024, 1024]
    arr = arr[None, ...]  # (1, H, W) channel-first

    transform = torchvision.transforms.Compose([
        xrv.datasets.XRayCenterCrop(),
        xrv.datasets.XRayResizer(settings.image_size),
    ])
    arr = transform(arr)
    tensor = torch.from_numpy(arr).float()
    return tensor.unsqueeze(0)  # (1, 1, H, W)
