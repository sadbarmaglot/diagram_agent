import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.staticfiles import StaticFiles
from openai import OpenAI

from agent import DiagramAgent


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_agent() -> DiagramAgent:
    return DiagramAgent(OpenAI())

@app.websocket("/ws/assistant")
async def assistant_websocket(
    websocket: WebSocket,
    agent: DiagramAgent = Depends(get_agent)
):
    await websocket.accept()

    try:
        while True:
            user_msg = await websocket.receive_text()
            if user_msg == "__ping__":
                continue
            await agent.run(websocket, user_msg)
    except WebSocketDisconnect as e:
        logger.info(f"Client disconnected: {e}")
