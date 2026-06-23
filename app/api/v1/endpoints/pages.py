from fastapi import APIRouter
from fastapi.responses import FileResponse
from logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(tags=["Display"])


# ===== СТРАНИЦЫ =====
@router.get("/", tags=["Display"], summary="Get init message")
async def ui():
    return FileResponse("app/static/index/index.html")


@router.get("/recognize", tags=["Display"])
async def recognize():
    return FileResponse("app/static/recognize/recognize.html")
