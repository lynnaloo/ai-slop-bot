from fastapi import APIRouter, Form, HTTPException, Request, UploadFile
from typing import Annotated

from app.core.analyzer import AnalysisInput, analyze
from app.models.request import AnalysisResult
from app.models.rubric import InputType

router = APIRouter(prefix="/api/analyze", tags=["analyze"])


@router.post("", response_model=AnalysisResult)
async def analyze_content(
    request: Request,
    input_type: Annotated[InputType, Form()],
    url: Annotated[str | None, Form()] = None,
    text: Annotated[str | None, Form()] = None,
    image: UploadFile | None = None,
) -> AnalysisResult:
    gemini = request.app.state.gemini
    rubric_store = request.app.state.rubric_store

    image_bytes: bytes | None = None
    if input_type == "image":
        if image is None:
            raise HTTPException(status_code=422, detail="image file required for input_type=image")
        image_bytes = await image.read()
    elif input_type == "url":
        if not url:
            raise HTTPException(status_code=422, detail="url required for input_type=url")
    elif input_type == "text":
        if not text:
            raise HTTPException(status_code=422, detail="text required for input_type=text")

    analysis_input = AnalysisInput(
        input_type=input_type,
        url=url,
        text=text,
        image_bytes=image_bytes,
    )

    try:
        return await analyze(analysis_input, gemini, rubric_store)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
