from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


# Define a request model
class RPCRequest(BaseModel):
    method: str
    params: dict


# Define a response model
class RPCResponse(BaseModel):
    result: str


@app.post("/rpc", response_model=RPCResponse)
async def rpc_endpoint(request: RPCRequest):
    """
    A simple RPC endpoint that echoes the method name and parameters.
    """
    # Example logic for the RPC method
    if request.method == "ping":
        return {"result": "pong"}
    elif request.method == "echo":
        return {"result": f"Echo: {request.params}"}
    else:
        return {"result": f"Unknown method: {request.method}"}
