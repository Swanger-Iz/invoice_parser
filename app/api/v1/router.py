from api.v1.endpoints import get_fio, pages, requests
from fastapi import APIRouter
from logger import setup_logger

logger = setup_logger(__name__)

api_router = APIRouter()

# Подключаем роутеры
api_router.include_router(pages.router)
api_router.include_router(requests.router)
api_router.include_router(get_fio.router)
