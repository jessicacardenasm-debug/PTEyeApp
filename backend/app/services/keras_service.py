import io
import numpy as np
from pathlib import Path
from PIL import Image
import tensorflow as tf
from app.models.analysis import AnalysisResult, Finding

_MODEL_PATH = Path(__file__).parent.parent.parent / "modelo" / "densenet201.keras"
_model: tf.keras.Model | None = None

# Orden alfabético por defecto de flow_from_directory:
# 0=AMD, 1=cataract, 2=diabetic_retinopathy, 3=glaucoma, 4=hypertension, 5=normal
# TODO: verificar con train_generator.class_indices si el orden difiere
_CLASS_NAMES = ["AMD", "cataract", "diabetic_retinopathy", "glaucoma", "hypertension", "normal"]
_IMG_SIZE = (224, 224)


def get_model() -> tf.keras.Model:
    global _model
    if _model is None:
        _model = tf.keras.models.load_model(str(_MODEL_PATH))
    return _model


_CLINICAL_INFO = {
    "AMD": {
        "condition": "Degeneración Macular Asociada a la Edad (DMAE)",
        "findings": [
            Finding(name="Drusas en mácula", severity="Moderate"),
            Finding(name="Alteraciones en epitelio pigmentario retiniano", severity="Moderate"),
            Finding(name="Posible neovascularización coroidea", severity="Severe"),
        ],
        "symptoms": [
            "Visión central borrosa o distorsionada",
            "Manchas oscuras en el centro del campo visual",
            "Dificultad para leer o reconocer rostros",
            "Metamorfopsia (líneas rectas que se ven onduladas)",
        ],
        "recommendation": (
            "Derivar a oftalmología para tomografía de coherencia óptica (OCT) y angiografía. "
            "Evaluar tratamiento con antiangiogénicos intravítreos si se confirma forma húmeda."
        ),
    },
    "cataract": {
        "condition": "Catarata",
        "findings": [
            Finding(name="Opacidad del cristalino", severity="Moderate"),
            Finding(name="Reducción de transparencia de medios oculares", severity="Moderate"),
        ],
        "symptoms": [
            "Visión borrosa o nublada progresiva",
            "Sensibilidad aumentada a la luz y deslumbramiento",
            "Halos alrededor de luces",
            "Cambios frecuentes en la graduación óptica",
        ],
        "recommendation": (
            "Derivar a oftalmología para evaluación de agudeza visual y biomicroscopía. "
            "Considerar cirugía de facoemulsificación con implante de lente intraocular."
        ),
    },
    "diabetic_retinopathy": {
        "condition": "Retinopatía Diabética",
        "findings": [
            Finding(name="Microaneurismas retinianos", severity="Moderate"),
            Finding(name="Exudados duros y/o algodonosos", severity="Moderate"),
            Finding(name="Hemorragias retinianas", severity="Severe"),
        ],
        "symptoms": [
            "Visión fluctuante",
            "Manchas oscuras o cuerpos flotantes",
            "Visión borrosa",
            "Pérdida de visión en estadios avanzados",
        ],
        "recommendation": (
            "Derivar urgentemente a oftalmología para clasificación de severidad y OCT macular. "
            "Optimizar control glucémico y tensión arterial. Evaluar fotocoagulación o antiangiogénicos."
        ),
    },
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
    "hypertension": {
        "condition": "Retinopatía Hipertensiva",
        "findings": [
            Finding(name="Estrechamiento arteriolar generalizado", severity="Moderate"),
            Finding(name="Cruces arteriovenosos patológicos", severity="Moderate"),
            Finding(name="Exudados y/o hemorragias en llama", severity="Severe"),
        ],
        "symptoms": [
            "Generalmente asintomática en estadios iniciales",
            "Visión borrosa en casos severos",
            "Cefalea asociada a hipertensión",
        ],
        "recommendation": (
            "Control urgente de presión arterial. Derivar a cardiología y oftalmología. "
            "Seguimiento estrecho del fondo de ojo según grado de retinopatía (clasificación Keith-Wagener)."
        ),
    },
    "normal": {
        "condition": "Sin patología detectada",
        "findings": [
            Finding(name="Nervio óptico con apariencia normal", severity="Mild"),
            Finding(name="Relación excavación/disco dentro de límites", severity="Mild"),
            Finding(name="Retina sin lesiones evidentes", severity="Mild"),
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
