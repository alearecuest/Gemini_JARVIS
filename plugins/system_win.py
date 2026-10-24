import sys
import subprocess
import psutil
from core.plugin_manager import jarvis_tool

ES_WINDOWS = sys.platform.startswith("win")

@jarvis_tool
def obtener_telemetria_sistema() -> str:
    """Devuelve el porcentaje actual de uso de CPU, memoria RAM y estado de la batería de la PC."""
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    bateria = psutil.sensors_battery()
    bat_str = f"{bateria.percent}% ({'Cargando' if bateria.power_plugged else 'En batería'})" if bateria else "Conectado a CA"
    return f"CPU: {cpu}%, RAM: {ram}%, Batería: {bat_str}"

@jarvis_tool
def abrir_aplicacion_sistema(nombre_app: str) -> str:
    app = nombre_app.lower().strip()
    
    prefijo = "" if ES_WINDOWS else "cmd.exe /c "
    
    comandos = {
        "calculadora": f"{prefijo}calc.exe",
        "notepad++": f"{prefijo}start notepad++",
        "bloc de notas": f"{prefijo}notepad.exe",
        "chrome": f"{prefijo}start chrome",
        "vscode": "code",
        "explorador": f"{prefijo}explorer.exe ."
    }
    
    for clave, cmd in comandos.items():
        if clave in app:
            subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"Aplicación '{clave}' iniciada correctamente."
    return f"No encontré un comando configurado para abrir '{nombre_app}'."

@jarvis_tool
def controlar_volumen_sistema(accion: str, pasos: int = 5) -> str:
    """Controla el volumen de audio del sistema. 'accion' puede ser 'subir', 'bajar' o 'silenciar'."""
    accion = accion.lower().strip()
    pasos = max(1, min(pasos, 25))
    
    if ES_WINDOWS:
        import ctypes
        vk = 0xAD if ("silenciar" in accion or "mute" in accion) else (0xAF if "subir" in accion else 0xAE)
        repeticiones = 1 if vk == 0xAD else pasos
        for _ in range(repeticiones):
            ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
            ctypes.windll.user32.keybd_event(vk, 0, 2, 0)
    else:
        char_code = 173 if ("silenciar" in accion or "mute" in accion) else (175 if "subir" in accion else 174)
        rep = 1 if char_code == 173 else pasos
        ps_cmd = f"$w = New-Object -ComObject WScript.Shell; 1..{rep} | ForEach-Object {{ $w.SendKeys([char]{char_code}) }}"
        subprocess.run(["powershell.exe", "-NoProfile", "-Command", ps_cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return f"Volumen ajustado ({accion})."