import os
import sys
import time
import asyncio
import tempfile
import subprocess

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
        self.audio_nativo = False
        self.es_wsl = os.path.exists("/mnt/c/Windows")
        self.mic_disponible = False

        try:
            devnull = os.open(os.devnull, os.O_WRONLY)
            old_stderr = os.dup(2)
            os.dup2(devnull, 2)
            try:
                pygame.mixer.init()
                self.audio_nativo = True
            finally:
                os.dup2(old_stderr, 2)
                os.close(devnull)
                os.close(old_stderr)
        except Exception:
            self.audio_nativo = False
            if self.es_wsl:
                print(" > [VoiceEngine]: Entorno WSL detectado. Puente SoundPlayer (WAV Síncrono) activo.")

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

    def _reproducir_en_wsl(self, texto: str):
        """Genera el MP3, lo pasa a WAV PCM y lo reproduce con SoundPlayer.PlaySync() en Windows."""
        ruta_mp3_wsl = "/mnt/c/Users/Public/jarvis_tts.mp3"
        ruta_wav_wsl = "/mnt/c/Users/Public/jarvis_tts.wav"
        ruta_wav_win = r"C:\Users\Public\jarvis_tts.wav"

        # 1. Generar MP3 desde Edge-TTS
        asyncio.run(self._generar_audio(texto, ruta_mp3_wsl))

        # 2. Convertir a WAV estándar con ffmpeg
        subprocess.run(
            ["ffmpeg", "-y", "-i", ruta_mp3_wsl, "-acodec", "pcm_s16le", "-ar", "24000", ruta_wav_wsl],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )

        # 3. Reproducir de forma síncrona nativa en Windows (1 sola línea infalible)
        ps_cmd = f"(New-Object Media.SoundPlayer '{ruta_wav_win}').PlaySync()"
        res = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", ps_cmd],
            capture_output=True,
            text=True
        )
        if res.returncode != 0 and res.stderr:
            print(f"   [!] Aviso PowerShell Audio: {res.stderr.strip()}")

        for f in (ruta_mp3_wsl, ruta_wav_wsl):
            if os.path.exists(f):
                try:
                    os.remove(f)
                except Exception:
                    pass

    def hablar(self, texto: str):
        if not texto:
            return
        print(f"\n\033[1;36m[J.A.R.V.I.S.]: {texto}\033[0m\n")
        StateBus.actualizar("SPEAKING", "Hablando...", ultima_respuesta=texto)

        try:
            if self.audio_nativo:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                    ruta_mp3 = tmp.name
                asyncio.run(self._generar_audio(texto, ruta_mp3))
                pygame.mixer.music.load(ruta_mp3)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(15)
                pygame.mixer.music.unload()
                os.remove(ruta_mp3)
            elif self.es_wsl:
                self._reproducir_en_wsl(texto)
            else:
                time.sleep(min(4.0, max(1.5, len(texto) * 0.04)))
        except Exception as e:
            print(f"   [!] Error reproduciendo TTS: {e}")
        finally:
            StateBus.actualizar("IDLE", "En guardia")

    def iniciar_bucle_voz(self, agent):
        if not self.mic_disponible:
            self.iniciar_bucle_texto(agent)
            return

        try:
            mic = sr.Microphone()
            with mic as source:
                print("\n[Calibrando micrófono (1 seg)...]")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
        except Exception:
            print("\033[1;33m > [Aviso]: Micrófono directo en WSL no detectado. Usando teclado con VOZ ACTIVA.\033[0m")
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
        self.hablar("Sistemas versión dos en línea, Alejandro. Audio puente activado.")
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
