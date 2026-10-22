import os
import datetime
import subprocess
import urllib.parse
import xml.etree.ElementTree as ET
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES_GOOGLE = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.readonly'
]

def obtener_servicio_google(servicio_nombre):
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES_GOOGLE)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                return None
            print("\n\033[1;33m[ATENCIÓN: Se abrirá tu navegador para autorizar permisos de Google...]\033[0m")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES_GOOGLE)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build(servicio_nombre, 'v3' if servicio_nombre == 'calendar' else 'v1', credentials=creds)

# --- 1. GOOGLE CALENDAR (AGENDAR, CONSULTAR Y ELIMINAR) ---
def agendar_evento_google_calendar(titulo: str, fecha_hora_inicio_iso: str, duracion_minutos: int = 60, descripcion: str = "") -> str:
    """Crea y guarda un evento en el Google Calendar principal de Alejandro.
    fecha_hora_inicio_iso: formato 'YYYY-MM-DDTHH:MM:SS'.
    """
    print(f"\033[1;32m > [Google Calendar: Agendando '{titulo}' ({fecha_hora_inicio_iso}, {duracion_minutos} min)...]\033[0m")
    service = obtener_servicio_google('calendar')
    if not service:
        return "ERROR: No se encontró credentials.json."
    try:
        dt_inicio = datetime.datetime.fromisoformat(fecha_hora_inicio_iso)
        dt_fin = dt_inicio + datetime.timedelta(minutes=duracion_minutos)
        evento = {
            'summary': titulo,
            'description': descripcion,
            'start': {'dateTime': dt_inicio.strftime('%Y-%m-%dT%H:%M:%S'), 'timeZone': 'America/Montevideo'},
            'end': {'dateTime': dt_fin.strftime('%Y-%m-%dT%H:%M:%S'), 'timeZone': 'America/Montevideo'},
        }
        service.events().insert(calendarId='primary', body=evento).execute()
        return f"ÉXITO: Evento '{titulo}' agendado para el {dt_inicio.strftime('%d/%m/%Y de %H:%M')} a {dt_fin.strftime('%H:%M')}."
    except Exception as e:
        return f"ERROR al guardar en Google Calendar: {e}"

def consultar_eventos_google_calendar(cantidad_maxima: int = 10) -> str:
    """Consulta y devuelve los próximos eventos reales del Google Calendar de Alejandro."""
    print("\033[1;32m > [Consultando Google Calendar en tiempo real...]\033[0m")
    service = obtener_servicio_google('calendar')
    if not service:
        return "ERROR: No se encontró credentials.json."
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

def eliminar_evento_google_calendar(texto_busqueda: str) -> str:
    """Busca un evento próximo en el Google Calendar de Alejandro que coincida con 'texto_busqueda' y lo elimina/cancela."""
    print(f"\033[1;32m > [Google Calendar: Buscando evento '{texto_busqueda}' para eliminar...]\033[0m")
    service = obtener_servicio_google('calendar')
    if not service:
        return "ERROR: No se encontró credentials.json."
    try:
        ahora_iso = datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")
        events_result = service.events().list(
            calendarId='primary', timeMin=ahora_iso,
            maxResults=25, singleEvents=True, orderBy='startTime'
        ).execute()
        eventos = events_result.get('items', [])
        
        busqueda_low = texto_busqueda.lower()
        for ev in eventos:
            titulo = ev.get('summary', '')
            if busqueda_low in titulo.lower():
                service.events().delete(calendarId='primary', eventId=ev['id']).execute()
                inicio = ev['start'].get('dateTime', ev['start'].get('date'))
                return f"ÉXITO: Se eliminó del calendario el evento '{titulo}' programado para {inicio}."
        
        return f"No encontré ningún evento próximo que contenga '{texto_busqueda}' para borrar."
    except Exception as e:
        return f"ERROR al eliminar evento: {e}"

