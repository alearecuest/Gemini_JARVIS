import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import asyncio
import datetime
import tempfile
import subprocess
import concurrent.futures
import speech_recognition as sr
import edge_tts
import pygame
import psutil
import ephem
import requests
from google import genai
from google.genai import types

# Librerías de Google Calendar
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

pygame.mixer.init()

VOZ_JARVIS = "es-UY-MateoNeural"
SCOPES_CALENDAR = ['https://www.googleapis.com/auth/calendar']

# Modelos reales verificados en tu cuenta (en orden de prioridad para evitar el 503 de 3.8)
MODELOS_ACTIVOS = [
    'gemini-3.7-flash',
    'gemini-3.6-flash',
    'gemini-3.5-flash',
    'gemini-3.8-flash',
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

# --- CONEXIÓN CON GOOGLE CALENDAR REAL ---
def obtener_servicio_calendar():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES_CALENDAR)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                return None
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES_CALENDAR)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

# --- HERRAMIENTAS (TOOLS) QUE GEMINI PUEDE EJECUTAR SOLO ---
def agendar_evento_google_calendar(titulo: str, fecha_hora_inicio_iso: str, duracion_minutos: int = 60, descripcion: str = "") -> str:
    """Crea y guarda un evento ordenado en el Google Calendar principal de Alejandro.
    fecha_hora_inicio_iso debe estar en formato 'YYYY-MM-DDTHH:MM:SS' (ej: '2026-10-22T15:00:00').
    """
    print(f"\033[1;32m > [Ejecutando Google Calendar: Agendando '{titulo}' para {fecha_hora_inicio_iso}...]\033[0m")
    service = obtener_servicio_calendar()
    if not service:
        return "ERROR: No se encontró el archivo credentials.json en la carpeta JARVIS_App para conectar con Google Calendar."
    
    try:
        dt_inicio = datetime.datetime.fromisoformat(fecha_hora_inicio_iso)
        dt_fin = dt_inicio + datetime.timedelta(minutes=duracion_minutos)
        
        evento = {
            'summary': titulo,
            'description': descripcion,
            'start': {'dateTime': dt_inicio.strftime('%Y-%m-%dT%H:%M:%S'), 'timeZone': 'America/Montevideo'},
            'end': {'dateTime': dt_fin.strftime('%Y-%m-%dT%H:%M:%S'), 'timeZone': 'America/Montevideo'},
        }
        creado = service.events().insert(calendarId='primary', body=evento).execute()
        return f"ÉXITO: Evento '{titulo}' guardado en el Google Calendar de Alejandro para el {dt_inicio.strftime('%d/%m/%Y a las %H:%M')}."
    except Exception as e:
        return f"ERROR al guardar en Google Calendar: {e}"

def consultar_eventos_google_calendar(cantidad_maxima: int = 5) -> str:
    """Consulta y devuelve los próximos eventos reales del Google Calendar de Alejandro."""
    print("\033[1;32m > [Consultando Google Calendar en tiempo real...]\033[0m")
    service = obtener_servicio_calendar()
    if not service:
        return "ERROR: Aún no está configurado el archivo credentials.json en la carpeta JARVIS_App."
    
    try:
        ahora_iso = datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")
        events_result = service.events().list(
            calendarId='primary', timeMin=ahora_iso,
            maxResults=cantidad_maxima, singleEvents=True,
            orderBy='startTime'
        ).execute()
        eventos = events_result.get('items', [])
        if not eventos:
            return "El Google Calendar de Alejandro no tiene eventos próximos registrados."
        
        lista = []
        for ev in eventos:
            inicio = ev['start'].get('dateTime', ev['start'].get('date'))
            lista.append(f"- {ev.get('summary', 'Sin título')} ({inicio})")
        return "Próximos eventos en Google Calendar:\n" + "\n".join(lista)
    except Exception as e:
        return f"ERROR al leer Google Calendar: {e}"

def abrir_programa_windows(nombre_programa: str) -> str:
    """Abre aplicaciones locales en la computadora Windows de Alejandro (calculadora, notepad++, navegador, consola)."""
    prog = nombre_programa.lower()
    if "calc" in prog:
        subprocess.Popen("calc.exe")
        return "Calculadora abierta."
    elif "notepad" in prog or "notas" in prog:
        subprocess.Popen("start notepad++", shell=True)
        return "Notepad++ abierto."
    elif "chrome" in prog or "navegador" in prog:
        subprocess.Popen("start chrome", shell=True)
        return "Navegador Chrome abierto."
    return f"No tengo configurado el ejecutable para {nombre_programa}."

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
    dia_nombre = dias_sem[ahora_dt.weekday()]
    fecha_completa = ahora_dt.strftime(f"{dia_nombre} %Y-%m-%d %H:%M")

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

    tiene_credenciales = "Conectado a Google Calendar" if os.path.exists("credentials.json") else "Falta archivo credentials.json para Google Calendar"

    return f"Fecha y Hora actual en Montevideo: {fecha_completa} | Clima: {clima} | Amanecer: {amanecer} | Atardecer: {atardecer} | Fase Lunar: {fase_nombre} ({iluminacion}%) | CPU: {cpu}% | RAM: {ram}% | Estado Agenda: {tiene_credenciales}"

