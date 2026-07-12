"""Runs the pretrained classifier and splits results into positive /
borderline / all findings based on the configured thresholds."""
import torch
from app.config import settings
from app.services.model_registry import get_model, get_device


@torch.no_grad()
def run_inference(model_tensor: torch.Tensor) -> dict:
    model = get_model()
    device = get_device()
    model_tensor = model_tensor.to(device)

    outputs = model(model_tensor)  # (1, num_pathologies), already sigmoid-activated by xrv
    probs = outputs[0].cpu().numpy()

    findings = {}
    for pathology, prob in zip(model.pathologies, probs):
        if not pathology:  # xrv pads unused label slots with empty strings for some weight sets
            continue
        findings[pathology] = round(float(prob), 4)

    positive = {k: v for k, v in findings.items() if v >= settings.finding_threshold}
    borderline = {
        k: v for k, v in findings.items()
        if settings.borderline_threshold <= v < settings.finding_threshold
    }

    positive = dict(sorted(positive.items(), key=lambda x: -x[1]))
    borderline = dict(sorted(borderline.items(), key=lambda x: -x[1]))

    return {
        "findings": findings,
        "positive_findings": positive,
        "borderline_findings": borderline,
        "overall_confidence": round(float(max(probs)) if len(probs) else 0.0, 4),
    }
