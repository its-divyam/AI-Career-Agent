from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/docs/openapi.json")
async def openapi_spec():
    return FileResponse(Path(__file__).parent.parent.parent / "openapi.json")
