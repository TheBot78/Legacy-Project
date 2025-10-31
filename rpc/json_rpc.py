from typing import Any, Optional

from pydantic import BaseModel


class RPCRequest(BaseModel):
    method: str
    params: dict[str, Any]
    id: Optional[int] = None


class RPCResponse(BaseModel):
    result: Any
    id: Optional[int] = None
