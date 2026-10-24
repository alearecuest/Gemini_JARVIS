import requests
import xml.etree.ElementTree as ET
from ddgs import DDGS
from core.plugin_manager import jarvis_tool

@jarvis_tool
def buscar_en_internet(consulta: str) -> str:
    """Realiza una búsqueda web en tiempo real en internet sobre cualquier tema actual, datos técnicos o eventos recientes."""
    print(f" > [Plugin Web]: Buscando '{consulta}'...")
    try:
        resultados = DDGS().text(consulta, region="uy-es", max_results=4)
        if not resultados:
            return "No se encontraron resultados en la web para esa consulta."
        resumen = [f"- {r.get('title')}: {r.get('body')}" for r in resultados]
        return "\n".join(resumen)
    except Exception as e:
        return f"Error al buscar en internet: {e}"

@jarvis_tool
def obtener_noticias_actuales(tema: str = "Uruguay") -> str:
    """Obtiene los últimos titulares de noticias en tiempo real desde Google News sobre un tema o país específico."""
    print(f" > [Plugin Noticias]: Consultando titulares sobre '{tema}'...")
    try:
        url = f"https://news.google.com/rss/search?q={requests.utils.quote(tema)}&hl=es-419&gl=UY&ceid=UY:es-419"
        resp = requests.get(url, timeout=5)
        root = ET.fromstring(resp.content)
        items = root.findall(".//item")[:5]
        if not items:
            return f"No se encontraron noticias recientes sobre {tema}."
        titulares = [f"- {item.find('title').text}" for item in items]
        return f"Últimas noticias sobre {tema}:\n" + "\n".join(titulares)
    except Exception as e:
        return f"Error al obtener noticias: {e}"

@jarvis_tool
def consultar_clima(ciudad: str = "Montevideo") -> str:
    """Consulta el estado del tiempo y temperatura actual en cualquier ciudad."""
    try:
        url = f"https://wttr.in/{requests.utils.quote(ciudad)}?format=%C,+temperatura+%t,+humedad+%h,+viento+%w&lang=es"
        resp = requests.get(url, timeout=4)
        if resp.status_code == 200:
            return f"Clima en {ciudad}: {resp.text.strip()}"
        return f"No se pudo obtener el clima de {ciudad}."
    except Exception as e:
        return f"Error al conectar con el servicio meteorológico: {e}"