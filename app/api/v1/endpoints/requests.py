from database.dependencies import SessionDep
from database.queries_core import DQL_queries
from fastapi import APIRouter, Response
from fastapi.exceptions import HTTPException

router = APIRouter(prefix="/requests", tags=["List of Requests"])


@router.get("/", tags=["Display"], summary="Get all requests")
async def get_all_requests(session: SessionDep):
    validated_rows = await DQL_queries.get_all_request_data(session)
    if not validated_rows:
        raise HTTPException(status_code=404, detail="No requests found")
    return validated_rows


@router.get("/{request_id}", tags=["Display"], summary="Get request by id")
async def get_request(session: SessionDep, request_id: str):
    try:
        request_id = int(request_id)
    except Exception:
        raise HTTPException(status_code=403, detail=f"Invalid {request_id} value, must be value")

    print(f"{request_id=}")

    if request_id < 0:
        raise HTTPException(status_code=404, detail=f"Request {request_id} not found")

    result = await DQL_queries.get_preview_request_data_by_id(session, request_id)

    return result


@router.get("/{request_id}/image")
async def get_request_image(session: SessionDep, request_id: str):
    image_bytes = await DQL_queries.get_image_by_id(session, request_id)
    if image_bytes is None:
        raise HTTPException(404)
    return Response(content=image_bytes, media_type="image/jpeg")
