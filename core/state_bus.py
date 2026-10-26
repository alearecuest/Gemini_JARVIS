import json
import os
import time

STATE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "memory", "runtime_state.json")

class StateBus:
    """Sincroniza el estado y la telemetría de IA en tiempo real entre el Core y el HUD."""
    
    @staticmethod
    def actualizar(estado: str, detalle: str = "", ultima_respuesta: str = None, telemetria: dict = None):
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        prev = StateBus.leer()
        
        datos = {
            "estado": estado.upper(),
            "detalle": detalle,
            "timestamp": time.time(),
            "ultima_respuesta": ultima_respuesta if ultima_respuesta is not None else prev.get("ultima_respuesta", ""),
            "telemetria": telemetria if telemetria is not None else prev.get("telemetria", {
                "modelo": "En espera",
                "latencia_ms": 0,
                "tokens": 0
            })
        }

        try:
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(datos, f, ensure_ascii=False)
        except Exception:
            pass

    @staticmethod
    def leer() -> dict:
        if not os.path.exists(STATE_FILE):
            return {
                "estado": "IDLE",
                "detalle": "Sistemas en espera",
                "ultima_respuesta": "",
                "telemetria": {"modelo": "Listo", "latencia_ms": 0, "tokens": 0}
            }
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {
                "estado": "IDLE",
                "detalle": "Sistemas en espera",
                "ultima_respuesta": "",
                "telemetria": {"modelo": "Listo", "latencia_ms": 0, "tokens": 0}
            }
