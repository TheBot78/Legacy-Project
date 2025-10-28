import json
from typing import Any

def encode(obj: Any) -> str:
    return json.dumps(obj)

def decode(data: str) -> Any:
    return json.loads(data)
