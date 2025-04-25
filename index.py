import sys
import math
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QPen, QPixmap, QRegion, QFont, QMouseEvent, QKeyEvent
from PyQt6.QtCore import QTimer, Qt, QTime, QRect, QPoint

class ClockWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('カスタム可能アナログ時計')
        self.resize(400, 400)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._drag_pos = QPoint()
        self._bg_offset = QPoint(0, 0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)

    def paintEvent(self, event):
        size = min(self.width(), self.height())
        center = QPoint(self.width() // 2, self.height() // 2)
        radius = size // 2

        bg = QPixmap("background.png").scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        circle = QRegion(QRect(center.x() - radius, center.y() - radius, size, size), QRegion.RegionType.Ellipse)
        self.setMask(circle)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.drawPixmap(self._bg_offset, bg)
        painter.translate(center)

        time = QTime.currentTime()

        def draw_hand(angle_deg, length_ratio, color, width_ratio):
            painter.save()
            painter.rotate(angle_deg)
            pen = QPen(color, size * width_ratio, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(0, 0, 0, -int(radius * length_ratio))
            painter.restore()

        # 文字盤
        painter.setPen(Qt.GlobalColor.black)
        font = QFont('Arial', int(radius * 0.1))
        painter.setFont(font)
        for i in range(1, 13):
            angle = math.radians((i - 3) * 30)
            x = int(math.cos(angle) * radius * 0.75)
            y = int(math.sin(angle) * radius * 0.75)
            text = str(i)
            metrics = painter.fontMetrics()
            w = metrics.horizontalAdvance(text)
            h = metrics.height()
            painter.drawText(x - w // 2, y + h // 4, text)

        # 針
        draw_hand(30 * (time.hour() % 12 + time.minute() / 60), 0.5, Qt.GlobalColor.black, 0.015)
        draw_hand(6 * time.minute(), 0.75, Qt.GlobalColor.darkBlue, 0.01)
        draw_hand(6 * time.second(), 0.9, Qt.GlobalColor.red, 0.005)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def keyPressEvent(self, event: QKeyEvent):
        if event.modifiers() & Qt.KeyboardModifier.AltModifier:
            # 背景画像の微調整（Alt + 矢印）
            if event.key() == Qt.Key.Key_Up:
                self._bg_offset.setY(self._bg_offset.y() - 1)
            elif event.key() == Qt.Key.Key_Down:
                self._bg_offset.setY(self._bg_offset.y() + 1)
            elif event.key() == Qt.Key.Key_Left:
                self._bg_offset.setX(self._bg_offset.x() - 1)
            elif event.key() == Qt.Key.Key_Right:
                self._bg_offset.setX(self._bg_offset.x() + 1)

            # サイズ変更（Alt + 数字）
            elif Qt.Key.Key_1 <= event.key() <= Qt.Key.Key_9:
                new_size = 100 * (event.key() - Qt.Key.Key_0) + 100  # Alt+1 → 200, Alt+2 → 300 ...
                self.resize(new_size, new_size)

            self.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    clock = ClockWidget()
    clock.show()
    sys.exit(app.exec())
