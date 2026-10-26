import os
import subprocess
from core.plugin_manager import jarvis_tool

@jarvis_tool
def consultar_estado_git(directorio: str = ".") -> str:
    """Devuelve la rama actual, los archivos modificados y el último commit de un repositorio Git local."""
    print(f" > [Plugin Dev]: Inspeccionando repositorio Git en '{directorio}'...")
    try:
        rama = subprocess.check_output(["git", "-C", directorio, "branch", "--show-current"], text=True).strip()
        estado = subprocess.check_output(["git", "-C", directorio, "status", "--short"], text=True).strip()
        ultimo = subprocess.check_output(["git", "-C", directorio, "log", "-1", "--oneline"], text=True).strip()
        cambios = estado if estado else "Árbol de trabajo limpio (sin cambios pendientes)."
        return f"Rama actual: {rama}\nÚltimo commit: {ultimo}\nEstado de archivos:\n{cambios}"
    except Exception as e:
        return f"No se pudo obtener información de Git: {e}"

@jarvis_tool
def explorar_directorio_local(ruta: str = ".") -> str:
    """Lista los archivos y subcarpetas dentro de un directorio local del proyecto o sistema."""
    print(f" > [Plugin Dev]: Listando archivos en '{ruta}'...")
    try:
        if not os.path.exists(ruta):
            return f"La ruta '{ruta}' no existe."
        elementos = sorted(os.listdir(ruta))[:30]
        return f"Contenido de '{ruta}': " + ", ".join(elementos)
    except Exception as e:
        return f"Error al explorar directorio: {e}"
