import os
import sys
import subprocess
import time

def main():
    print("\n\033[1;36m========================================\033[0m")
    print("\033[1;36m   INICIANDO SISTEMAS INTEGRADOS J.A.R.V.I.S.\033[0m")
    print("\033[1;36m========================================\033[0m\n")

    ruta_base = os.path.dirname(os.path.abspath(__file__))
    python_executable = sys.executable  # Usa el python del entorno virtual actual (venv)

    hud_path = os.path.join(ruta_base, "jarvis_hud.py")
    core_path = os.path.join(ruta_base, "jarvis_core.py")

    if not os.path.exists(hud_path) or not os.path.exists(core_path):
        print("\033[1;31m[Error]: No se encuentran 'jarvis_hud.py' o 'jarvis_core.py' en la carpeta.\033[0m")
        return

    try:
        # 1. Lanzamos el HUD gráfico en una ventana separada
        print(" > Lanzando Interfaz Gráfica (HUD)...")
        proceso_hud = subprocess.Popen([python_executable, hud_path])
        
        time.sleep(1) # Breve respiro entre procesos

        # 2. Lanzamos el Núcleo de voz y backend en la terminal actual
        print(" > Activando Núcleo de Voz y Backend...\n")
        proceso_core = subprocess.Popen([python_executable, core_path])

        # Mantiene el lanzador abierto mientras corren los procesos
        proceso_core.wait()

    except KeyboardInterrupt:
        print("\n\033[1;33m[Apagando sistemas de J.A.R.V.I.S.]...\033[0m")
        try:
            proceso_hud.terminate()
            proceso_core.terminate()
        except Exception:
            pass
        print("Sistemas cerrados correctamente. ¡Hasta luego, Alejandro!")

if __name__ == "__main__":
    main()