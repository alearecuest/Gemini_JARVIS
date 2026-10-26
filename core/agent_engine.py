import os
import time
import datetime
import requests
from google import genai
from google.genai import types
from core.plugin_manager import PluginManager
from core.state_bus import StateBus
from core.telemetry import TelemetryLogger

class JarvisAgent:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key else None
        self.plugin_manager = PluginManager()
        self.tools = self.plugin_manager.cargar_plugins()
        
        self.modelos = self._descubrir_modelos()
        self.ollama_url = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
        self.historial = []

    def _descubrir_modelos(self) -> list:
        preferidos = [
            "gemini-3.5-flash-lite",
            "gemini-3.6-flash",
            "gemini-3.8-flash",
            "gemini-3.5-flash"
        ]
        if not self.client:
            return preferidos
        disponibles = []
        try:
            for m in self.client.models.list():
                nombre = m.name.replace("models/", "")
                if "gemini" in nombre and "flash" in nombre and "tts" not in nombre and "image" not in nombre:
                    disponibles.append(nombre)
        except Exception:
            pass

        ordenados = [m for m in preferidos if m in disponibles]
        for m in disponibles:
            if m not in ordenados:
                ordenados.append(m)
        return ordenados if ordenados else preferidos

    def _construir_config(self) -> types.GenerateContentConfig:
        ahora = datetime.datetime.now().strftime("%A %d/%m/%Y %H:%M")
        system_prompt = (
            f"Sos J.A.R.V.I.S., el asistente personal avanzado de Alejandro en Uruguay. "
            f"Fecha y hora actual del sistema: {ahora}. "
            "Hablás en español rioplatense natural (voseo), con tono profesional, ágil, conciso y leal. "
            "Tenés acceso a un ecosistema de plugins para consultar agenda, correos, clima, noticias, "
            "controlar el sistema, inspeccionar código/Git y guardar/buscar en tu memoria vectorial RAG. "
            "Cuando respondas para ser leído por voz, evitá usar asteriscos de markdown o listas largas: "
            "sé directo, conversacional y resolutivo."
        )
        return types.GenerateContentConfig(
            system_instruction=system_prompt,
            tools=self.tools,
            temperature=0.4
        )

    def _fallback_ollama_local(self, texto_usuario: str) -> str:
        """Enrutador hacia motor local (Ollama) si la nube no está disponible."""
        try:
            tags = requests.get(f"{self.ollama_url}/api/tags", timeout=2).json().get("models", [])
            if not tags:
                return None
            modelo_local = tags[0]["name"]
            print(f" > [LocalRouter]: Ejecutando con Ollama local ({modelo_local})...")
            resp = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": modelo_local,
                    "prompt": f"Sos JARVIS, asistente de Alejandro en Uruguay. Respondé breve en español rioplatense: {texto_usuario}",
                    "stream": False
                },
                timeout=30
            ).json()
            return resp.get("response", "").strip(), f"ollama/{modelo_local}"
        except Exception:
            return None, None

    def procesar_consulta(self, texto_usuario: str) -> str:
        t0 = time.perf_counter()
        StateBus.actualizar("THINKING", f"Analizando: '{texto_usuario[:35]}...'")
        config = self._construir_config()

        if self.client:
            for modelo in self.modelos:
                try:
                    print(f" > [AgentEngine]: Procesando con {modelo}...")
                    chat = self.client.chats.create(
                        model=modelo,
                        config=config,
                        history=self.historial
                    )
                    respuesta = chat.send_message(texto_usuario)
                    texto_final = (respuesta.text or "Tarea completada, Alejandro.").strip()
                    
                    latencia_ms = int((time.perf_counter() - t0) * 1000)
                    tokens_usados = 0
                    if getattr(respuesta, "usage_metadata", None):
                        tokens_usados = getattr(respuesta.usage_metadata, "total_token_count", 0) or 0

                    self.historial = chat.get_history()
                    if len(self.historial) > 24:
                        self.historial = self.historial[-24:]

                    metrica = {"modelo": modelo, "latencia_ms": latencia_ms, "tokens": tokens_usados}
                    TelemetryLogger.registrar_traza(modelo, latencia_ms, tokens_usados, texto_usuario)
                    print(f" > [Telemetry]: {modelo} | {latencia_ms} ms | {tokens_usados} tokens")
                    
                    StateBus.actualizar("IDLE", "Listo", ultima_respuesta=texto_final, telemetria=metrica)
                    return texto_final
                except Exception as e:
                    print(f"   [!] Saltando {modelo}: {str(e)[:90]}...")
                    continue

        # Fallback hacia modelo local Ollama si falló la nube
        resp_local, mod_local = self._fallback_ollama_local(texto_usuario)
        if resp_local:
            latencia_ms = int((time.perf_counter() - t0) * 1000)
            metrica = {"modelo": mod_local, "latencia_ms": latencia_ms, "tokens": 0}
            TelemetryLogger.registrar_traza(mod_local, latencia_ms, 0, texto_usuario)
            StateBus.actualizar("IDLE", "Listo (Modo Local)", ultima_respuesta=resp_local, telemetria=metrica)
            return resp_local

        error_msg = "Disculpá Alejandro, ni los servidores cloud ni el motor local están disponibles ahora."
        StateBus.actualizar("IDLE", "Error de conexión", ultima_respuesta=error_msg)
        return error_msg
