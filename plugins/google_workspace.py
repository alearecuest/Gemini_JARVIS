import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from core.plugin_manager import jarvis_tool

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.readonly"
]

def _obtener_credenciales():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

@jarvis_tool
def consultar_agenda_calendar(cantidad_eventos: int = 5) -> str:
    """Consulta los próximos eventos agendados en Google Calendar en tiempo real."""
    print(" > [Plugin Google]: Consultando Google Calendar...")
    try:
        creds = _obtener_credenciales()
        service = build("calendar", "v3", credentials=creds)
        ahora = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        events_result = service.events().list(
            calendarId="primary", timeMin=ahora,
            maxResults=cantidad_eventos, singleEvents=True,
            orderBy="startTime"
        ).execute()
        eventos = events_result.get("items", [])

        if not eventos:
            return "No hay eventos próximos agendados en el calendario."

        lista = []
        for ev in eventos:
            inicio = ev["start"].get("dateTime", ev["start"].get("date"))
            lista.append(f"- {ev.get('summary', 'Sin título')} ({inicio})")
        return "Próximos eventos en agenda:\n" + "\n".join(lista)
    except Exception as e:
        return f"Error al consultar Google Calendar: {e}"

@jarvis_tool
def agendar_evento_calendar(titulo: str, fecha_hora_iso: str, duracion_minutos: int = 60) -> str:
    """Crea un nuevo evento en Google Calendar. 'fecha_hora_iso' debe tener formato YYYY-MM-DDTHH:MM:SS (ejemplo: 2026-10-25T15:00:00)."""
    print(f" > [Plugin Google]: Agendando '{titulo}' para {fecha_hora_iso}...")
    try:
        creds = _obtener_credenciales()
        service = build("calendar", "v3", credentials=creds)
        
        dt_inicio = datetime.datetime.fromisoformat(fecha_hora_iso)
        dt_fin = dt_inicio + datetime.timedelta(minutes=duracion_minutos)
        
        evento = {
            "summary": titulo,
            "start": {"dateTime": dt_inicio.isoformat(), "timeZone": "America/Montevideo"},
            "end": {"dateTime": dt_fin.isoformat(), "timeZone": "America/Montevideo"},
        }
        creado = service.events().insert(calendarId="primary", body=evento).execute()
        return f"Evento '{titulo}' agendado con éxito para el {fecha_hora_iso}."
    except Exception as e:
        return f"Error al agendar el evento: {e}"

@jarvis_tool
def leer_correos_no_leidos(cantidad: int = 5) -> str:
    """Revisa la bandeja de entrada de Gmail y devuelve los remitentes y asuntos de los últimos correos importantes no leídos."""
    print(" > [Plugin Google]: Consultando bandeja de Gmail...")
    try:
        creds = _obtener_credenciales()
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(
            userId="me", q="is:unread category:primary", maxResults=cantidad
        ).execute()
        mensajes = results.get("messages", [])

        if not mensajes:
            return "No tenés correos nuevos sin leer en tu bandeja principal."

        resumen = []
        for msg in mensajes:
            detalle = service.users().messages().get(userId="me", id=msg["id"], format="metadata", metadataHeaders=["From", "Subject"]).execute()
            headers = {h["name"]: h["value"] for h in detalle.get("payload", {}).get("headers", [])}
            remitente = headers.get("From", "Desconocido")
            asunto = headers.get("Subject", "Sin asunto")
            resumen.append(f"- De: {remitente} | Asunto: {asunto}")
        return "Correos sin leer:\n" + "\n".join(resumen)
    except Exception as e:
        return f"Error al leer Gmail: {e}"