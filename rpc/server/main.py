from fastapi import FastAPI
from rpc.route import router
from rpc.service import register_service

app = FastAPI()
app.include_router(router)

# Exemple de services comme dans OCaml
@register_service("ping")
def ping():
    return "pong"

@register_service("add")
def add(x: int, y: int):
    return x + y
