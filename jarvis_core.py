import os
import warnings
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
warnings.filterwarnings("ignore")

import time
import asyncio
import datetime
import tempfile
import concurrent.futures
import speech_recognition as sr
import edge_tts
import pygame
import psutil
import ephem
import requests
from google import genai
from google.genai import types

# Importamos todas las herramientas desde el módulo auxiliar
from jarvis_tools import LISTA_HERRAMIENTAS_JARVIS

pygame.mixer.init()
VOZ_JARVIS = "es-UY-MateoNeural"

MODELOS_ACTIVOS = [
    'gemini-3.5-flash-lite',
    'gemini-3.8-flash',
    'gemini-3.6-flash',
    'gemini-3.5-flash',
    'gemini-3.1-pro-preview'
]

# --- MOTOR DE VOZ NEURONAL ---
async def _generar_audio(texto, archivo_salida):
    comunicador = edge_tts.Communicate(texto, VOZ_JARVIS, rate="+5%", pitch="-3Hz")
    await comunicador.save(archivo_salida)

def hablar(texto):
    print(f"\n\033[1;36m[J.A.R.V.I.S.]: {texto}\033[0m\n")
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            temp_path = fp.name
        asyncio.run(_generar_audio(texto, temp_path))
        pygame.mixer.music.load(temp_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
        os.remove(temp_path)
    except Exception as e:
        print(f"[Error en motor de voz]: {e}")

# --- TELEMETRÍA Y ASTRONOMÍA ---
def calcular_nombre_fase_lunar(fecha_utc):
    luna = ephem.Moon(fecha_utc)
    iluminacion = round(luna.phase, 1)
    edad_dias = fecha_utc - ephem.previous_new_moon(fecha_utc)
    if iluminacion < 3: nombre = "Luna Nueva"
    elif iluminacion > 97: nombre = "Luna Llena"
    elif edad_dias < 7.4: nombre = "Luna Creciente"
    elif edad_dias < 11.0: nombre = "Cuarto Creciente"
    elif edad_dias < 14.8: nombre = "Luna Gibosa Creciente"
    elif edad_dias < 22.1: nombre = "Luna Gibosa Menguante"
    elif edad_dias < 25.8: nombre = "Cuarto Menguante"
    else: nombre = "Luna Menguante"
    return nombre, iluminacion

def obtener_contexto():
    cpu = psutil.cpu_percent(interval=0.2)
    ram = psutil.virtual_memory().percent
    ahora_dt = datetime.datetime.now()
    dias_sem = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    fecha_completa = ahora_dt.strftime(f"{dias_sem[ahora_dt.weekday()]} %Y-%m-%d %H:%M")

    obs = ephem.Observer()
    obs.lat, obs.lon = '-34.9011', '-56.1645'
    ahora_utc = ephem.Date(datetime.datetime.now(datetime.UTC))
    obs.date = ahora_utc

    sol = ephem.Sun()
    fase_nombre, iluminacion = calcular_nombre_fase_lunar(ahora_utc)

    try:
        amanecer = ephem.localtime(obs.next_rising(sol)).strftime("%H:%M")
        atardecer = ephem.localtime(obs.next_setting(sol)).strftime("%H:%M")
    except Exception:
        amanecer, atardecer = "no disponible", "no disponible"

    try:
        clima = requests.get("https://wttr.in/Montevideo?format=%C,+%t&lang=es", timeout=2).text.strip()
    except Exception:
        clima = "sin datos meteorológicos"

    return f"Fecha y Hora en Montevideo: {fecha_completa} | Clima: {clima} | Amanecer: {amanecer} | Atardecer: {atardecer} | Fase Lunar: {fase_nombre} ({iluminacion}%) | CPU: {cpu}% | RAM: {ram}%"

# --- CEREBRO IA ---
historial_conversacion = []

def _llamar_gemini_con_tools(modelo, prompt_sistema, mensaje_usuario):
    client = genai.Client()
    config = types.GenerateContentConfig(
        system_instruction=prompt_sistema,
        tools=LISTA_HERRAMIENTAS_JARVIS,
        temperature=0.3
    )
    chat = client.chats.create(model=modelo, config=config)
    response = chat.send_message(mensaje_usuario)
    return response.text.replace("*", "").strip()

def consultar_gemini(comando):
    global historial_conversacion
    contexto = obtener_contexto()
    historial_texto = "\n".join(historial_conversacion[-8:])
    
    prompt_sistema = f"""
    Eres J.A.R.V.I.S., el asistente personal inteligente de Alejandro en Montevideo, Uruguay.
    Contexto en tiempo real: {contexto}.
    Historial reciente:
    {historial_texto}
    
    INSTRUCCIONES DE HERRAMIENTAS:
    1. Usa las herramientas de Google Calendar para agendar, consultar o eliminar/cancelar eventos.
    2. Usa `buscar_correos_gmail` para revisar correos.
    3. Usa `buscar_en_internet` cuando Alejandro pregunte por noticias actuales, cotizaciones o datos de la web.
    4. Usa `controlar_sistema_windows` para abrir programas o controlar el volumen de la PC.
    5. Habla en español rioplatense/uruguayo natural, conciso (1 a 2 oraciones), sin asteriscos.
    """

    for modelo in MODELOS_ACTIVOS:
        try:
            print(f"\033[90m > [Procesando con {modelo}...]\033[0m")
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                futuro = executor.submit(_llamar_gemini_con_tools, modelo, prompt_sistema, comando)
                respuesta = futuro.result(timeout=20)
                
            historial_conversacion.append(f"Alejandro: {comando}")
            historial_conversacion.append(f"JARVIS: {respuesta}")
            return respuesta
        except Exception as e:
            print(f"\033[33m > [Saltando {modelo}: {str(e)[:80]}...]\033[0m")
            time.sleep(1.5)
            continue

    return "Alejandro, en este momento los servidores presentan demora."

# --- BUCLE PRINCIPAL ---
def iniciar_jarvis():
    r = sr.Recognizer()
    r.dynamic_energy_threshold = False
    r.pause_threshold = 1.0
    mic = sr.Microphone(device_index=1)

    en_suspension = False
    ultimo_dialogo = 0
    VENTANA_CHARLA_SEGUNDOS = 20
    ultimo_estado_impreso = ""

    with mic as source:
        print("\n[Calibrando micrófono (1 seg)...]")
        r.adjust_for_ambient_noise(source, duration=1)
        hablar("Sistemas en línea, Alejandro. Todos los módulos de backend operativos.")

        while True:
            try:
                en_charla_activa = (time.time() - ultimo_dialogo) < VENTANA_CHARLA_SEGUNDOS

                estado_actual = "SUSPENSION" if en_suspension else ("ACTIVA" if en_charla_activa else "GUARDIA")
                if estado_actual != ultimo_estado_impreso:
                    if estado_actual == "SUSPENSION":
                        print("\033[34m[MODO SUSPENSIÓN - Di 'Jarvis, despierta' para reactivar]\033[0m")
                    elif estado_actual == "ACTIVA":
                        print("\033[1;32m[Charla activa (20s) - Puedes responder directo...]\033[0m")
                    else:
                        print("\033[90m[En guardia - Di 'Jarvis, <tu pedido>'...]\033[0m")
                    ultimo_estado_impreso = estado_actual

                audio = r.listen(source, timeout=2, phrase_time_limit=12)
                frase = r.recognize_google(audio, language="es-UY").strip()
                frase_low = frase.lower()
                print(f" > Escuché: '{frase}'")
                ultimo_estado_impreso = ""

                if en_suspension:
                    if "jarvis" in frase_low and any(w in frase_low for w in ["despierta", "activar", "actívate", "iniciar", "arriba", "vuelve", "volver"]):
                        en_suspension = False
                        ultimo_dialogo = time.time()
                        hablar("Sistemas reactivados, Alejandro. Te escucho.")
                    continue

                if not en_charla_activa and "jarvis" not in frase_low:
                    continue

                comando = frase_low.replace("jarvis", "").replace("service", "").strip(" ,.¿?¡!")

                if comando in ["", "hola", "che", "ey", "buen día", "buenos días", "buenas"]:
                    hablar("¿Sí, Alejandro?")
                    ultimo_dialogo = time.time()
                    continue

                if comando in ["gracias", "muchas gracias", "genial gracias", "buenísimo gracias", "impecable gracias", "listo gracias"]:
                    ultimo_dialogo = 0
                    hablar("Por nada, Alejandro. Quedo atento por si necesitás algo más.")
                    continue

                frases_suspension = [
                    "descansa", "suspensión", "suspension", "terminar sesión", "termina sesión",
                    "modo espera", "modo de espera", "duerme", "eso es todo", "nada más por ahora",
                    "no voy a usar más", "no te voy a usar", "hasta luego"
                ]
                if any(w in comando for w in frases_suspension):
                    en_suspension = True
                    ultimo_dialogo = 0
                    hablar("Entendido, Alejandro. Quedo en modo de espera.")
                    continue

                if any(w in comando for w in ["apagado total", "cerrar aplicación", "salir del sistema"]):
                    hablar("Cerrando todos los sistemas. Que tengas una excelente jornada, Alejandro.")
                    break

                respuesta = consultar_gemini(comando)
                hablar(respuesta)
                ultimo_dialogo = time.time()

            except sr.WaitTimeoutError:
                pass
            except sr.UnknownValueError:
                pass
            except Exception as e:
                print(f"[Alerta]: {e}")

if __name__ == "__main__":
    iniciar_jarvis()