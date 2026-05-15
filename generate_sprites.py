"""生成默认像素风精灵图"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QFont
from PyQt6.QtCore import Qt, QRect

SIZE = 128
app = QApplication(sys.argv)

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "sprites", "default")


def draw_cat_base(painter: QPainter, body_color: QColor, eye_state="open", offset_y=0):
    """绘制像素猫基础形状"""
    painter.setPen(Qt.PenStyle.NoPen)
    # 身体
    painter.setBrush(body_color)
    painter.drawRoundedRect(34, 50 + offset_y, 60, 50, 15, 15)
    # 头
    painter.drawEllipse(38, 25 + offset_y, 52, 45)
    # 耳朵
    ear_color = body_color.darker(120)
    painter.setBrush(ear_color)
    points_l = [(42, 28 + offset_y), (38, 10 + offset_y), (55, 25 + offset_y)]
    points_r = [(86, 28 + offset_y), (90, 10 + offset_y), (73, 25 + offset_y)]
    from PyQt6.QtGui import QPolygon
    from PyQt6.QtCore import QPoint
    painter.drawPolygon(QPolygon([QPoint(*p) for p in points_l]))
    painter.drawPolygon(QPolygon([QPoint(*p) for p in points_r]))
    # 眼睛
    painter.setBrush(QColor(50, 50, 50))
    if eye_state == "open":
        painter.drawEllipse(50, 40 + offset_y, 10, 12)
        painter.drawEllipse(70, 40 + offset_y, 10, 12)
        painter.setBrush(QColor(255, 255, 255))
        painter.drawEllipse(53, 42 + offset_y, 4, 4)
        painter.drawEllipse(73, 42 + offset_y, 4, 4)
    elif eye_state == "closed":
        pen = QPen(QColor(50, 50, 50), 2)
        painter.setPen(pen)
        painter.drawLine(50, 46 + offset_y, 60, 46 + offset_y)
        painter.drawLine(70, 46 + offset_y, 80, 46 + offset_y)
        painter.setPen(Qt.PenStyle.NoPen)
    elif eye_state == "happy":
        pen = QPen(QColor(50, 50, 50), 2)
        painter.setPen(pen)
        from PyQt6.QtCore import QRectF
        painter.drawArc(QRect(50, 40 + offset_y, 10, 12), 0, 180 * 16)
        painter.drawArc(QRect(70, 40 + offset_y, 10, 12), 0, 180 * 16)
        painter.setPen(Qt.PenStyle.NoPen)
    # 嘴巴
    pen = QPen(QColor(50, 50, 50), 1.5)
    painter.setPen(pen)
    painter.drawLine(62, 55 + offset_y, 58, 58 + offset_y)
    painter.drawLine(62, 55 + offset_y, 66, 58 + offset_y)
    painter.setPen(Qt.PenStyle.NoPen)
    # 尾巴
    painter.setBrush(body_color.darker(110))
    pen = QPen(body_color.darker(130), 4)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    from PyQt6.QtGui import QPainterPath
    path = QPainterPath()
    path.moveTo(90, 85 + offset_y)
    path.cubicTo(105, 75 + offset_y, 110, 60 + offset_y, 100, 50 + offset_y)
    painter.drawPath(path)
    painter.setPen(Qt.PenStyle.NoPen)


def gen_idle():
    """待机：轻微呼吸动画"""
    d = os.path.join(BASE, "idle")
    for i in range(4):
        pix = QPixmap(SIZE, SIZE)
        pix.fill(QColor(0, 0, 0, 0))
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        offset = [0, -1, -2, -1][i]
        draw_cat_base(p, QColor(255, 180, 100), "open", offset)
        p.end()
        pix.save(os.path.join(d, f"idle_{i+1:03d}.png"))


def gen_thinking():
    """思考：头顶问号/省略号"""
    d = os.path.join(BASE, "thinking")
    symbols = [".", "..", "...", "?"]
    for i in range(4):
        pix = QPixmap(SIZE, SIZE)
        pix.fill(QColor(0, 0, 0, 0))
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        draw_cat_base(p, QColor(255, 180, 100), "open", 0)
        # 思考气泡
        p.setBrush(QColor(255, 255, 255, 200))
        p.setPen(QPen(QColor(100, 100, 100), 1))
        p.drawRoundedRect(70, 2, 40, 22, 8, 8)
        p.setPen(QColor(80, 80, 80))
        font = QFont("Consolas", 12, QFont.Weight.Bold)
        p.setFont(font)
        p.drawText(QRect(70, 2, 40, 22), Qt.AlignmentFlag.AlignCenter, symbols[i])
        p.end()
        pix.save(os.path.join(d, f"think_{i+1:03d}.png"))


def gen_coding():
    """写代码：爪子敲键盘"""
    d = os.path.join(BASE, "coding")
    for i in range(4):
        pix = QPixmap(SIZE, SIZE)
        pix.fill(QColor(0, 0, 0, 0))
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        draw_cat_base(p, QColor(255, 180, 100), "open", 0)
        # 小键盘
        p.setBrush(QColor(60, 60, 60))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(30, 95, 68, 20, 4, 4)
        # 按键闪烁
        p.setBrush(QColor(100, 255, 100, 150 + i * 25))
        key_x = 35 + (i * 15)
        p.drawRect(key_x, 99, 12, 12)
        # 代码符号
        p.setPen(QColor(0, 200, 100))
        font = QFont("Consolas", 8)
        p.setFont(font)
        codes = ["{}", "//", "=>", "()"]
        p.drawText(QRect(15, 108, 40, 15), Qt.AlignmentFlag.AlignCenter, codes[i])
        p.end()
        pix.save(os.path.join(d, f"code_{i+1:03d}.png"))


def gen_searching():
    """搜索：放大镜移动"""
    d = os.path.join(BASE, "searching")
    for i in range(4):
        pix = QPixmap(SIZE, SIZE)
        pix.fill(QColor(0, 0, 0, 0))
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        draw_cat_base(p, QColor(255, 180, 100), "open", 0)
        # 放大镜
        mag_x = 85 + [0, 5, 10, 5][i]
        mag_y = 20 + [0, -3, 0, 3][i]
        pen = QPen(QColor(80, 80, 80), 3)
        p.setPen(pen)
        p.setBrush(QColor(200, 230, 255, 150))
        p.drawEllipse(mag_x, mag_y, 20, 20)
        p.drawLine(mag_x + 17, mag_y + 17, mag_x + 25, mag_y + 25)
        p.end()
        pix.save(os.path.join(d, f"search_{i+1:03d}.png"))


def gen_happy():
    """开心：跳跃"""
    d = os.path.join(BASE, "happy")
    for i in range(4):
        pix = QPixmap(SIZE, SIZE)
        pix.fill(QColor(0, 0, 0, 0))
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        offset = [0, -8, -12, -6][i]
        draw_cat_base(p, QColor(255, 180, 100), "happy", offset)
        # 星星
        p.setPen(QColor(255, 200, 0))
        font = QFont("Segoe UI Emoji", 12)
        p.setFont(font)
        if i > 0:
            p.drawText(20 + i * 10, 20, "✦")
            p.drawText(90 - i * 5, 15 + i * 3, "✦")
        p.end()
        pix.save(os.path.join(d, f"happy_{i+1:03d}.png"))


def gen_sleeping():
    """睡觉：闭眼+Zzz"""
    d = os.path.join(BASE, "sleeping")
    for i in range(4):
        pix = QPixmap(SIZE, SIZE)
        pix.fill(QColor(0, 0, 0, 0))
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        draw_cat_base(p, QColor(255, 180, 100), "closed", 2)
        # Zzz
        p.setPen(QColor(150, 150, 255))
        font = QFont("Consolas", 8 + i * 2)
        p.setFont(font)
        p.drawText(85 + i * 3, 20 - i * 4, "z")
        p.end()
        pix.save(os.path.join(d, f"sleep_{i+1:03d}.png"))


if __name__ == "__main__":
    gen_idle()
    gen_thinking()
    gen_coding()
    gen_searching()
    gen_happy()
    gen_sleeping()
    print("精灵图生成完成！")
