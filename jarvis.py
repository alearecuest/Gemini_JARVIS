import os
import sys
import datetime
import urllib.request
import psutil
import time
import threading
import subprocess
import random
from google import genai

is_thinking = True

def animate_spectrum():
    """Genera una animación de espectro de audio en color cian mientras JARVIS procesa"""
    bars = [' ', '▂', '▃', '▄', '▅', '▆', '▇', '█']
    while is_thinking:
        spectrum = "".join(random.choice(bars) for _ in range(30))
        sys.stdout.write(f"\r\033[36m[J.A.R.V.I.S. ENLAZANDO] {spectrum}\033[0m")
        sys.stdout.flush()
        time.sleep(0.08)
    sys.stdout.write("\r" + " " * 60 + "\r")

def typewriter_print(text, speed=0.015):
    """Efecto visual de escritura letra por letra en color cian brillante"""
    sys.stdout.write("\033[1;36m")
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    sys.stdout.write("\033[0m\n")

if not os.environ.get("GEMINI_API_KEY"):
    sys.exit()

anim_thread = threading.Thread(target=animate_spectrum)
anim_thread.start()

try:
    time.sleep(2)
    client = genai.Client()
    fecha_hora = datetime.datetime.now().strftime("%A, %d de %B de %Y - %H:%M")
    usuario = "Alejandro"
    
    try:
        req = urllib.request.Request("https://wttr.in/Montevideo?format=%C+%t", headers={'User-Agent': 'Mozilla/5.0'})
        clima = urllib.request.urlopen(req, timeout=2).read().decode('utf-8').strip()
    except:
        clima = "Sistemas meteorológicos offline"

    cpu = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory().percent

    prompt = f"""
    Actúa como JARVIS. El usuario {usuario} acaba de iniciar sesión.
    Datos: {fecha_hora}. Clima: {clima}. CPU: {cpu}%. RAM: {ram}%.
    Genera un saludo de máximo 4 líneas. Menciona los datos. Tono tecnológico, de IA avanzada. Dirígete a él exclusivamente como "Alejandro", nunca uses nombres de usuario de sistema.
    """

    modelos = ['gemini-3.8-flash', 'gemini-1.5-flash']
    mensaje = None

    for modelo in modelos:
        try:
            response = client.models.generate_content(
                model=modelo,
                contents=prompt,
            )
            mensaje = response.text.strip()
            break
        except Exception:
            continue

    if not mensaje:
        mensaje = "Alerta: Red global inaccesible. Operando con módulos de memoria locales. Sistemas listos para desarrollo."

except Exception as e:
    mensaje = f"Error crítico en el núcleo del sistema: {e}"

finally:
    is_thinking = False
    anim_thread.join()

    print("\n\033[36m" + "="*60 + "\033[0m")
    print("\033[1;36m" + "S I S T E M A   E N   L Í N E A  -  I N T E R F A Z  J.A.R.V.I.S." + "\033[0m")
    print("\033[36m" + "="*60 + "\033[0m\n")
    
    typewriter_print(mensaje)
    
    print("\n\033[36m" + "="*60 + "\033[0m\n")

try:
    texto_limpio = mensaje.replace("'", "")
    ps_command = f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{texto_limpio}')"
    subprocess.run(["powershell.exe", "-Command", ps_command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except Exception as e:
    print(f"\033[31m[Error de módulo de voz: {e}]\033[0m")
