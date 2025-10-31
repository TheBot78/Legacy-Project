from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from rpc.route import router
from rpc.service import register_service

app = FastAPI()
app.include_router(router)


# Custom 404 for RPC service
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content={
                "error": "Not Found",
                "detail": "Endpoint not found",
                "path": request.url.path,
            },
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail or "HTTP error", "path": request.url.path},
    )


# Exemple de services comme dans OCaml
@register_service("ping")
def ping():
    return "pong"


@register_service("add")
def add(x: int, y: int):
    return x + y
