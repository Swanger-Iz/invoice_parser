import os

from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter

load_dotenv()

tencent_model = "tencent/hy3:free"
openai_model = "openai/gpt-oss-120b:free"
openai_model2 = "openai/gpt-oss-20b:free"

llm = ChatOpenRouter(model=openai_model2, api_key=os.getenv("OPENROUTER_API_KEY"), temperature=0)

response = llm.invoke("Hello")
print(response.content)
print(llm.profile)
