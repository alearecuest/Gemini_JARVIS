from core.plugin_manager import jarvis_tool
from memory.local_memory import guardar_recuerdo_db, buscar_recuerdos_db

@jarvis_tool
def guardar_en_memoria(dato_a_recordar: str, categoria: str = "nota") -> str:
    """Guarda un dato importante, preferencia, nota técnica o recordatorio en la base de datos de memoria permanente de JARVIS."""
    print(f" > [Memoria]: Guardando recuerdo en categoría '{categoria}'...")
    return guardar_recuerdo_db(dato_a_recordar, categoria)

@jarvis_tool
def consultar_memoria(palabra_clave: str = "") -> str:
    """Busca notas, datos técnicos o preferencias guardadas previamente en la memoria permanente de JARVIS."""
    print(f" > [Memoria]: Consultando recuerdos ('{palabra_clave}')...")
    return buscar_recuerdos_db(palabra_clave)
