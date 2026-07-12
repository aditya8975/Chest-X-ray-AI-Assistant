"""
Orchestrates the full per-study pipeline:

  1. Load & normalize the uploaded image (DICOM or standard formats)
  2. Run the classifier -> per-pathology probabilities
  3. Compute Grad-CAM heatmaps for the top surfaced findings
  4. Generate the draft report

Grad-CAM is capped at `max_heatmaps_per_study` findings (positive findings
first, then borderline) since each heatmap requires its own backward pass.
"""
from app.config import settings
from app.services import preprocessing, inference, gradcam, report_generator
from app.utils.image_utils import save_heatmap


def run_pipeline(raw_bytes: bytes, filename: str, stem: str, patient_ref: str | None) -> dict:
    display_image = preprocessing.to_display_png(raw_bytes, filename)
    model_tensor = preprocessing.to_model_tensor(display_image)

    result = inference.run_inference(model_tensor)

    heatmap_targets = list(result["positive_findings"].keys())
    for pathology in result["borderline_findings"]:
        if len(heatmap_targets) >= settings.max_heatmaps_per_study:
            break
        heatmap_targets.append(pathology)
    heatmap_targets = heatmap_targets[: settings.max_heatmaps_per_study]

    heatmap_paths = {}
    for pathology in heatmap_targets:
        cam = gradcam.compute_gradcam(model_tensor, pathology)
        overlay = gradcam.overlay_heatmap(display_image, cam)
        heatmap_paths[pathology] = save_heatmap(overlay, stem, pathology)

    model_version = settings.xrv_weights

    report_text = report_generator.generate_report(
        positive_findings=result["positive_findings"],
        borderline_findings=result["borderline_findings"],
        model_version=model_version,
        patient_ref=patient_ref,
    )

    return {
        "display_image": display_image,
        "findings": result["findings"],
        "positive_findings": result["positive_findings"],
        "borderline_findings": result["borderline_findings"],
        "overall_confidence": result["overall_confidence"],
        "heatmaps": heatmap_paths,
        "report_text": report_text,
        "model_version": model_version,
    }
