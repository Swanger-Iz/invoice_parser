import io
import sys
import time
import uuid
from pathlib import Path
from typing import Literal

from langchain.agents.structured_output import StructuredOutputValidationError
from langchain.messages import HumanMessage
from PIL import Image
from pydantic import BaseModel

sys.path.insert(1, str(Path(__file__).parent.parent))  # Вставляю путь invoice_ai

from models.models import ExtractionModel


# Caching
class ModelRequests(BaseModel):
    id: str
    status: Literal["good", "bad"]
    image_bytes: bytes


model_requests = []

invoice_ai_dir = Path(__file__).parent.parent
print("Working directory:", str(invoice_ai_dir))

# Init a image
image_path = invoice_ai_dir / "data" / "orion_agreement.png"
image = Image.open(str(image_path)).convert("RGB")

byte_buffer = io.BytesIO()
image.save(byte_buffer, format=image_path.suffix[1:])
image_bytes = byte_buffer.getvalue()

# LLM init
extractor_agent = ExtractionModel.init_extractor_agent()

# llm params
messages = [HumanMessage(content_blocks=[{"type": "text", "text": "Проанализируй договор картинки полученной в битовом формате!"}])]
config = {"configurable": {"image_bytes": image_bytes}}


# llm invoke
def safely_exec_agent(agent, attempts=3):
    for attempt in range(attempts):
        try:
            response = agent.invoke({"messages": messages}, config=config)
            print("\t---!!Success!!---")
            model_requests.append(ModelRequests(id=uuid.uuid2(), status="good", image_bytes=config["configurable"]["image_bytes"]))
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
        model_requests.append(ModelRequests(id=uuid.uuid2(), status="bad", image_bytes=config["configurable"]["image_bytes"]))
        return None


print("Safely starting the agent")
response = safely_exec_agent(extractor_agent, 3)
if response is not None:
    print(f"ФИО исполнителя: {response['structured_response'].constructor_name};\
        ФИО заказчика: {response['structured_response'].customer_name}")
else:
    print("Error!")
