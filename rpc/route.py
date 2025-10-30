from fastapi import APIRouter

from rpc.json_rpc import RPCRequest, RPCResponse
from rpc.service import call_service

router = APIRouter()


@router.post("/rpc", response_model=RPCResponse)
async def rpc_endpoint(request: RPCRequest):
    try:
        result = call_service(request.method, request.params)
        return {"result": result, "id": request.id}
    except Exception as e:
        return {"result": f"Error: {e}", "id": request.id}
