import io
import logging
import os
import time
from typing import Annotated

# import sys
# from pathlib import Path
# sys.path.insert(0, str(Path(__file__).parent.parent))
import numpy as np
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.structured_output import StructuredOutputValidationError
from langchain.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import InjectedToolArg, tool
from langchain_openrouter import ChatOpenRouter
from paddleocr import PaddleOCR
from PIL import Image

from models.config import (
    chat_model_name,
    detection_dir_path,
    doc_orientation_dir_path,
    recognition_dir_path,
    system_prompt,
)
from schemas.main_schemas import ResponseFormat

logger = logging.getLogger(__name__)


class ExtractionAgent:
    # _instanse = None
    # _initialized = False

    def __init__(self):
        load_dotenv()
        print(".env vars set")

        self.ocr_model = self._init_PaddleOCR()
        self.image_parser = self._create_parser_tool(self.ocr_model)
        self.agent = create_agent(
            model=ChatOpenRouter(model=chat_model_name, temperature=0, api_key=os.getenv("OPENROUTER_API_KEY")),
            tools=[self.image_parser],
            system_prompt=system_prompt,
            response_format=ResponseFormat,
            # debug=True,
        )

    # PaddleOCR init
    def _init_PaddleOCR(self) -> PaddleOCR:
        ocr = PaddleOCR(
            # det config
            text_detection_model_dir=detection_dir_path,
            text_detection_model_name="PP-OCRv5_server_det",
            text_det_box_thresh=0.5,
            text_det_thresh=0.3,
            text_det_unclip_ratio=1.6,  # расширение bbox (важно для плотного текста!)
            # rec config
            text_recognition_model_name="eslav_PP-OCRv5_mobile_rec",
            text_recognition_model_dir=recognition_dir_path,
            # text_recognition_model_name="PP-OCRv5_server_rec",
            text_recognition_batch_size=6,
            # Классификатор поворота строк
            doc_orientation_classify_model_dir=doc_orientation_dir_path,
            use_doc_orientation_classify=True,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            device="gpu",
        )
        return ocr

    # Langchain tools and models configuring
    def _create_parser_tool(self, ocr_model: PaddleOCR):
        @tool(description="Parse text from byted image")
        def image_parser(config: Annotated[RunnableConfig, InjectedToolArg]) -> str:
            image_bytes = config["configurable"]["image_bytes"]
            # ocr_model = config['configurable']['ocr_model']

            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            ocr_result = ocr_model.predict(np.array(image))
            ocr_text = " ".join(ocr_result[0].get("rec_texts", None))

            return ocr_text

        return image_parser

    # llm params
    def init_llm_configs(self, image_bytes: bytes):
        messages = [HumanMessage(content_blocks=[{"type": "text", "text": "Проанализируй договор картинки полученной в битовом формате!"}])]
        config = {"configurable": {"image_bytes": image_bytes}}

        return (messages, config)

    # llm invoke
    def safely_exec_agent(self, attempts=3, image_in_bytes: bytes = None):
        if image_in_bytes is None:
            return None
        messages, config = self.init_llm_configs(image_bytes=image_in_bytes)
        print("Safely starting the agent")
        for attempt in range(attempts):
            start_time = time.time()
            print(f"Attempt - {attempt+1}\n")
            try:
                response = self.agent.invoke({"messages": messages}, config=config)
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


# LLM init
extractor_agent = ExtractionAgent()
