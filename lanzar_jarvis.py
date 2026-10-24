import os
import sys
import subprocess
import time
from core.agent_engine import JarvisAgent
from core.voice_engine import VoiceEngine
from core.state_bus import StateBus

def main():
    print("\n\033[1;36m==================================================\033[0m")
    print("\033[1;36m   J.A.R.V.I.S. v2 (OpenJarvis Modular Architecture)\033[0m")
    print("\033[1;36m==================================================\033[0m\n")

    ruta_base = os.path.dirname(os.path.abspath(__file__))
    hud_path = os.path.join(ruta_base, "ui", "jarvis_hud.py")

    StateBus.actualizar("IDLE", "Iniciando sistemas...")

    # 1. Lanzar HUD Gráfico en proceso separado
    proceso_hud = None
    if os.path.exists(hud_path):
        print(" > Lanzando Interfaz Gráfica Reactiva (ui/jarvis_hud.py)...")
        try:
            proceso_hud = subprocess.Popen([sys.executable, hud_path])
        except Exception as e:
            print(f"   [!] No se pudo abrir la ventana gráfica en este entorno: {e}")

    time.sleep(1)

    # 2. Inicializar Cerebro IA + Plugins y Motor de Voz
    try:
        agent = JarvisAgent()
        voice = VoiceEngine()
        voice.iniciar_bucle_voz(agent)
    except KeyboardInterrupt:
        print("\n\033[1;33m[Apagando sistemas J.A.R.V.I.S. v2]...\033[0m")
    finally:
        StateBus.actualizar("IDLE", "Sistemas apagados")
        if proceso_hud:
            try:
                proceso_hud.terminate()
            except Exception:
                pass
        print("Sistemas cerrados correctamente. ¡Hasta luego, Alejandro!")

if __name__ == "__main__":
    main()
