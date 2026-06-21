import uvicorn
from api.v1.router import api_router
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

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
        return FileResponse("app/static/error404.html", status_code=404)
    else:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


if __name__ == "__main__":
    print("script running")

    uvicorn.run("main:app", reload=True)


##### TESTS ######
# invoice_ai_dir = Path(__file__).parent.parent
# # print("Working directory:", str(invoice_ai_dir))

# # Init a image, test
# image_path = invoice_ai_dir / "data" / "orion_agreement.png"
# image = Image.open(str(image_path)).convert("RGB")

# byte_buffer = io.BytesIO()
# image.save(byte_buffer, format=image_path.suffix[1:])
# image_bytes = byte_buffer.getvalue()
