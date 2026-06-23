import asyncio
import hashlib

from database.dependencies import SessionDep
from database.queries_core import DQL_queries
from database.queries_orm import DML_queries
from fastapi import APIRouter, UploadFile
from fastapi.exceptions import HTTPException
from logger import setup_logger
from models.models import extractor_agent
from schemas.main_schemas import RequestPreviewDTO, RequestsPostDTO

logger = setup_logger(__name__)


router = APIRouter(prefix="/api")


@router.post("/get_fio", status_code=201, tags=["Recognize"], summary="Send image and get FIO from it.")
async def get_fio(session: SessionDep, upload_file: UploadFile) -> RequestPreviewDTO:
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

    logger.info("No image in DB, launching a model\n")
    # Main Logic
    try:
        response = await asyncio.wait_for(extractor_agent.safely_exec_agent(3, image_in_bytes=image_in_bytes), timeout=60.0)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Processing timeout: model took too long")

    # Assume model calling fails, i.e. we cannot access to the model
    if response is None:
        raise HTTPException(status_code=503, detail="Cannot access to the model for extracting FIO, please try later!")

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

    return RequestPreviewDTO.model_validate(row, from_attributes=True)
