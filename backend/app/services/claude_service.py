import json
import base64
import anthropic
from app.config import settings
from app.models.analysis import AnalysisResult, Finding

_MOCK_RESULT = {
    "condition": "Conjuntivitis Bacteriana",
    "confidence": 0.87,
    "findings": [
        {"name": "Hiperemia Conjuntival", "severity": "Severe"},
        {"name": "Edema Palpebral", "severity": "Mild"},
        {"name": "Secreción Mucosa", "severity": "Moderate"},
    ],
    "symptoms": ["Enrojecimiento", "Prurito", "Lagrimeo", "Secreción", "Visión borrosa"],
    "recommendation": "Considerar antibióticos tópicos. Seguimiento en 72 horas.",
}

_PROMPT = """Eres un especialista en oftalmología. Analiza esta imagen ocular.
Responde ÚNICAMENTE con JSON válido con esta estructura exacta:
{
  "condition": "nombre de la patología principal detectada",
  "confidence": número entre 0.0 y 1.0,
  "findings": [{"name": "hallazgo clínico", "severity": "Mild|Moderate|Severe"}],
  "symptoms": ["síntoma1", "síntoma2"],
  "recommendation": "recomendación clínica breve"
}"""


async def analyze_eye_image(image_bytes: bytes, patient_id: str) -> AnalysisResult:
    if not settings.ANTHROPIC_API_KEY:
        data = _MOCK_RESULT.copy()
        data["patient_id"] = patient_id
        data["findings"] = [Finding(**f) for f in data["findings"]]
        return AnalysisResult(**data)

    client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    image_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")

    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_b64,
                        },
                    },
                    {"type": "text", "text": _PROMPT},
                ],
            }
        ],
    )

    data = json.loads(message.content[0].text)
    data["patient_id"] = patient_id
    data["findings"] = [Finding(**f) for f in data["findings"]]
    return AnalysisResult(**data)
