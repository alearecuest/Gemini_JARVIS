import os
import time
import asyncio
import tempfile

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame
import edge_tts

try:
    import speech_recognition as sr
except ImportError:
    sr = None

from core.state_bus import StateBus

class VoiceEngine:
    def __init__(self, voz="es-UY-MateoNeural", wake_word="jarvis"):
        self.voz = voz
        self.wake_word = wake_word.lower()
        self.audio_disponible = False
        self.mic_disponible = False

        # Inicializar salida de audio de forma segura (soporta WSL sin placa de audio)
        try:
            # Silenciar advertencias ALSA de C en entornos WSL sin placa de sonido
            devnull = os.open(os.devnull, os.O_WRONLY)
            old_stderr = os.dup(2)
            os.dup2(devnull, 2)
            try:
                pygame.mixer.init()
                self.audio_disponible = True
            finally:
                os.dup2(old_stderr, 2)
                os.close(devnull)
                os.close(old_stderr)
        except Exception as e:
            print(f" > [VoiceEngine]: Audio nativo no detectado en este entorno ({e}). Usando salida visual/texto.")

        # Inicializar reconocedor de micrófono si está instalado
        if sr is not None:
            try:
                self.recognizer = sr.Recognizer()
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.pause_threshold = 0.8
                self.mic_disponible = True
            except Exception:
                self.mic_disponible = False

    async def _generar_audio(self, texto: str, archivo_salida: str):
        comunicador = edge_tts.Communicate(texto, self.voz, rate="+8%")
        await comunicador.save(archivo_salida)

    def hablar(self, texto: str):
        """Sintetiza voz neuronal y actualiza el StateBus a SPEAKING mientras reproduce."""
        if not texto:
            return
        print(f"\n\033[1;36m[J.A.R.V.I.S.]: {texto}\033[0m\n")
        StateBus.actualizar("SPEAKING", "Hablando...", ultima_respuesta=texto)

        if not self.audio_disponible:
            # Simula el tiempo de habla en el HUD aunque no haya parlantes en WSL
            time.sleep(min(4.0, max(1.5, len(texto) * 0.04)))
            StateBus.actualizar("IDLE", "En guardia")
            return

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                ruta_mp3 = tmp.name

            asyncio.run(self._generar_audio(texto, ruta_mp3))

            pygame.mixer.music.load(ruta_mp3)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(15)
            pygame.mixer.music.unload()
            os.remove(ruta_mp3)
        except Exception as e:
            print(f"   [!] Error reproduciendo TTS: {e}")
        finally:
            StateBus.actualizar("IDLE", "En guardia")

    def iniciar_bucle_voz(self, agent):
        """Intenta usar micrófono; si no hay (ej. WSL sin passthrough), pasa a modo consola."""
        if not self.mic_disponible:
            self.iniciar_bucle_texto(agent)
            return

        try:
            mic = sr.Microphone()
            with mic as source:
                print("\n[Calibrando micrófono (1 seg)...]")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
        except Exception as e:
            print(f"\033[1;33m > [Aviso]: Micrófono físico no accesible desde esta terminal ({e}).\033[0m")
            print("\033[1;33m > Activando Modo Consola Interactivo (el HUD 3D seguirá sincronizado en vivo).\033[0m")
            self.iniciar_bucle_texto(agent)
            return

        self.hablar("Sistemas versión dos en línea, Alejandro. Todos los plugins operativos.")
        charla_activa_hasta = 0

        while True:
            en_ventana_activa = time.time() < charla_activa_hasta
            if en_ventana_activa:
                print("\033[1;32m[Charla activa (20s) - Hablá directo...]\033[0m")
                StateBus.actualizar("LISTENING", "Escuchando conversación activa...")
            else:
                print("\033[0;37m[En guardia - Decí 'Jarvis, <tu pedido>'...]\033[0m")
                StateBus.actualizar("IDLE", "En espera ('Jarvis...')")

            try:
                with mic as source:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=12)

                texto = self.recognizer.recognize_google(audio, language="es-UY").strip()
                if not texto:
                    continue
                print(f" > Escuché: '{texto}'")
                texto_lower = texto.lower()

                if any(frase in texto_lower for frase in ["quedate en espera", "quédate en espera", "descansa jarvis", "silencio jarvis"]):
                    charla_activa_hasta = 0
                    self.hablar("Entendido, Alejandro. Quedo en guardia.")
                    continue

                if en_ventana_activa or self.wake_word in texto_lower:
                    StateBus.actualizar("LISTENING", f"Escuché: {texto[:30]}...")
                    pedido = texto
                    if not en_ventana_activa:
                        idx = texto_lower.find(self.wake_word)
                        pedido = texto[idx + len(self.wake_word):].strip(" ,.:;¿?¡!")
                        if not pedido:
                            self.hablar("Sí, Alejandro, te escucho.")
                            charla_activa_hasta = time.time() + 20
                            continue

                    respuesta = agent.procesar_consulta(pedido)
                    self.hablar(respuesta)
                    charla_activa_hasta = time.time() + 20

            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"   [!] Error en bucle de voz: {e}")
                time.sleep(1)

    def iniciar_bucle_texto(self, agent):
        """Modo interactivo por teclado con sincronización completa del HUD 3D."""
        self.hablar("Sistemas versión dos en línea, Alejandro. Modo interactivo listo.")
        while True:
            try:
                StateBus.actualizar("IDLE", "Esperando comando...")
                consulta = input("\n\033[1;32mAlejandro > \033[0m").strip()
                if not consulta:
                    continue
                if consulta.lower() in ["salir", "exit", "chau"]:
                    break
                respuesta = agent.procesar_consulta(consulta)
                self.hablar(respuesta)
            except KeyboardInterrupt:
                break
