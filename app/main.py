import argparse

import uvicorn
from api.v1.router import api_router
from custom_errors import (
    InsertingIntoDBError,
    ModelServerError,
    NoneError,
    UnknownModelCallingError,
)
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from logger import setup_logger

logger = setup_logger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--mode", default="local", choices=["docker", "local"])

# FastAPI
app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)


# ====== ОБРАБОТКА ОШИБОК ======
@app.exception_handler(404)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 404:
        return FileResponse("app/static/404/404.html", status_code=404)
    else:
        return exc


@app.exception_handler(NoneError)
async def none_error_handler(request: Request, exc: HTTPException):
    JSONResponse(status_code=404, content={"error": "Invalid input", "detail": str(exc), "type": "NoneError"})


@app.exception_handler(InsertingIntoDBError)
async def inserting_into_db_handler(request: Request, exc: HTTPException):
    JSONResponse(status_code=500, content={"error": "Cannot insert into DB", "detail": str(exc), "type": "InsertingIntoDBError"})


@app.exception_handler(ModelServerError)
async def error_handler(request: Request, exc: HTTPException):
    JSONResponse(status_code=503, content={"error": "Cannot send to server for detecting", "detail": str(exc), "type": "ModelServerError"})


@app.exception_handler(UnknownModelCallingError)
async def model_server_error_handler(request: Request, exc: HTTPException):
    JSONResponse(status_code=500, content={"error": "Unknown Error while sending request", "detail": str(exc), "type": "UnknownModelCallingError"})


if __name__ == "__main__":
    args = parser.parse_args()
    host = "0.0.0.0" if args.mode == "docker" else "127.0.0.1"
    try:
        logger.info(f"App runs in {args.mode} mode")
        uvicorn.run("main:app", host=host, port=8000)
    except Exception as e:
        logger.info(f"Error - {e}")
        raise
