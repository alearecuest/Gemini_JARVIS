from core.plugin_manager import jarvis_tool
from memory.local_memory import guardar_recuerdo_db, buscar_recuerdos_db
from memory.rag_engine import RAGEngine

_rag = None

def _get_rag():
    global _rag
    if _rag is None:
        _rag = RAGEngine()
    return _rag

@jarvis_tool
def guardar_en_memoria(dato_a_recordar: str, categoria: str = "nota") -> str:
    """Guarda un dato importante, preferencia, nota técnica o recordatorio en la memoria permanente y vectorial (RAG) de JARVIS."""
    print(f" > [Memoria Vectorial]: Guardando e indexando en '{categoria}'...")
    res_sql = guardar_recuerdo_db(dato_a_recordar, categoria)
    res_rag = _get_rag().indexar_texto(dato_a_recordar, origen=f"memoria:{categoria}")
    return f"{res_sql} ({res_rag})"

@jarvis_tool
def consultar_memoria(consulta: str = "") -> str:
    """Busca notas, documentos indexados o preferencias en la memoria de JARVIS usando búsqueda semántica por significado (RAG) y base de datos."""
    print(f" > [Memoria Vectorial]: Buscando semánticamente '{consulta}'...")
    res_rag = _get_rag().buscar_semantico(consulta)
    res_sql = buscar_recuerdos_db(consulta)
    return f"{res_rag}\n\n{res_sql}"

@jarvis_tool
def indexar_documento_local(ruta_archivo: str) -> str:
    """Lee e indexa un archivo de texto, documentación (.md, .txt) o código (.py) en la base de conocimiento vectorial (RAG) de JARVIS."""
    print(f" > [RAG Engine]: Indexando documento '{ruta_archivo}'...")
    return _get_rag().indexar_archivo(ruta_archivo)
