# J.A.R.V.I.S. v2.1 — OpenJarvis Modular AI Framework

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)
![Gemini](https://img.shields.io/badge/Google%20Gemini-3.5%20%7C%203.6%20Flash-orange?logo=google&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-WebSockets%20Server-009688?logo=fastapi&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20WSL2%20Ubuntu-0078D6?logo=linux&logoColor=white)

Framework de agente de inteligencia artificial personal **local-first e híbrido**, inspirado en la arquitectura modular de **OpenJarvis**. Combina razonamiento multi-modelo (Google Gemini Cloud + Fallback local con Ollama), autodescubrimiento dinámico de plugins, memoria semántica vectorial (RAG), telemetría de inferencia en tiempo real, voz neuronal rioplatense y una interfaz gráfica holográfica 3D reactiva en PyQt6.

---

## Arquitectura del Sistema (`v2.1`)

```text
Gemini_JARVIS/
├── core/
│   ├── agent_engine.py      # Cerebro IA: Autodescubrimiento Gemini + Enrutador Local (Ollama)
│   ├── plugin_manager.py    # Cargador dinámico de herramientas mediante decorador @jarvis_tool
│   ├── server.py            # Servidor API REST + WebSockets (/ws/state) con FastAPI
│   ├── state_bus.py         # Bus de sincronización en tiempo real (IDLE, LISTENING, THINKING, SPEAKING)
│   ├── telemetry.py         # Trazabilidad de agente: latencia (ms), tokens y auditoría SQLite
│   └── voice_engine.py      # Motor TTS Neuronal (es-UY-MateoNeural) + Puente WAV Síncrono WSL/Windows
├── memory/
│   ├── local_memory.py      # Persistencia SQLite para recuerdos episódicos y trazas
│   └── rag_engine.py        # Motor RAG Vectorial (Embeddings + Cosine Similarity con NumPy)
├── plugins/                 # Ecosistema de 14 herramientas autodescubiertas en caliente
│   ├── dev_tools.py         # Inspección de estado Git y exploración de archivos locales
│   ├── google_workspace.py  # Integración OAuth2 en vivo con Google Calendar y Gmail
│   ├── memory_tools.py      # Guardado, búsqueda semántica RAG e ingesta de documentos locales
│   ├── system_win.py        # Telemetría de hardware (CPU/RAM/Batería), volumen y lanzamiento de apps
│   └── web_search.py        # Búsqueda web (DuckDuckGo), Google News RSS y meteorología (wttr.in)
├── ui/
│   ├── jarvis_3d_widget.py  # Núcleo holográfico 3D reactivo a estados del agente
│   └── jarvis_hud.py        # HUD transparente en PyQt6 con espectro de audio y telemetría IA en vivo
├── jarvis_cli.py            # CLI unificado estilo OpenJarvis (doctor, stats, ask, serve, chat)
└── lanzar_jarvis.py         # Orquestador de arranque multiproceso (HUD + Voz + Agente)
```

---

## Características Principales

- **Autodescubrimiento de Plugins (`@jarvis_tool`)**: Cualquier función decorada dentro de `plugins/` es detectada, tipada e inyectada automáticamente en las capacidades de Function Calling del agente al iniciar.
- **Memoria Híbrida (SQLite + RAG Vectorial)**: Almacena notas permanentes y permite indexar documentos o código fuente local, realizando búsquedas por significado semántico mediante Cosine Similarity.
- **Puente de Audio Híbrido WSL2 ↔ Windows**: Detecta automáticamente si corre en Linux/WSL sin placa ALSA, convierte la síntesis neuronal de edge-tts con ffmpeg y la reproduce de forma síncrona a través del subsistema Media.SoundPlayer de Windows.
- **Enrutador Multi-Modelo Resiliente**: Descubre dinámicamente los modelos gemini-3.x-flash disponibles en la cuenta y cuenta con fallback automático hacia motores locales (Ollama) en caso de corte de conectividad.
- **Telemetría y Trazas (Agent Traces)**: Registra cada consulta en base de datos midiendo modelo utilizado, tiempo de inferencia en milisegundos (ms) y consumo total de tokens, visualizables tanto en el HUD 3D como por CLI.

---

## Ecosistema de Plugins Activos (14 Tools)

| Módulo | Herramienta Registrada | Descripción |
|--------|------------------------|-------------|
| `dev_tools.py` | `consultar_estado_git` | Informa rama activa, último commit y archivos modificados del repositorio. |
| | `explorar_directorio_local` | Lista archivos y estructura de cualquier carpeta del proyecto. |
| `google_workspace.py` | `consultar_agenda_calendar` | Lee los próximos eventos en tiempo real desde Google Calendar. |
| | `agendar_evento_calendar` | Crea nuevos eventos en el calendario principal en formato ISO. |
| | `leer_correos_no_leidos` | Obtiene remitentes y asuntos de los correos principales sin leer en Gmail. |
| `memory_tools.py` | `guardar_en_memoria` | Persiste notas y preferencias en SQLite e indexa su vector semántico. |
| | `consultar_memoria` | Ejecuta búsqueda híbrida (Vectorial RAG + SQLite) sobre los recuerdos. |
| | `indexar_documento_local` | Fragmenta (chunking) e indexa archivos `.md`, `.txt` o `.py` en la base RAG. |
| `system_win.py` | `obtener_telemetria_sistema` | Reporta uso de CPU, memoria RAM y estado de la batería. |
| | `abrir_aplicacion_sistema` | Inicia aplicaciones locales (VS Code, Chrome, Calculadora, Notepad++, etc.). |
| | `controlar_volumen_sistema` | Sube, baja o silencia el audio maestro de Windows desde Windows o WSL. |
| `web_search.py` | `buscar_en_internet` | Realiza búsquedas web en tiempo real mediante DuckDuckGo (ddgs). |
| | `obtener_noticias_actuales` | Extrae los últimos titulares desde el feed RSS de Google News. |
| | `consultar_clima` | Obtiene estado meteorológico, temperatura, humedad y viento actual. |

---

## Uso del CLI Oficial (`jarvis_cli.py`)

El proyecto incluye una interfaz de línea de comandos inspirada en OpenJarvis:

### 1. Diagnóstico de Salud del Sistema (`doctor`)

Verifica clave de API, códec FFmpeg, puente de audio WSL/Windows, base de datos SQLite/RAG, credenciales OAuth2 de Google y carga de plugins:

```bash
python3 jarvis_cli.py doctor
```

### 2. Consulta Directa con Respuesta por Voz (`ask`)

Envía una orden puntual al agente, ejecuta los plugins necesarios y reproduce la respuesta por voz:

```bash
python3 jarvis_cli.py ask "Revisá el estado de Git de este proyecto y decime el clima en Montevideo"
```

### 3. Métricas y Telemetría de Inferencia (`stats`)

Muestra el total de consultas procesadas, la latencia promedio en milisegundos, los tokens acumulados y las últimas trazas:

```bash
python3 jarvis_cli.py stats
```

### 4. Servidor API FastAPI + WebSockets (`serve`)

Levanta el backend en `http://127.0.0.1:8000` (con documentación Swagger en `/docs` y stream de estado en vivo en `/ws/state`):

```bash
python3 jarvis_cli.py serve --port 8000
```

### 5. Experiencia Completa con HUD Holográfico 3D (`chat`)

Inicia el HUD gráfico en PyQt6 sincronizado con el bucle de voz (o consola interactiva en WSL):

```bash
python3 jarvis_cli.py chat
# o directamente:
python3 lanzar_jarvis.py
```

---

## Instalación Rápida

```bash
# 1. Clonar el repositorio
git clone https://github.com/alearecuest/Gemini_JARVIS.git
cd Gemini_JARVIS

# 2. Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install google-genai google-api-python-client google-auth-oauthlib \
            ddgs requests psutil edge-tts pygame PyQt6 SpeechRecognition \
            numpy fastapi uvicorn websockets

# 4. Configurar API Key y verificar estado
export GEMINI_API_KEY="tu_api_key_aqui"
python3 jarvis_cli.py doctor
```

---

Desarrollado por **Alejandro Arévalo** — Montevideo, Uruguay (2026)
