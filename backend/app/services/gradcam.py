"""
Grad-CAM (Selvaraju et al., 2017) for the torchxrayvision DenseNet121.

We hook the output of `model.features` -- the final convolutional feature
map before global pooling and classification -- which is the standard
Grad-CAM target for a DenseNet-style architecture. For each requested
pathology we backprop from that pathology's output score, weight the
feature maps by the (globally-averaged) gradient, and ReLU the result to
keep only the regions that positively influenced the prediction.

This is computed per-pathology (not once per image), since each finding
can be driven by a different region of the lung fields.
"""
import numpy as np
import cv2
import torch
from PIL import Image
from app.services.model_registry import get_model, get_device


class _GradCAMHooks:
    def __init__(self, target_layer: torch.nn.Module):
        self.activations = None
        self.gradients = None
        self._fwd_handle = target_layer.register_forward_hook(self._save_activation)
        self._bwd_handle = target_layer.register_full_backward_hook(self._save_gradient)

    def _save_activation(self, module, inp, out):
        self.activations = out.detach()

    def _save_gradient(self, module, grad_in, grad_out):
        self.gradients = grad_out[0].detach()

    def remove(self):
        self._fwd_handle.remove()
        self._bwd_handle.remove()


def _get_target_layer(model):
    # torchxrayvision's DenseNet exposes the torchvision-style `.features`
    # Sequential; its output is the last conv feature map before pooling.
    if hasattr(model, "features"):
        return model.features
    raise AttributeError(
        "Could not find a convolutional feature layer named 'features' on "
        "this model. If a different torchxrayvision weight set exposes a "
        "different architecture, update _get_target_layer() to point at "
        "its final conv block."
    )


def compute_gradcam(model_tensor: torch.Tensor, pathology: str) -> np.ndarray:
    """Returns a (H, W) float array in [0, 1] -- the Grad-CAM heatmap for
    the given pathology, at the model's internal feature-map resolution
    upsampled to the model input resolution."""
    model = get_model()
    device = get_device()
    target_layer = _get_target_layer(model)

    class_idx = list(model.pathologies).index(pathology)

    hooks = _GradCAMHooks(target_layer)
    model.zero_grad()
    input_tensor = model_tensor.clone().to(device).requires_grad_(True)

    output = model(input_tensor)
    score = output[0, class_idx]
    score.backward()

    activations = hooks.activations[0]      # (C, h, w)
    gradients = hooks.gradients[0]           # (C, h, w)
    hooks.remove()

    weights = gradients.mean(dim=(1, 2))     # (C,)
    cam = torch.relu((weights[:, None, None] * activations).sum(dim=0))  # (h, w)

    cam = cam.cpu().numpy()
    if cam.max() > 0:
        cam = cam / cam.max()

    target_h, target_w = model_tensor.shape[-2], model_tensor.shape[-1]
    cam = cv2.resize(cam, (target_w, target_h))
    return cam


def overlay_heatmap(base_image: Image.Image, cam: np.ndarray, alpha: float = 0.45) -> Image.Image:
    """Overlays a Grad-CAM heatmap (values in [0,1]) onto the base display
    image using a standard jet colormap, matching the model's input
    resolution back onto the original display size."""
    base = np.array(base_image.convert("RGB").resize((cam.shape[1], cam.shape[0])))
    heatmap = cv2.applyColorMap((cam * 255).astype(np.uint8), cv2.COLORMAP_JET)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
    blended = (base.astype(np.float32) * (1 - alpha) + heatmap.astype(np.float32) * alpha).astype(np.uint8)
    return Image.fromarray(blended)
