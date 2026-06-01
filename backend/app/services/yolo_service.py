import io
from pathlib import Path
from PIL import Image
from ultralytics import YOLO
from app.models.analysis import AnalysisResult, Finding

_MODEL_PATH = Path(__file__).parent.parent.parent / "modelo" / "best.pt"
_model: YOLO | None = None


def get_model() -> YOLO:
    global _model
    if _model is None:
        _model = YOLO(str(_MODEL_PATH))
    return _model


# Información clínica por condición detectada
_CLINICAL_INFO = {
    "glaucoma": {
        "condition": "Glaucoma",
        "findings": [
            Finding(name="Excavación del nervio óptico aumentada", severity="Severe"),
            Finding(name="Defecto en capa de fibras nerviosas", severity="Moderate"),
            Finding(name="Presión intraocular elevada (probable)", severity="Moderate"),
        ],
        "symptoms": [
            "Pérdida periférica del campo visual",
            "Visión en túnel (estadios avanzados)",
            "Dolor ocular ocasional",
            "Halos alrededor de luces",
        ],
        "recommendation": (
            "Derivar urgentemente a oftalmología para medición de presión intraocular "
            "y campo visual. Iniciar tratamiento hipotensor ocular si se confirma diagnóstico."
        ),
    },
    "normal": {
        "condition": "Sin patología detectada",
        "findings": [
            Finding(name="Nervio óptico con apariencia normal", severity="Mild"),
            Finding(name="Relación excavación/disco dentro de límites", severity="Mild"),
        ],
        "symptoms": [
            "Sin síntomas visuales reportados",
            "Agudeza visual conservada",
        ],
        "recommendation": (
            "Fondo de ojo dentro de parámetros normales. "
            "Se recomienda control preventivo anual."
        ),
    },
}


async def analyze_eye_image(image_bytes: bytes, patient_id: str) -> AnalysisResult:
    model = get_model()

    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    results = model(image, verbose=False)

    best_class = "normal"
    best_conf = 0.0

    for result in results:
        if result.boxes is not None and len(result.boxes) > 0:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                cls_name = model.names[cls_id]
                # Prioriza glaucoma si es detectado con cualquier confianza
                if cls_name == "glaucoma" or conf > best_conf:
                    best_class = cls_name
                    best_conf = conf

    # Si no detectó nada, asumir normal con baja confianza
    if best_conf == 0.0:
        best_class = "normal"
        best_conf = 0.55

    info = _CLINICAL_INFO[best_class]

    return AnalysisResult(
        patient_id=patient_id,
        condition=info["condition"],
        confidence=round(best_conf, 4),
        findings=info["findings"],
        symptoms=info["symptoms"],
        recommendation=info["recommendation"],
    )
