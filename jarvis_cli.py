import os
import sys
import shutil
import argparse
from core.plugin_manager import PluginManager
from memory.local_memory import inicializar_db, DB_PATH
from core.telemetry import TelemetryLogger

def cmd_doctor():
    """Diagnóstico completo del ecosistema al estilo 'open-jarvis doctor'."""
    print("\n\033[1;36m====================================================\033[0m")
    print("\033[1;36m   J.A.R.V.I.S. DOCTOR - Diagnóstico de Sistema\033[0m")
    print("\033[1;36m====================================================\033[0m\n")

    checks = []
    api_key = os.environ.get("GEMINI_API_KEY")
    checks.append(("GEMINI_API_KEY", bool(api_key), "Configurada correctamente" if api_key else "Falta variable de entorno GEMINI_API_KEY"))

    ffmpeg_ok = shutil.which("ffmpeg") is not None
    checks.append(("FFmpeg Audio Codec", ffmpeg_ok, f"Instalado ({shutil.which('ffmpeg')})" if ffmpeg_ok else "Falta instalar (sudo apt install ffmpeg)"))

    es_wsl = os.path.exists("/mnt/c/Windows")
    ps_ok = shutil.which("powershell.exe") is not None if es_wsl else True
    checks.append(("Puente de Audio / SO", ps_ok, "WSL -> Windows SoundPlayer activo" if es_wsl else "Audio Nativo OS"))

    try:
        inicializar_db()
        db_ok = os.path.exists(DB_PATH)
    except Exception:
        db_ok = False
    checks.append(("Memoria SQLite + RAG Vectorial", db_ok, f"Operativa en {DB_PATH}" if db_ok else "Error al inicializar DB"))

    cred_ok = os.path.exists("credentials.json") or os.path.exists("token.json")
    checks.append(("Google OAuth2 (Calendar/Gmail)", cred_ok, "Credenciales detectadas" if cred_ok else "No se encontró credentials.json / token.json"))

    pm = PluginManager()
    tools = pm.cargar_plugins()
    checks.append(("Plugins Dinámicos", len(tools) > 0, f"{len(tools)} herramientas registradas sin errores"))

    print("\n\033[1;37mResumen de Salud:\033[0m")
    for nombre, estado, detalle in checks:
        icono = "\033[1;32m[OK]\033[0m" if estado else "\033[1;31m[FALLO]\033[0m"
        print(f"  {icono} {nombre:<30} -> {detalle}")
    print("")

def cmd_stats():
    """Muestra las métricas de telemetría de IA acumuladas (latencia, tokens y trazas)."""
    res = TelemetryLogger.obtener_resumen()
    print("\n\033[1;36m====================================================\033[0m")
    print("\033[1;36m   J.A.R.V.I.S. TELEMETRY - Métricas de Agente\033[0m")
    print("\033[1;36m====================================================\033[0m")
    print(f"  • Consultas procesadas : {res['total_consultas']}")
    print(f"  • Latencia promedio    : {res['latencia_promedio_ms']} ms")
    print(f"  • Tokens acumulados    : {res['tokens_acumulados']} tokens\n")
    if res["ultimas"]:
        print("  Últimas trazas registradas:")
        for mod, lat, tok, fecha in res["ultimas"]:
            print(f"   - [{fecha}] {mod:<22} | {lat:>5} ms | {tok:>5} tok")
    print("")

def main():
    parser = argparse.ArgumentParser(description="CLI Oficial de J.A.R.V.I.S. (OpenJarvis Architecture)")
    subparsers = parser.add_subparsers(dest="comando", help="Comandos disponibles")

    subparsers.add_parser("doctor", help="Verifica el estado de salud de todos los módulos y dependencias")
    subparsers.add_parser("stats", help="Muestra las métricas de telemetría (latencia, tokens y modelos)")
    subparsers.add_parser("chat", help="Inicia JARVIS completo (HUD + Voz + Bucle Interactivo)")
    
    parser_ask = subparsers.add_parser("ask", help="Envía una consulta directa a JARVIS desde la terminal")
    parser_ask.add_argument("pregunta", type=str, help="Consulta para JARVIS")

    parser_serve = subparsers.add_parser("serve", help="Inicia el servidor FastAPI + WebSockets en segundo plano")
    parser_serve.add_argument("--port", type=int, default=8000, help="Puerto del servidor (default: 8000)")

    args = parser.parse_args()

    if args.comando == "doctor":
        cmd_doctor()
    elif args.comando == "stats":
        cmd_stats()
    elif args.comando == "ask":
        from core.agent_engine import JarvisAgent
        from core.voice_engine import VoiceEngine
        agent = JarvisAgent()
        voice = VoiceEngine()
        resp = agent.procesar_consulta(args.pregunta)
        voice.hablar(resp)
    elif args.comando == "serve":
        import uvicorn
        print(f"\033[1;36m > Iniciando Servidor OpenJarvis en http://127.0.0.1:{args.port} ...\033[0m")
        uvicorn.run("core.server:app", host="127.0.0.1", port=args.port, reload=False)
    else:
        import lanzar_jarvis
        lanzar_jarvis.main()

if __name__ == "__main__":
    main()