# --- 2. GMAIL ---
def buscar_correos_gmail(query: str = "is:unread", max_resultados: int = 3) -> str:
    """Busca correos electrónicos recientes o no leídos en el Gmail principal de Alejandro."""
    print(f"\033[1;32m > [Gmail: Buscando mensajes con filtro '{query}'...]\033[0m")
    service = obtener_servicio_google('gmail')
    if not service:
        return "ERROR: No se encontró credentials.json."
    try:
        results = service.users().messages().list(userId='me', q=query, maxResults=max_resultados).execute()
        messages = results.get('messages', [])
        if not messages:
            return "No se encontraron correos coincidentes en Gmail."
        detalles = []
        for msg in messages:
            txt = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            headers = txt['payload']['headers']
            asunto = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Sin asunto')
            remitente = next((h['value'] for h in headers if h['name'] == 'From'), 'Desconocido')
            snippet = txt.get('snippet', '')
            detalles.append(f"De: {remitente} | Asunto: {asunto} | Extracto: {snippet}")
        return "Mensajes en Gmail:\n" + "\n".join(detalles)
    except Exception as e:
        return f"ERROR al consultar Gmail: {e}"

# --- 3. BÚSQUEDA WEB Y NOTICIAS EN TIEMPO REAL ---
def buscar_en_internet(consulta: str, max_resultados: int = 4) -> str:
    """Busca información actualizada, noticias en tiempo real, cotizaciones o datos en internet."""
    print(f"\033[1;32m > [Web Search: Buscando en vivo '{consulta}'...]\033[0m")
    resultados = []
    
    # 1. Intentar con DuckDuckGo Search (si está instalado) para datos generales y web
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            for r in ddgs.text(consulta, region="uy-es", max_results=max_resultados):
                resultados.append(f"- {r.get('title')}: {r.get('body')}")
    except Exception:
        pass

    # 2. Respaldo / complemento en vivo con Google News RSS (ideal para noticias del día y actualidad)
    if not resultados:
        try:
            q_encoded = urllib.parse.quote(consulta)
            url = f"https://news.google.com/rss/search?q={q_encoded}&hl=es-419&gl=UY&ceid=UY:es-419"
            resp = requests.get(url, timeout=4)
            root = ET.fromstring(resp.content)
            for item in root.findall('.//item')[:max_resultados]:
                titulo = item.find('title').text if item.find('title') is not None else ''
                fecha = item.find('pubDate').text if item.find('pubDate') is not None else ''
                resultados.append(f"- {titulo} ({fecha})")
        except Exception as e:
            return f"Error al buscar en internet: {e}"

    if not resultados:
        return f"No se encontraron resultados en vivo para '{consulta}'."
    return "Resultados en tiempo real:\n" + "\n".join(resultados)

# --- 4. CONTROL DE SISTEMA WINDOWS ---
def controlar_sistema_windows(accion: str) -> str:
    """Controla funciones de la PC Windows de Alejandro: abrir_calculadora, abrir_notepad, abrir_chrome, silenciar_volumen, subir_volumen, bajar_volumen."""
    accion_low = accion.lower()
    print(f"\033[1;32m > [Sistema Windows: Ejecutando '{accion}'...]\033[0m")
    if "calculadora" in accion_low or "calc" in accion_low:
        subprocess.Popen("calc.exe")
        return "Calculadora abierta."
    elif "notepad" in accion_low or "notas" in accion_low:
        subprocess.Popen("start notepad++", shell=True)
        return "Notepad++ abierto."
    elif "chrome" in accion_low or "navegador" in accion_low:
        subprocess.Popen("start chrome", shell=True)
        return "Navegador Chrome abierto."
    elif "silenciar" in accion_low or "mute" in accion_low:
        subprocess.run(["powershell", "-c", "$w = New-Object -ComObject WScript.Shell; $w.SendKeys([char]173)"])
        return "Audio silenciado."
    elif "subir" in accion_low:
        for _ in range(5):
            subprocess.run(["powershell", "-c", "$w = New-Object -ComObject WScript.Shell; $w.SendKeys([char]175)"])
        return "Volumen subido."
    elif "bajar" in accion_low:
        for _ in range(5):
            subprocess.run(["powershell", "-c", "$w = New-Object -ComObject WScript.Shell; $w.SendKeys([char]174)"])
        return "Volumen bajado."
    return f"No tengo automatizada la acción: {accion}."

# Lista exportable con todas las herramientas para pasar directo a Gemini
LISTA_HERRAMIENTAS_JARVIS = [
    agendar_evento_google_calendar,
    consultar_eventos_google_calendar,
    eliminar_evento_google_calendar,
    buscar_correos_gmail,
    buscar_en_internet,
    controlar_sistema_windows
]