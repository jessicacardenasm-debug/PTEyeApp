import io
import numpy as np
from pathlib import Path
from PIL import Image
import tensorflow as tf
from app.models.analysis import AnalysisResult, Finding

_MODEL_PATH = Path(__file__).parent.parent.parent / "modelo" / "densenet201.keras"
_model: tf.keras.Model | None = None

# TODO: actualizar con el orden real de class_indices del entrenamiento (son 6 clases)
_CLASS_NAMES = ["normal", "glaucoma"]
_IMG_SIZE = (224, 224)


def get_model() -> tf.keras.Model:
    global _model
    if _model is None:
        _model = tf.keras.models.load_model(str(_MODEL_PATH))
    return _model


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


def _preprocess(image_bytes: bytes) -> np.ndarray:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize(_IMG_SIZE)
    arr = tf.keras.applications.densenet.preprocess_input(np.array(image, dtype=np.float32))
    return np.expand_dims(arr, axis=0)


async def analyze_eye_image(image_bytes: bytes, patient_id: str) -> AnalysisResult:
    model = get_model()
    inputs = _preprocess(image_bytes)
    predictions = model.predict(inputs, verbose=0)

    # predictions shape: (1, num_classes) con salida softmax
    probs = predictions[0]
    best_idx = int(np.argmax(probs))
    best_conf = float(probs[best_idx])
    best_class = _CLASS_NAMES[best_idx] if best_idx < len(_CLASS_NAMES) else None

    if best_class is None or best_class not in _CLINICAL_INFO:
        return AnalysisResult(
            patient_id=patient_id,
            condition="Patología no clasificada",
            confidence=round(best_conf, 4),
            findings=[Finding(name="Hallazgo pendiente de clasificación", severity="Moderate")],
            symptoms=["Requiere evaluación oftalmológica presencial"],
            recommendation="El modelo detectó una anomalía que requiere revisión por un especialista.",
        )

    info = _CLINICAL_INFO[best_class]

    return AnalysisResult(
        patient_id=patient_id,
        condition=info["condition"],
        confidence=round(best_conf, 4),
        findings=info["findings"],
        symptoms=info["symptoms"],
        recommendation=info["recommendation"],
    )
