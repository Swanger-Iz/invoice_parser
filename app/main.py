import io
import sys
import time
from pathlib import Path

import uvicorn

sys.path.insert(1, str(Path(__file__).parent.parent))  # Вставляю путь invoice_ai


from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from langchain.agents.structured_output import StructuredOutputValidationError
from langchain.messages import HumanMessage
from PIL import Image

from models.models import ExtractionModel
from schemas.main_schemas import ModelRequests

model_requests = []

invoice_ai_dir = Path(__file__).parent.parent
# print("Working directory:", str(invoice_ai_dir))

# Init a image
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
        print(f"Attempt - {attempt+1}\n")
        try:
            start_time = time.time()
            response = agent.invoke({"messages": messages}, config=config)
            print("=" * 20, "Success", "=" * 20)
            model_requests.append(ModelRequests(id=len(model_requests) + 1, status="good", image_bytes=config["configurable"]["image_bytes"]))
            print(f"Response time = {time.time() - start_time:.2f}")
            return response
        except StructuredOutputValidationError:
            print(f"Попытка {attempt+1}: пустой/невалидный ответ модели, повтор...")
            time.sleep(2)
        except Exception as e:
            if "TooManyRequests" in str(e):
                print("Rate limit, wait 60 sec...")
                time.sleep(60)
            else:
                raise
    print("=" * 20, "Fail", "=" * 20)
    print(f"Response time = {time.time() - start_time:.2f}")
    model_requests.append(ModelRequests(id=len(model_requests) + 1, status="bad", image_bytes=config["configurable"]["image_bytes"]))
    return None


# FastAPI
app = FastAPI()


@app.get("/", tags=["Main"], summary="Get init message")
async def root():
    return {"message": "Hi user!"}


@app.post("/images", tags=["Main"], summary="Send image and get FIO from it.")
async def get_fio(upload_file: UploadFile):
    image_in_bytes = await upload_file.read()  # читает содержимое как bytes

    response = safely_exec_agent(extractor_agent, 3, image_in_bytes=image_in_bytes)

    post_response = (
        {
            "Status": "OK",
            "Constructor_name": response["structured_response"].constructor_name,
            "Customer_name": response["structured_response"].customer_name,
        }
        if response is not None
        else {
            "Status": "OK",
            "Constructor_name": None,
            "Customer_name": None,
        }
    )

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
