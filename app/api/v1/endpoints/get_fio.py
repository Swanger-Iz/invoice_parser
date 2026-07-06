import asyncio
import hashlib
import uuid

from database.dependencies import SessionDep
from database.queries_core import DQL_queries
from database.queries_orm import DML_queries
from fastapi import APIRouter, BackgroundTasks, UploadFile
from fastapi.exceptions import HTTPException
from logger import setup_logger
from models.models import extractor_agent
from schemas.main_schemas import RequestPreviewDTO, RequestsPostDTO, TaskResponseDTO
from storage import task_storage

logger = setup_logger(__name__)


router = APIRouter(prefix="/api/v1", tags=["Recognize"])


async def launch_model(image_in_bytes: bytes, session: SessionDep, task_id: str) -> RequestPreviewDTO | None:
    # Main Logic
    try:
        response = await asyncio.wait_for(extractor_agent.safely_exec_agent(3, image_in_bytes=image_in_bytes), timeout=60.0)
        task_storage[task_id] = "success"
    except asyncio.TimeoutError:
        task_storage[task_id] = "error"
        return
        # raise HTTPException(status_code=504, detail="Processing timeout: model took too long")
    except Exception as e:  # ловим всё остальное включая UnknownModelCallingError
        task_storage[task_id] = "error"
        logger.error(f"Task {task_id} failed: {e}")
        return

    # Assume model calling fails, i.e. we cannot access to the model
    if response is None:
        task_storage[task_id] = "error"
        return
        # raise HTTPException(status_code=503, detail="Cannot access to the model for extracting FIO, please try later!")

    # Success extraction, create an object for returning and writing in DB
    row = RequestsPostDTO(
        status="SUCCESS",
        image_bytes=image_in_bytes,
        image_hash=hashlib.sha256(image_in_bytes).hexdigest(),
        constructor_name=response["structured_response"].constructor_name,
        customer_name=response["structured_response"].customer_name,
    )
    # Writing into DB
    await DML_queries.insert_new_data_to_user_requests(row=row, session=session)
    logger.info("SUCCES recognition, row was added in DB")
    return RequestPreviewDTO.model_validate(row, from_attributes=True)


@router.post("/get_fio", status_code=202, summary="Send image and get FIO from it.")
async def get_fio(upload_file: UploadFile, session: SessionDep, bg_tasks: BackgroundTasks) -> RequestPreviewDTO | TaskResponseDTO:
    # Checking a size
    file_size_MB = upload_file.size / 1024 / 1024
    if file_size_MB > 20:
        raise HTTPException(status_code=415, detail="File is too big!")

    # Logging
    logger.info(f"FILE SIZE: {file_size_MB:.2f} MB")
    logger.info(f"\nFILE NAME: {upload_file.filename}")

    file_format = upload_file.filename.split(".")[-1].strip().lower()

    if file_format not in ["jpg", "jpeg", "png"]:
        raise HTTPException(status_code=415, detail=f"Unsupported file type: {upload_file.content_type}")

    image_in_bytes = await upload_file.read()  # читает содержимое как bytes

    ## Caching
    cached = await DQL_queries.get_image_by_hash(session, input_hash=hashlib.sha256(image_in_bytes).hexdigest())
    if cached:
        logger.info("The image in DB retruned from DB\n")
        return RequestPreviewDTO.model_validate(cached, from_attributes=True)

    logger.info("No image in DB, sent request to a model\n")

    task_id = str(uuid.uuid4())
    task_storage[task_id] = "in_process"
    bg_tasks.add_task(launch_model, image_in_bytes, session, task_id)

    logger.info(f"Endpoint: /api/v1, ended and launching bg_task: {task_id}")
    return TaskResponseDTO.model_validate({"task_id": task_id, "status": "in_process"}, from_attributes=True)
