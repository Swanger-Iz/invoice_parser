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
    try:
        uvicorn.run("main:app", host="127.0.0.1", port=8000)
    except Exception as e:
        logger.info(f"Error - {e}")
        raise


##### TESTS ######
# invoice_ai_dir = Path(__file__).parent.parent
# # logger.info("Working directory:", str(invoice_ai_dir))

# # Init a image, test
# image_path = invoice_ai_dir / "data" / "orion_agreement.png"
# image = Image.open(str(image_path)).convert("RGB")

# byte_buffer = io.BytesIO()
# image.save(byte_buffer, format=image_path.suffix[1:])
# image_bytes = byte_buffer.getvalue()
