import math
import random
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPainter, QColor, QPen

class Jarvis3DHologram(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(160, 160)
        
        # Variables de rotación y animación 3D
        self.angulo_x = 0.0
        self.angulo_y = 0.0
        self.angulo_z = 0.0
        self.velocidad_giro = 0.03
        
        # Temporizador de renderizado fluido a ~60 FPS
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_animacion)
        self.timer.start(16)

    def actualizar_animacion(self):
        # Incrementa los ángulos para generar rotación tridimensional en los 3 ejes
        self.angulo_x += self.velocidad_giro * 0.7
        self.angulo_y += self.velocidad_giro
        self.angulo_z += self.velocidad_giro * 0.4
        self.update() # Forzar redibujado de la ventana

    def set_modo_activo(self, activo=True):
        # Acelera el giro holográfico cuando JARVIS está procesando o hablando
        self.velocidad_giro = 0.08 if activo else 0.025

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        cx, cy = self.width() / 2, self.height() / 2
        radio_base = 55.0

        # Dibujar anillos concéntricos simulando malla esférica 3D
        num_anillos = 3
        for i in range(num_anillos):
            offset = i * 15
            r = radio_base - offset
            
            # Perspectiva y rotación en seno/coseno
            factor_y = math.cos(self.angulo_x + i) * 0.35
            radio_actual_y = r * (1.0 + factor_y)

            painter.save()
            painter.translate(cx, cy)
            painter.rotate(math.degrees(self.angulo_z + (i * 0.5)))

            # Color cian holográfico con transparencia variable
            color = QColor(0, 255, 255, 180 if i == 0 else 110)
            painter.setPen(QPen(color, 1.8 if i == 0 else 1.2, Qt.PenStyle.DashLine if i > 0 else Qt.PenStyle.SolidLine))
            
            # Dibujar órbita elíptica 3D
            painter.drawEllipse(int(-r), int(-radio_actual_y), int(r * 2), int(radio_actual_y * 2))
            painter.restore()

        # Núcleo central pulsante de energía
        pulso = abs(math.sin(self.angulo_y * 2)) * 6
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 255, 255, 60))
        painter.drawEllipse(int(cx - 15 - pulso/2), int(cy - 15 - pulso/2), int(30 + pulso), int(30 + pulso))

        painter.setBrush(QColor(200, 255, 255, 220))
        painter.drawEllipse(int(cx - 5), int(cy - 5), 10, 10)