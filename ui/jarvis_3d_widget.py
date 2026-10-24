import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPainter, QColor, QPen

class Jarvis3DHologram(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(160, 160)
        self.angulo_x = 0.0
        self.angulo_y = 0.0
        self.angulo_z = 0.0
        self.velocidad_giro = 0.025
        self.color_principal = QColor(0, 255, 255)  # Cian por defecto

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_animacion)
        self.timer.start(16)

    def actualizar_animacion(self):
        self.angulo_x += self.velocidad_giro * 0.7
        self.angulo_y += self.velocidad_giro
        self.angulo_z += self.velocidad_giro * 0.4
        self.update()

    def configurar_estado(self, estado: str):
        if estado == "THINKING":
            self.velocidad_giro = 0.09
            self.color_principal = QColor(255, 0, 255)   # Magenta/Violeta IA procesando
        elif estado == "SPEAKING":
            self.velocidad_giro = 0.065
            self.color_principal = QColor(0, 200, 255)   # Azul eléctrico hablando
        elif estado == "LISTENING":
            self.velocidad_giro = 0.05
            self.color_principal = QColor(0, 255, 120)   # Verde esmeralda escuchando
        else:
            self.velocidad_giro = 0.022
            self.color_principal = QColor(0, 255, 255)   # Cian en guardia

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        cx, cy = self.width() / 2, self.height() / 2
        radio_base = 55.0

        r_col, g_col, b_col = self.color_principal.red(), self.color_principal.green(), self.color_principal.blue()

        for i in range(3):
            offset = i * 15
            r = radio_base - offset
            factor_y = math.cos(self.angulo_x + i) * 0.35
            radio_actual_y = r * (1.0 + factor_y)

            painter.save()
            painter.translate(cx, cy)
            painter.rotate(math.degrees(self.angulo_z + (i * 0.5)))

            color = QColor(r_col, g_col, b_col, 190 if i == 0 else 115)
            estilo = Qt.PenStyle.DashLine if i > 0 else Qt.PenStyle.SolidLine
            painter.setPen(QPen(color, 1.8 if i == 0 else 1.2, estilo))
            painter.drawEllipse(int(-r), int(-radio_actual_y), int(r * 2), int(radio_actual_y * 2))
            painter.restore()

        pulso = abs(math.sin(self.angulo_y * 2)) * 8
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(r_col, g_col, b_col, 65))
        painter.drawEllipse(int(cx - 15 - pulso/2), int(cy - 15 - pulso/2), int(30 + pulso), int(30 + pulso))

        painter.setBrush(QColor(220, 255, 255, 230))
        painter.drawEllipse(int(cx - 5), int(cy - 5), 10, 10)
