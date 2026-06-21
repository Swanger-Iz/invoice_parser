from fastapi import APIRouter, UploadFile
from fastapi.exceptions import HTTPException
from models.models import extractor_agent

router = APIRouter(prefix="/api")


@router.post("/get_fio", tags=["Main"], summary="Send image and get FIO from it.")
async def get_fio(upload_file: UploadFile):

    # Checking a size
    file_size_MB = upload_file.size / 1024 / 1024
    if file_size_MB > 20:
        raise HTTPException(status_code=415, detail=f"Unsupported file type: {upload_file.content_type}")

    # Logging
    print("FILE SIZE:", file_size_MB, f"\nFILE NAME: {upload_file.filename}")
    file_format = upload_file.filename.split(".")[-1]

    if file_format not in ["jpg", "jpeg", "png"]:
        return {
            "Status": "WRONG_FILE_FORMAT",
            "Constructor_name": None,
            "Customer_name": None,
        }

    # Main Logic
    image_in_bytes = await upload_file.read()  # читает содержимое как bytes

    response = extractor_agent.safely_exec_agent(3, image_in_bytes=image_in_bytes)

    return None
    # response_list.append(
    #     ModelRequests(
    #         id=len(response_list) + 1,
    #         status=(
    #             "SUCCESS"
    #             if response["structured_response"].constructor_name is not None and response["structured_response"].customer_name is not None
    #             else "BAD"
    #         ),
    #         constructor_name=response["structured_response"].constructor_name if response is not None else None,
    #         customer_name=response["structured_response"].customer_name if response is not None else None,
    #         image_bytes=image_in_bytes,
    #     )
    # )

    # post_response = {
    #     "Status": response_list[-1].status,
    #     "Constructor_name": response_list[-1].constructor_name,
    #     "Customer_name": response_list[-1].customer_name,
    # }

    # print(f"Constructor_name: {post_response['Constructor_name']}, Customer_name: {post_response['Customer_name']}")
    # return post_response
