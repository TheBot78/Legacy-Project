import uvicorn
from rpc.server.main import app

def run(host="0.0.0.0", port=8080):
    uvicorn.run(app, host=host, port=port)
