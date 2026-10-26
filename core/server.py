import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from core.agent_engine import JarvisAgent
from core.voice_engine import VoiceEngine
from core.state_bus import StateBus

app = FastAPI(title="OpenJarvis Core Server (Alejandro Edition)", version="2.1.0")

agent = None
voice = None

class AskRequest(BaseModel):
    prompt: str
    speak: bool = True

@app.on_event("startup")
def startup_event():
    global agent, voice
    agent = JarvisAgent()
    voice = VoiceEngine()
    StateBus.actualizar("IDLE", "Servidor FastAPI en línea")

@app.get("/v1/status")
def get_status():
    estado = StateBus.leer()
    return {
        "status": "online",
        "engine_state": estado,
        "models_available": agent.modelos if agent else [],
        "active_plugins": list(agent.plugin_manager.tool_map.keys()) if agent else []
    }

@app.post("/v1/ask")
def ask_jarvis(req: AskRequest):
    respuesta = agent.procesar_consulta(req.prompt)
    if req.speak and voice:
        voice.hablar(respuesta)
    return {"prompt": req.prompt, "response": respuesta, "state": StateBus.leer()}

@app.websocket("/ws/state")
async def websocket_state(websocket: WebSocket):
    """Stream de estado en tiempo real a 20 FPS para el HUD o clientes web."""
    await websocket.accept()
    ultimo_enviado = None
    try:
        while True:
            actual = StateBus.leer()
            if actual != ultimo_enviado:
                await websocket.send_json(actual)
                ultimo_enviado = actual
            await asyncio.sleep(0.05)
    except WebSocketDisconnect:
        pass
