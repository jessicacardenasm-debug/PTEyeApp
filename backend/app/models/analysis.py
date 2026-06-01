from pydantic import BaseModel
from typing import List


class Finding(BaseModel):
    name: str
    severity: str  # Mild | Moderate | Severe


class AnalysisResult(BaseModel):
    patient_id: str
    condition: str
    confidence: float
    findings: List[Finding]
    symptoms: List[str]
    recommendation: str
    disclaimer: str = (
        "Este análisis es una pre-clasificación de IA. "
        "Se requiere validación y correlación con el expediente clínico."
    )