# --- CEREBRO IA CON MEMORIA DE CONVERSACIÓN Y HERRAMIENTAS ---
historial_conversacion = []

def _llamar_gemini_con_tools(modelo, prompt_sistema, mensaje_usuario):
    client = genai.Client()
    config = types.GenerateContentConfig(
        system_instruction=prompt_sistema,
        tools=[agendar_evento_google_calendar, consultar_eventos_google_calendar, abrir_programa_windows],
        temperature=0.3
    )
    response = client.models.generate_content(
        model=modelo,
        contents=mensaje_usuario,
        config=config
    )
    return response.text.replace("*", "").strip()

def consultar_gemini(comando):
    global historial_conversacion
    contexto = obtener_contexto()
    
    # Guardamos los últimos 4 intercambios para que tenga hilo de conversación coherente
    historial_texto = "\n".join(historial_conversacion[-6:])
    
    prompt_sistema = f"""
    Eres J.A.R.V.I.S., el asistente personal inteligente de Alejandro en Montevideo, Uruguay.
    Contexto en tiempo real: {contexto}.
    Historial reciente de la charla:
    {historial_texto}
    
    REGLAS DE COHERENCIA:
    1. Si Alejandro te dicta una idea desordenada para agendar, ORDENA y redacta un título prolijo, deduce la fecha y hora exacta basándote en la Fecha Actual ({contexto.split('|')[0]}), y ejecuta la herramienta `agendar_evento_google_calendar`.
    2. Si falta la hora o el día para agendar, pregúntaselo brevemente antes de agendar.
    3. Tu agenda oficial es el Google Calendar principal de Alejandro. Si pregunta dónde guardas la agenda o qué tiene agendado, usa `consultar_eventos_google_calendar` o explicale con precisión el estado de conexión.
    4. NO recites el clima, ni la luna, ni la CPU a menos que Alejandro te lo pregunte específicamente.
    5. Habla en español rioplatense natural, conciso (1 a 3 oraciones), sin usar asteriscos ni formato markdown.
    """

    for modelo in MODELOS_ACTIVOS:
        try:
            print(f"\033[90m > [Procesando con {modelo}...]\033[0m")
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                futuro = executor.submit(_llamar_gemini_con_tools, modelo, prompt_sistema, comando)
                respuesta = futuro.result(timeout=15)
                
            historial_conversacion.append(f"Alejandro: {comando}")
            historial_conversacion.append(f"JARVIS: {respuesta}")
            return respuesta
        except Exception as e:
            print(f"\033[33m > [Saltando {modelo}: {str(e)[:80]}...]\033[0m")
            continue

    return "Alejandro, en este momento todos los nodos neuronales presentan inconvenientes de red."

# --- BUCLE PRINCIPAL ---
def iniciar_jarvis():
    r = sr.Recognizer()
    r.dynamic_energy_threshold = False
    r.pause_threshold = 1.0 # 1 segundo de pausa para permitirte pensar mientras hablas desordenado
    mic = sr.Microphone(device_index=1)

    en_suspension = False

    with mic as source:
        print("\n[Calibrando micrófono (1 seg)...]")
        r.adjust_for_ambient_noise(source, duration=1)
        hablar("Sistemas en línea, Alejandro. Estoy a tu disposición.")

        while True:
            try:
                if not en_suspension:
                    print("\033[90m[Activo - Di 'Jarvis, <tu pedido>'...]\033[0m")
                else:
                    print("\033[34m[MODO SUSPENSIÓN - Di 'Jarvis, despierta' para reactivar]\033[0m")

                audio = r.listen(source, timeout=None, phrase_time_limit=12)
                frase = r.recognize_google(audio, language="es-UY").strip()
                frase_low = frase.lower()
                print(f" > Escuché: '{frase}'")

                if "jarvis" not in frase_low:
                    continue

                if en_suspension:
                    if any(w in frase_low for w in ["despierta", "activar", "actívate", "iniciar", "arriba", "vuelve", "volver"]):
                        en_suspension = False
                        hablar("Sistemas reactivados, Alejandro. Te escucho.")
                    continue

                partes = frase_low.split("jarvis", 1)
                comando = partes[1].strip(" ,.") if len(partes) > 1 else ""

                if len(comando) < 3:
                    hablar("¿Sí, Alejandro?")
                    print("\033[1;33m[Escuchando tu pedido (puedes hablar tranquilo)...]\033[0m")
                    audio_cmd = r.listen(source, timeout=5, phrase_time_limit=15)
                    comando = r.recognize_google(audio_cmd, language="es-UY").strip()
                    print(f" > Pedido: '{comando}'")

                if any(w in comando.lower() for w in ["descansa", "suspensión", "suspension", "terminar sesión", "termina sesión", "modo espera", "duerme"]):
                    en_suspension = True
                    hablar("Entendido, Alejandro. Quedo en modo de espera.")
                    continue

                if any(w in comando.lower() for w in ["apagado total", "cerrar aplicación", "salir del sistema"]):
                    hablar("Cerrando todos los sistemas. Hasta luego, Alejandro.")
                    break

                respuesta = consultar_gemini(comando)
                hablar(respuesta)

            except sr.WaitTimeoutError:
                pass
            except sr.UnknownValueError:
                pass
            except Exception as e:
                print(f"[Alerta]: {e}")

if __name__ == "__main__":
    iniciar_jarvis()