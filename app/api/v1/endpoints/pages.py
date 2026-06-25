from fastapi import APIRouter, Response
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse
from logger import setup_logger
from storage import task_storage

logger = setup_logger(__name__)

router = APIRouter(tags=["Display"])


# ===== СТРАНИЦЫ =====
@router.get("/", tags=["Display"], summary="Get init message")
async def ui():
    return FileResponse("app/static/index/index.html")


@router.get("/recognize", tags=["Display"])
async def recognize():
    return FileResponse("app/static/recognize/recognize.html")


@router.get("/requests")
async def requests_page():
    return FileResponse("app/static/requests/requests.html")


@router.get("/status/{task_id}")
async def get_status(task_id: str):
    status = task_storage.get(task_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"task_id": task_id, "status": status}


@router.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)  # No Content, браузер поймёт
