"""
Lazy, process-wide singleton for the torchxrayvision classification model.

Loaded once on first use and reused for every subsequent request so we're
not re-loading ~30M parameters from disk on every upload.
"""
import threading
import torch
from app.config import settings

_lock = threading.Lock()
_registry: dict = {}


def get_device() -> str:
    if settings.force_cpu:
        return "cpu"
    return "cuda" if torch.cuda.is_available() else "cpu"


def get_model():
    """Returns the pretrained torchxrayvision DenseNet121 classifier.

    Weights download automatically from the torchxrayvision release the
    first time this runs (a few hundred MB) and are cached under
    ~/.torchxrayvision afterwards.
    """
    if "model" not in _registry:
        with _lock:
            if "model" not in _registry:
                import torchxrayvision as xrv
                model = xrv.models.DenseNet(weights=settings.xrv_weights)
                model.to(get_device())
                model.eval()
                _registry["model"] = model
    return _registry["model"]


def get_pathologies() -> list[str]:
    model = get_model()
    return list(model.pathologies)
