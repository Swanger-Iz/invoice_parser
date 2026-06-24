from database.dependencies import SessionDep
from database.queries_core import DQL_queries
from fastapi import APIRouter, Response
from fastapi.exceptions import HTTPException
from logger import setup_logger
from schemas.main_schemas import RequestPreviewDTO

logger = setup_logger(__name__)

router = APIRouter(prefix="/requests", tags=["List of Requests"])


@router.get("/", summary="Get all requests")
async def get_all_requests(session: SessionDep) -> list[RequestPreviewDTO]:
    validated_rows = await DQL_queries.get_all_request_data(session)
    if validated_rows is None:
        raise HTTPException(status_code=404, detail="No requests found")
    return validated_rows


@router.get("/{request_id}", summary="Get request by id")
async def get_request(session: SessionDep, request_id: str) -> RequestPreviewDTO | None:
    try:
        request_id = int(request_id)
    except Exception:
        raise HTTPException(status_code=403, detail=f"Invalid {request_id} value, must be value")

    logger.info(f"{request_id=}")

    if request_id < 0:
        raise HTTPException(status_code=404, detail=f"Request {request_id} must be not negative number")

    result = await DQL_queries.get_preview_request_data_by_id(session, request_id)

    if result is None:
        raise HTTPException(status_code=404, detail="No requests found")

    return result


@router.get("/{request_id}/image")
async def get_request_image(session: SessionDep, request_id: str):
    try:
        request_id = int(request_id)
    except Exception:
        raise HTTPException(status_code=403, detail=f"Invalid {request_id} value, must be numeric")

    response = await DQL_queries.get_image_by_id(session, request_id)
    image_bytes = response.image_bytes

    if image_bytes is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return Response(content=image_bytes, media_type="image/png")
