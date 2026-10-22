# *J.A.R.V.I.S. Terminal Assistant*

Un asistente personal de línea de comandos impulsado por IA, diseñado para ejecutarse automáticamente al iniciar la terminal (Zsh/Bash en entornos Linux/WSL). Proporciona un reporte de estado contextual interactivo antes de comenzar tu jornada de desarrollo.

## *Características*

Arranque Automático: Se integra directamente en tu archivo `.zshrc` o `.bashrc`.
Contexto del Sistema: Monitoreo en tiempo real del uso de CPU y memoria RAM local utilizando `psutil`.
Datos Meteorológicos: Integración nativa con `wttr.in` para obtener reportes de clima en vivo.
Inteligencia Artificial: Conectado a la API oficial de Google Gemini (`google-genai`) para generar saludos contextuales, formales y dinámicos basados en el estado actual.
Protocolo de Respaldo (Fallback): Sistema de redundancia que cambia automáticamente de modelo de IA si los servidores principales están saturados, asegurando que el inicio de tu terminal nunca falle.
UI/UX en Consola: Animación holográfica de espectro de audio en color cian durante el procesamiento y efecto visual de máquina de escribir (typewriter) en la salida de texto.

## *Instalación* 

Sigue estos pasos para instalar a J.A.R.V.I.S. en tu entorno local:

### *1. Clonar el repositorio*

```bash
git clone https://github.com/tu-usuario/jarvis-terminal.git
cd jarvis-terminal
```

### *2. Crear entorno virtual e instalar dependencias*

Es altamente recomendado usar un entorno virtual para evitar el error `externally-managed-environment` en distribuciones modernas de Linux.

```bash
# Crear el entorno virtual oculto en tu directorio home
python3 -m venv ~/.jarvis_env

# Instalar las librerías necesarias dentro del entorno
~/.jarvis_env/bin/pip install google-genai psutil
```

### *3. Configurar API Key*

- Obtén tu clave de API gratuita en Google AI Studio.
- Abre tu archivo de configuración de terminal (por ejemplo, `~/.zshrc` o `~/.bashrc`) y añade tu clave:

```bash
export GEMINI_API_KEY="TU_API_KEY_AQUI"
```


### *4. Vincular al inicio de sesión*

En el mismo archivo de configuración de tu terminal (`~/.zshrc`), agrega la siguiente línea al final para ejecutar el script usando el Python del entorno virtual:

```bash
~/.jarvis_env/bin/python /ruta/absoluta/a/tu/jarvis.py
```
(Nota: asegúrate de cambiar `/ruta/absoluta/a/tu/jarvis.py` por la ruta real donde clonaste este repositorio, o muévelo a `~/.jarvis.py` como en la configuración original).


## *Uso*

Una vez configurado, simplemente recarga tu terminal:

```bash
source ~/.zshrc
```
A partir de este momento, cada vez que abras una nueva ventana de terminal o inicies sesión en WSL, J.A.R.V.I.S. evaluará tu sistema y te dará la bienvenida.


## *Tecnologías Utilizadas*

Python 3
Google Gemini API (`google-genai`)
`psutil` (Métricas de hardware)
Zsh / Bash
WSL / Ubuntu

---
