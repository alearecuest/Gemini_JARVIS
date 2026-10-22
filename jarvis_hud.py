import sys
import random
import psutil
import datetime
import requests
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QFrame
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont

from jarvis_3d_widget import Jarvis3DHologram

# Importamos nuestro componente holográfico 3D modular
from jarvis_3d_widget import Jarvis3DHologram

class JarvisHUD(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_datos)
        self.timer.start(1000)

        self.timer_audio = QTimer(self)
        self.timer_audio.timeout.connect(self.animar_espectro)
        self.timer_audio.start(80)

    def initUI(self):
        self.setWindowTitle("J.A.R.V.I.S.")
        self.setFixedSize(380, 580)  # Ampliamos ligeramente para alojar el holograma 3D
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

        # --- NÚCLEO HOLOGRÁFICO 3D ---
        self.holograma_3d = Jarvis3DHologram(self.marco)
        marco_layout.addWidget(self.holograma_3d, alignment=Qt.AlignmentFlag.AlignCenter)

        # Estado del Asistente
        self.lbl_estado = QLabel("ESTADO: EN ESPERA", self.marco)
        self.lbl_estado.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        self.lbl_estado.setStyleSheet("color: #00ff66; border: none; padding: 6px;")
        self.lbl_estado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        marco_layout.addWidget(self.lbl_estado)

        # Línea divisoria
        linea = QFrame()
        linea.setFrameShape(QFrame.Shape.HLine)
        linea.setStyleSheet("background-color: #00ffff; border: none;")
        marco_layout.addWidget(linea)

        # Telemetría
        self.lbl_telemetria = QLabel("Cargando telemetría...", self.marco)
        self.lbl_telemetria.setFont(QFont("Consolas", 10))
        self.lbl_telemetria.setStyleSheet("color: #a0ffff; border: none; padding: 6px;")
        marco_layout.addWidget(self.lbl_telemetria)

        # Espectro de audio
        self.contenedor_espectro = QHBoxLayout()
        self.contenedor_espectro.setSpacing(4)
        self.contenedor_espectro.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.barras_audio = []
        for _ in range(12):
            barra = QFrame()
            barra.setFixedSize(14, 20)
            barra.setStyleSheet("background-color: #00ffff; border-radius: 3px;")
            self.contenedor_espectro.addWidget(barra)
            self.barras_audio.append(barra)
            
        marco_layout.addLayout(self.contenedor_espectro)

        # Agenda
        lbl_agenda_tit = QLabel("--- AGENDA PRÓXIMA ---", self.marco)
        lbl_agenda_tit.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        lbl_agenda_tit.setStyleSheet("color: #00ffff; border: none; margin-top: 5px;")
        marco_layout.addWidget(lbl_agenda_tit)

        self.lbl_agenda = QLabel("Sincronizando Google Calendar...", self.marco)
        self.lbl_agenda.setFont(QFont("Consolas", 8))
        self.lbl_agenda.setStyleSheet("color: #e0e0e0; border: none; padding: 3px;")
        self.lbl_agenda.setWordWrap(True)
        marco_layout.addWidget(self.lbl_agenda)

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
        
        try:
            clima = requests.get("https://wttr.in/Montevideo?format=%C,+%t&lang=es", timeout=1).text.strip()
        except Exception:
            clima = "Sin conexión"

        ahora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        texto_telemetria = f"📅 {ahora}\n🌤️ Clima: {clima}\n💻 CPU: {cpu}%  |  RAM: {ram}%"
        self.lbl_telemetria.setText(texto_telemetria)

    def animar_espectro(self):
        colores = ["#00ffff", "#0088ff", "#ff00ff", "#00ff66"]
        for barra in self.barras_audio:
            altura = random.randint(6, 30)
            color = random.choice(colores)
            barra.setFixedHeight(altura)
            barra.setStyleSheet(f"background-color: {color}; border-radius: 3px;")

def arrancar_hud():
    app = QApplication(sys.argv)
    hud = JarvisHUD()
    hud.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    arrancar_hud()