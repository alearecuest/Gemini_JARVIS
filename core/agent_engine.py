import os
import datetime
from google import genai
from google.genai import types
from core.plugin_manager import PluginManager
from core.state_bus import StateBus

class JarvisAgent:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("No se encontró la variable de entorno GEMINI_API_KEY.")
            
        self.client = genai.Client(api_key=api_key)
        self.plugin_manager = PluginManager()
        self.tools = self.plugin_manager.cargar_plugins()
        
        self.modelos = self._descubrir_modelos()
        self.historial = []

    def _descubrir_modelos(self) -> list:
        """Descubre dinámicamente los modelos Gemini Flash disponibles en la cuenta."""
        preferidos = [
            "gemini-3.5-flash-lite",
            "gemini-3.6-flash",
            "gemini-3.8-flash",
            "gemini-3.5-flash"
        ]
        disponibles = []
        try:
            for m in self.client.models.list():
                nombre = m.name.replace("models/", "")
                if "gemini" in nombre and "flash" in nombre and "tts" not in nombre and "image" not in nombre:
                    disponibles.append(nombre)
        except Exception:
            pass

        # Ordenar priorizando los preferidos que existan en la cuenta, y luego el resto
        ordenados = [m for m in preferidos if m in disponibles]
        for m in disponibles:
            if m not in ordenados:
                ordenados.append(m)

        return ordenados if ordenados else preferidos

    def _construir_config(self) -> types.GenerateContentConfig:
        ahora = datetime.datetime.now().strftime("%A %d/%m/%Y %H:%M")
        system_prompt = (
            f"Sos J.A.R.V.I.S., el asistente personal avanzado de Alejandro en Montevideo, Uruguay. "
            f"Fecha y hora actual del sistema: {ahora}. "
            "Hablás en español rioplatense natural (voseo), con tono profesional, ágil, conciso y leal. "
            "Tenés acceso a un ecosistema de plugins para consultar agenda, correos, clima, noticias, "
            "controlar el sistema y guardar/buscar recuerdos en tu base de datos permanente. "
            "Cuando respondas para ser leído por voz, evitá usar asteriscos de markdown o listas largas: "
            "sé directo, conversacional y resolutivo."
        )
        return types.GenerateContentConfig(
            system_instruction=system_prompt,
            tools=self.tools,
            temperature=0.4
        )

    def procesar_consulta(self, texto_usuario: str) -> str:
        StateBus.actualizar("THINKING", f"Analizando: '{texto_usuario[:35]}...'")
        config = self._construir_config()

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
                
                # Actualizamos el historial para mantener memoria de conversación entre modelos
                self.historial = chat.get_history()
                if len(self.historial) > 24:
                    self.historial = self.historial[-24:]

                StateBus.actualizar("IDLE", "Listo", ultima_respuesta=texto_final)
                return texto_final
            except Exception as e:
                print(f"   [!] Saltando {modelo}: {str(e)[:90]}...")
                continue

        error_msg = "Disculpá Alejandro, todos los servidores de IA están saturados en este momento."
        StateBus.actualizar("IDLE", "Error de conexión", ultima_respuesta=error_msg)
        return error_msg
