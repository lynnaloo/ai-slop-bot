from fastapi import APIRouter, Request

from app.models.rubric import Rubric

router = APIRouter(prefix="/api/rubric", tags=["rubric"])


@router.get("", response_model=Rubric)
async def get_rubric(request: Request) -> Rubric:
    return request.app.state.rubric_store.rubric


@router.post("/reload", response_model=Rubric)
async def reload_rubric(request: Request) -> Rubric:
    return request.app.state.rubric_store.reload()
