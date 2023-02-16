import numpy as np
from PyQt5.Qt import *
import os
from detect_ellipse import *
import threading
import copy

class LabelPro(QLabel):
    rec_list_change = pyqtSignal([list, str])
    def __init__(self, *args):
        super(LabelPro, self).__init__(*args)

        self.rec = []           # 最后一个绘制的矩形
        self.rec_list = []      # 当前图像中的所有矩形 [[], [], ..., []]
        self.image_rec = []     # 所有图像中的矩形 [[rec_list], [rec_list], ..., [rec_list]]

        self.last_point: np.array = None  # 最后选择的点
        self.point_list = np.array([], dtype=np.int)  # 当前图像中的所有点

        self.setMouseTracking(True)
        self.line = []
        self.mouse_is_in = False
        self.can_rec = True
        self.left_button = False
        self.right_button = False
        self.text = ''

        self.out_width = None
        self.out_height = None


    def rec_the_image_outside(self, width, height):
        self.out_width = width
        self.out_height = height
        self.update()

    def rec_clean(self, index, type_str):
        if type_str == 'next':
            self.rec = []
            self.rec_list = []
            self.line = []
            self.text = '重置'
            self.rec_list_change[list, str].emit(self.rec_list, self.text)
        elif type_str == 'last':
            self.rec = []
            self.rec_list = []
            self.line = []
            self.text = '重置'
            self.rec_list_change[list, str].emit(self.rec_list, self.text)


    def rec_pop(self):
        if len(self.rec_list) <= 0:
            return
        self.rec_list.pop()
        if len(self.rec_list) > 0:
            self.rec = self.rec_list[-1][0]
        else:
            self.rec = []
        self.rec_list_change[list, str].emit(self.rec_list, '删除')
        self.update()


    def enterEvent(self, evt) -> None:
        self.mouse_is_in = True

    def mousePressEvent(self, evt) -> None:
        if evt.button() == Qt.MouseButton.LeftButton and self.can_rec is True:
            self.left_button = True
            self.rec = [evt.x(), evt.y(), 0, 0]
        if evt.button() == Qt.MouseButton.RightButton:
            self.right_button = True
            self.last_point = np.array([evt.x(), evt.y()], dtype=np.int32)

    def mouseMoveEvent(self, evt) -> None:
        self.line = [QPoint(0, evt.y()), QPoint(self.width(), evt.y()), QPoint(evt.x(), 0),
                     QPoint(evt.x(), self.height())]
        if self.left_button is True and self.can_rec is True:
            startx, starty = self.rec[0: 2]
            if evt.x() < 0:
                finalx = 0
            elif evt.x() > self.width():
                finalx = self.width()
            else:
                finalx = evt.x()
            if evt.y() < 0:
                finaly = 0
            elif evt.y() > self.height():
                finaly = self.height()
            else:
                finaly = evt.y()
            self.rec = [startx, starty, finalx - startx, finaly - starty]

        self.update()

    def mouseReleaseEvent(self, evt) -> None:
        if self.left_button is True and self.can_rec is True:
            startx, starty = self.rec[0: 2]
            if evt.x() < 0:
                finalx = 1
            elif evt.x() > self.width():
                finalx = self.width() - 1
            else:
                finalx = evt.x()
            if evt.y() < 0:
                finaly = 1
            elif evt.y() > self.height():
                finaly = self.height() - 1
            else:
                finaly = evt.y()

            if abs(finalx - startx) > 10 and abs(finaly - starty) > 10:
                if startx > finalx:
                    temp = startx
                    startx = finalx
                    finalx = temp
                if starty > finaly:
                    temp = starty
                    starty = finaly
                    finaly = temp
                self.rec = [startx, starty, finalx - startx, finaly - starty]
                self.update()
                self.rec_list.append((self.rec, False))
                self.rec_list_change[list, str].emit(self.rec_list, '添加')
                self.left_button = False
            else:
                self.update()
                self.rec = []
                self.left_button = False
        if self.right_button is True:
            self.point_list = np.append(self.point_list, self.last_point)
            self.last_point = None
            self.right_button = False

    def leaveEvent(self, evt) -> None:
        self.mouse_is_in = False
        self.line = []
        self.update()

    def paintEvent(self, evt) -> None:
        super(LabelPro, self).paintEvent(evt)

        if self.out_height is not None and self.out_width is not None:
            topleft_x = int((self.width() - self.out_width) / 2)
            topleft_y = int((self.height() - self.out_height) / 2)
            rec_width = int(self.out_width)
            rec_height = int(self.out_height)
            rec = [topleft_x, topleft_y, rec_width, rec_height]
            qp = QPainter()
            qp.begin(self)

            pen_blue = QPen(Qt.blue, 2)
            qp.setPen(pen_blue)
            qp.drawRect(*rec)

            qp.end()

        qp = QPainter()
        qp.begin(self)

        if len(self.line) > 0:
            self.drawLine(qp)
        if self.rec:
            self.drawRec(qp)
        qp.end()

    def drawRec(self, qp):
        def draw_done_rec(rec_list):
            pen_red = QPen(Qt.red, 2)
            pen_green = QPen(Qt.green, 2)
            if len(self.rec_list) > 0:
                for i in rec_list:
                    if i[1] is True:
                        qp.setPen(pen_green)
                        qp.drawRect(QRect(*(i[0])))
                    else:
                        qp.setPen(pen_red)
                        qp.drawRect(QRect(*(i[0])))

        pen_red = QPen(Qt.red, 2)
        qp.setPen(pen_red)
        qp.drawRect(*self.rec)
        draw_done_rec(self.rec_list)

    def drawLine(self, qp):
        pen = QPen(Qt.gray, 1)
        qp.setPen(pen)
        qp.drawLine(self.line[0], self.line[1])
        qp.drawLine(self.line[2], self.line[3])