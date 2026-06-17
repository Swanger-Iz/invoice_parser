import io
import sys
import time
from pathlib import Path

import uvicorn

sys.path.insert(1, str(Path(__file__).parent.parent))  # Вставляю путь invoice_ai


from fastapi import FastAPI, Request, UploadFile
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from langchain.agents.structured_output import StructuredOutputValidationError
from langchain.messages import HumanMessage
from PIL import Image

from models.models import ExtractionModel
from schemas.main_schemas import ModelRequests

response_list = [
    ModelRequests(id=0 + 1, status="SUCCESS", constructor_name="Кучков Игорь Маркович", customer_name="Валеев Артур Хамзадович", image_bytes=bytes(10)),
    ModelRequests(
        id=1 + 1, status="SUCCESS", constructor_name="Горемыкин Артем Динисович", customer_name="Уразбахтин Тимур Фанильевич", image_bytes=bytes(12)
    ),
]

invoice_ai_dir = Path(__file__).parent.parent
# print("Working directory:", str(invoice_ai_dir))

# Init a image, test
image_path = invoice_ai_dir / "data" / "orion_agreement.png"
image = Image.open(str(image_path)).convert("RGB")

byte_buffer = io.BytesIO()
image.save(byte_buffer, format=image_path.suffix[1:])
image_bytes = byte_buffer.getvalue()

# LLM init
extractor_agent = ExtractionModel.init_extractor_agent()


# llm params
def init_configs(image_bytes: bytes):
    messages = [HumanMessage(content_blocks=[{"type": "text", "text": "Проанализируй договор картинки полученной в битовом формате!"}])]
    config = {"configurable": {"image_bytes": image_bytes}}

    return (messages, config)


# llm invoke
def safely_exec_agent(agent, attempts=3, image_in_bytes: bytes = None):
    if image_in_bytes is None:
        return None
    messages, config = init_configs(image_bytes=image_in_bytes)
    print("Safely starting the agent")
    for attempt in range(attempts):
        start_time = time.time()
        print(f"Attempt - {attempt+1}\n")
        try:
            response = agent.invoke({"messages": messages}, config=config)
            print("=" * 20, "Success", "=" * 20)
            print(f"Response time = {time.time() - start_time:.2f}")
            return response
        except StructuredOutputValidationError:
            print(f"Попытка {attempt+1}: пустой/невалидный ответ модели, повтор...")
            print(f"Response time = {time.time() - start_time:.2f}")
            time.sleep(2)
        except Exception as e:
            if "TooManyRequests" in str(e):
                print(f"Response time = {time.time() - start_time:.2f}")
                print("Rate limit, try againg in 60 sec...")
            else:
                print("ERROR!")
                print(f"Response time = {time.time() - start_time:.2f}")
        else:
            print("ERROR!")
    print("=" * 20, "Fail", "=" * 20)
    print(f"Response time = {time.time() - start_time:.2f}")
    return None


# FastAPI
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== СТРАНИЦЫ =====
@app.get("/", tags=["Display"], summary="Get init message")
async def ui():
    return FileResponse("static/index.html")


@app.get("/recognize", tags=["Display"])
async def recognize():
    return FileResponse("static/recognize.html")


@app.get("/requests", tags=["Display"])
async def get_all_requests():
    return [{"Request ID": r.id, "Request_status": r.status, "constructor_name": r.constructor_name, "customer_name": r.customer_name} for r in response_list]


@app.get("/requests/{request_id}", tags=["Display"])
async def get_request(request_id: str):
    request_id = int(request_id) - 1
    print(f"{request_id=}")
    if request_id < 0:
        request_id = 0
    elif request_id > len(response_list) - 1:
        request_id = len(response_list) - 1

    return {
        "Request ID": response_list[request_id].id,
        "Request_status": response_list[request_id].status,
        "constructor_name": response_list[request_id].constructor_name,
        "customer_name": response_list[request_id].customer_name,
    }


# ====== ОБРАБОТКА ОШИБОК ======
@app.exception_handler(404)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 404:
        return FileResponse("static/error404.html", status_code=404)
    else:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


# ===== ЛОГИКА ======
@app.post("/images", tags=["Main"], summary="Send image and get FIO from it.")
async def get_fio(upload_file: UploadFile):
    file_size_MB = upload_file.size / 1024 / 1024
    if file_size_MB > 20:
        return {
            "Status": "FILE_IS_TOO_BIG",
            "Constructor_name": None,
            "Customer_name": None,
        }

    image_in_bytes = await upload_file.read()  # читает содержимое как bytes

    response = safely_exec_agent(extractor_agent, 3, image_in_bytes=image_in_bytes)

    response_list.append(
        ModelRequests(
            id=len(response_list) + 1,
            status=(
                "SUCCESS"
                if response["structured_response"].constructor_name is not None and response["structured_response"].customer_name is not None
                else "BAD"
            ),
            constructor_name=response["structured_response"].constructor_name if response is not None else None,
            customer_name=response["structured_response"].customer_name if response is not None else None,
            image_bytes=image_in_bytes,
        )
    )

    post_response = {
        "Status": response_list[-1].status,
        "Constructor_name": response_list[-1].constructor_name,
        "Customer_name": response_list[-1].customer_name,
    }

    print(f"Constructor_name: {post_response['Constructor_name']}, Customer_name: {post_response['Customer_name']}")
    return post_response


if __name__ == "__main__":
    print("script running")

    uvicorn.run("main:app", reload=True)
    # response = safely_exec_agent(extractor_agent, 3)
    # if response is not None:
    #     print(f"ФИО исполнителя: {response['structured_response'].constructor_name};\
    #         ФИО заказчика: {response['structured_response'].customer_name}")
    # else:
    #     print("Error!")
    # print(model_requests)
