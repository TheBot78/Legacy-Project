from pydantic import BaseModel
from typing import Any, Optional

class RPCRequest(BaseModel):
    method: str
    params: dict[str, Any]
    id: Optional[int] = None

class RPCResponse(BaseModel):
    result: Any
    id: Optional[int] = None
