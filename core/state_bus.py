import json
import os
import time

STATE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "memory", "runtime_state.json")

class StateBus:
    """Sincroniza el estado en tiempo real entre el Core de IA/Voz y el HUD gráfico."""
    
    @staticmethod
    def actualizar(estado: str, detalle: str = "", ultima_respuesta: str = None):
        """
        Estados válidos: 'IDLE', 'LISTENING', 'THINKING', 'SPEAKING'
        """
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        datos = {
            "estado": estado.upper(),
            "detalle": detalle,
            "timestamp": time.time()
        }
        if ultima_respuesta is not None:
            datos["ultima_respuesta"] = ultima_respuesta
        elif os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    prev = json.load(f)
                    datos["ultima_respuesta"] = prev.get("ultima_respuesta", "")
            except Exception:
                datos["ultima_respuesta"] = ""

        try:
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(datos, f, ensure_ascii=False)
        except Exception:
            pass

    @staticmethod
    def leer() -> dict:
        if not os.path.exists(STATE_FILE):
            return {"estado": "IDLE", "detalle": "Sistemas en espera", "ultima_respuesta": ""}
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"estado": "IDLE", "detalle": "Sistemas en espera", "ultima_respuesta": ""}