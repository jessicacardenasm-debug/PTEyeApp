from fastapi import APIRouter, UploadFile, File, Form, Depends
from app.services.yolo_service import analyze_eye_image
from app.models.analysis import AnalysisResult
from app.dependencies import get_current_user

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResult)
async def analyze(
    patient_id: str = Form(...),
    image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    image_bytes = await image.read()
    return await analyze_eye_image(image_bytes, patient_id)
