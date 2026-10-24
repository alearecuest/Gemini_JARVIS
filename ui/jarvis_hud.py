import sys
import os
import random
import psutil
import datetime
import requests
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QFrame
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont

# Asegurar que la raíz del proyecto esté en el path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.jarvis_3d_widget import Jarvis3DHologram
from core.state_bus import StateBus

class JarvisHUD(QMainWindow):
    def __init__(self):
        super().__init__()
        self.estado_actual = "IDLE"
        self.clima_cache = "Sincronizando..."
        self.ultimo_clima_ts = 0
        self.initUI()
        
        # Timer de telemetría (1s)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_datos)
        self.timer.start(1000)

        # Timer de sincronización de estado y espectro (80ms)
        self.timer_audio = QTimer(self)
        self.timer_audio.timeout.connect(self.sincronizar_estado_y_espectro)
        self.timer_audio.start(80)

    def initUI(self):
        self.setWindowTitle("J.A.R.V.I.S. v2")
        self.setFixedSize(390, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        self.marco = QFrame(central_widget)
        self.marco.setStyleSheet("""
            QFrame {
                background-color: #0b0f19;
                border: 2px solid #00ffff;
                border-radius: 12px;
            }
        """)
        marco_layout = QVBoxLayout(self.marco)
        marco_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Núcleo Holográfico 3D
        self.holograma_3d = Jarvis3DHologram(self.marco)
        marco_layout.addWidget(self.holograma_3d, alignment=Qt.AlignmentFlag.AlignCenter)

        # Estado en Tiempo Real
        self.lbl_estado = QLabel("ESTADO: EN ESPERA", self.marco)
        self.lbl_estado.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        self.lbl_estado.setStyleSheet("color: #00ffff; border: none; padding: 4px;")
        self.lbl_estado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        marco_layout.addWidget(self.lbl_estado)

        # Línea divisoria
        linea = QFrame()
        linea.setFrameShape(QFrame.Shape.HLine)
        linea.setStyleSheet("background-color: #00ffff; border: none;")
        marco_layout.addWidget(linea)

        # Telemetría
        self.lbl_telemetria = QLabel("Cargando telemetría...", self.marco)
        self.lbl_telemetria.setFont(QFont("Consolas", 9))
        self.lbl_telemetria.setStyleSheet("color: #a0ffff; border: none; padding: 6px;")
        marco_layout.addWidget(self.lbl_telemetria)

        # Espectro de audio reactivo
        self.contenedor_espectro = QHBoxLayout()
        self.contenedor_espectro.setSpacing(4)
        self.contenedor_espectro.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.barras_audio = []
        for _ in range(14):
            barra = QFrame()
            barra.setFixedSize(12, 8)
            barra.setStyleSheet("background-color: #00ffff; border-radius: 3px;")
            self.contenedor_espectro.addWidget(barra)
            self.barras_audio.append(barra)
            
        marco_layout.addLayout(self.contenedor_espectro)

        # Consola de Respuesta en Vivo
        lbl_resp_tit = QLabel("--- ÚLTIMA TRANSMISIÓN ---", self.marco)
        lbl_resp_tit.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        lbl_resp_tit.setStyleSheet("color: #00ffff; border: none; margin-top: 6px;")
        lbl_resp_tit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        marco_layout.addWidget(lbl_resp_tit)

        self.lbl_respuesta = QLabel("Esperando órdenes, Alejandro...", self.marco)
        self.lbl_respuesta.setFont(QFont("Consolas", 8))
        self.lbl_respuesta.setStyleSheet("color: #e0e0e0; border: none; padding: 6px;")
        self.lbl_respuesta.setWordWrap(True)
        self.lbl_respuesta.setAlignment(Qt.AlignmentFlag.AlignCenter)
        marco_layout.addWidget(self.lbl_respuesta)

        layout.addWidget(self.marco)
        self.oldPos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.oldPos is not None:
            delta = event.globalPosition().toPoint() - self.oldPos
            self.move(self.pos() + delta)
            self.oldPos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.oldPos = None

    def actualizar_datos(self):
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        
        ahora_ts = datetime.datetime.now().timestamp()
        if ahora_ts - self.ultimo_clima_ts > 300: # Actualizar clima cada 5 min
            try:
                self.clima_cache = requests.get("https://wttr.in/Montevideo?format=%C,+%t&lang=es", timeout=1.5).text.strip()
                self.ultimo_clima_ts = ahora_ts
            except Exception:
                pass

        ahora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        texto_telemetria = f"📅 {ahora}\n🌤️ Montevideo: {self.clima_cache}\n💻 CPU: {cpu}%  |  RAM: {ram}%"
        self.lbl_telemetria.setText(texto_telemetria)

    def sincronizar_estado_y_espectro(self):
        datos = StateBus.leer()
        estado = datos.get("estado", "IDLE")
        detalle = datos.get("detalle", "")
        ultima_resp = datos.get("ultima_respuesta", "")

        self.holograma_3d.configurar_estado(estado)
        self.lbl_estado.setText(f"[{estado}] {detalle}")

        if ultima_resp:
            texto_corto = ultima_resp if len(ultima_resp) <= 160 else ultima_resp[:157] + "..."
            self.lbl_respuesta.setText(f'"{texto_corto}"')

        # El ecualizador solo salta fuerte cuando JARVIS habla o procesa
        colores = ["#00ffff", "#0088ff", "#ff00ff", "#00ff66"]
        for barra in self.barras_audio:
            if estado == "SPEAKING":
                altura = random.randint(8, 34)
                color = random.choice(colores)
            elif estado == "THINKING":
                altura = random.randint(6, 18)
                color = "#ff00ff"
            elif estado == "LISTENING":
                altura = random.randint(5, 14)
                color = "#00ff66"
            else:
                altura = 4
                color = "#005577"
            barra.setFixedHeight(altura)
            barra.setStyleSheet(f"background-color: {color}; border-radius: 3px;")

def arrancar_hud():
    app = QApplication(sys.argv)
    hud = JarvisHUD()
    hud.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    arrancar_hud()
