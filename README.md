# J.A.R.V.I.S. // Desktop AI Assistant

Un asistente personal inteligente nativo de escritorio para Windows, diseñado con arquitectura modular, interfaz gráfica holográfica flotante (HUD en PyQt6) con renderizado 3D, síntesis de voz neuronal (`edge-tts`) y control por voz con bucle de conversación fluida y automatización mediante Function Calling.

---

## Características Principales

- **Arquitectura Modular:** Separación limpia de responsabilidades en archivos auxiliares especializados (`jarvis_core.py`, `jarvis_tools.py`, `jarvis_hud.py` y `jarvis_3d_widget.py`).
- **Interfaz Gráfica HUD (PyQt6):** Ventana flotante translúcida sin bordes con estética tecnológica, telemetría en tiempo real (CPU, RAM, clima en Montevideo) y un **núcleo holográfico tridimensional interactivo**.
- **Espectro de Audio Dinámico:** Animación visual de ecualizador con destellos de colores en tiempo real que acompañan el estado del sistema.
- **Voz Neuronal Natural:** Respuestas sintetizadas en alta calidad mediante `edge-tts` (con soporte para voz regional `es-UY-MateoNeural`).
- **Integración con Google APIs (OAuth2):**
  - **Google Calendar:** Agendar, consultar y eliminar eventos reales por voz.
  - **Gmail:** Lectura inteligente de correos no leídos y resúmenes de bandeja de entrada.
- **Búsqueda Web en Vivo:** Consulta automática de noticias, clima y datos de actualidad en internet mediante `ddgs` (DuckDuckGo) y Google News RSS.
- **Control de Sistema Windows:** Apertura de aplicaciones (Notepad++, Chrome, Calculadora) y control multimedia/volumen por comandos de voz.
- **Sistema de Respaldo por IA (Fallback):** Selección dinámica de modelos de Gemini (`gemini-3.5-flash-lite`, `gemini-3.6-flash`, etc.) para evitar bloqueos por cuota (`429`) o saturación de servidores (`503`).

---

## Estructura del Proyecto

```text
JARVIS_App/
│
├── jarvis_core.py         # Núcleo principal de voz, reconocimiento y cerebro IA
├── jarvis_tools.py        # Módulo con integraciones (Calendar, Gmail, Web, Windows)
├── jarvis_hud.py          # Interfaz gráfica principal (HUD flotante y telemetría)
├── jarvis_3d_widget.py    # Componente visual con renderizado holográfico 3D
├── lanzar_jarvis.py       # Script lanzador unificado en paralelo
├── iniciar_jarvis.vbs     # Script de ejecución en segundo plano (sin consola)
├── requirements.txt       # Dependencias del proyecto
├── credentials.json       # Credenciales OAuth2 de Google Cloud
└── token.json             # Token de sesión generado automáticamente
```

---

## Requisitos e Instalación

### 1. Clonar el repositorio y configurar el entorno virtual

```powershell
git clone https://github.com/tu-usuario/JARVIS_App.git
cd JARVIS_App
python -m venv venv
venv\Scripts\activate
```

### 2. Instalar Dependencias

```powershell
pip install google-genai google-auth-oauthlib google-api-python-client edge-tts pygame psutil PyQt6 ddgs requests
```

### 3. Credenciales de Google Cloud

Coloca tu archivo `credentials.json` (configurado en Google Cloud Console con permisos para Google Calendar y Gmail) en la raíz del proyecto. El sistema generará el archivo `token.json` automáticamente durante la primera autenticación.

---

## Uso

### Método 1: Lanzador integrado desde consola

```powershell
python lanzar_jarvis.py
```

### Método 2: Aplicación de escritorio independiente (sin consola)

Puedes utilizar el script `iniciar_jarvis.vbs` o crear un acceso directo en tu escritorio apuntando a él para levantar la interfaz gráfica y el núcleo de voz de forma totalmente nativa con un doble clic.

---

## Tecnologías Utilizadas

- **Python 3**
- **Google GenAI SDK & Gemini API**
- **PyQt6** — Interfaz gráfica, layouts y renderizado vectorial 3D
- **SpeechRecognition & Edge-TTS** — Reconocimiento de voz y síntesis neuronal
- **Google Calendar & Gmail APIs**
- **psutil & requests** — Métricas de hardware y clima en tiempo real