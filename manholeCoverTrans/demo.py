from UI2 import *
import cv2
import sys
import math
import numpy as np
from PyQt5.Qt import *


class Window(QWidget, Ui_Form):

    def __init__(self):
        super(Window, self).__init__()
        self.setupUi(self)
        self.lineEdit_range.setText('5')
        self.image = cv2.imread(r'_0_0.png',  cv2.IMREAD_UNCHANGED)
        self.w = self.image.shape[1]
        self.h = self.image.shape[0]
        print(f'w:{self.w}, h:{self.h}')
        self.z_angle = 0
        self.x_angle = 0
        self.dist_ori = 0.1
        self.dist = 0.2

    def show_image(self):
        R_AB = np.array([[math.cos(self.z_angle), math.sin(self.z_angle), 0], [-math.sin(self.z_angle), math.cos(self.z_angle), 0], [0, 0, 1]]).T
        # 绕x轴旋转
        R_BC = np.array([[1, 0, 0], [0, math.cos(self.x_angle), math.sin(self.x_angle)], [0, -math.sin(self.x_angle), math.cos(
            self.x_angle)]]).T
        R_AD = np.dot(R_AB, R_BC)
        t_AD = np.array([-math.sin(self.z_angle), math.cos(self.z_angle), 0]).reshape(3, 1)
        offset = self.dist * math.sin(self.x_angle)
        print(f'offset: \n{offset}\n')
        t_AD = t_AD * offset
        z_offset = self.dist * math.cos(self.x_angle) - self.dist_ori
        t_AD2 = np.array([0, 0, -1]).reshape(3, 1) * z_offset
        t_AD += t_AD2
        K = np.array([[self.w / 2, 0, self.w / 2], [0, self.w / 2, self.h / 2], [0, 0, 1]])
        R_DA = np.linalg.inv(R_AD)
        t_DA = -np.dot(R_DA, t_AD)
        n = np.array([0, 0, 1]).reshape(1, 3)
        nd = n / self.dist_ori
        K_inv = np.linalg.inv(K)
        dot1 = np.dot(t_DA, nd)
        print(f't_DA: \n{t_DA}\n\n'
              f't_AD: \n{t_AD}\n\n'
              f'np: \n{nd}\n\n'
              f'dot1: \n{dot1}\n\n'
              f'dist: \n{self.dist}\n'
              f'-------------------------------------------\n')
        H = np.dot(K, np.dot((R_DA + np.dot(t_DA, nd)), K_inv))
        dst_img = cv2.warpPerspective(self.image, H, (int(self.w * 1), int(self.h * 1)))

        image = cv2.cvtColor(dst_img, cv2.COLOR_BGRA2RGBA)
        image = QImage(image.data, image.shape[1], image.shape[0], image.shape[1] * 4,
                       QImage.Format_RGBA8888)
        self.label_show_image.setPixmap(QPixmap.fromImage(image).scaled(self.w, self.h))


    def z_up_cao(self):
        self.z_angle += int(self.lineEdit_range.text()) * 3.14 / 180
        self.show_image()

    def z_down_cao(self):
        self.z_angle -= int(self.lineEdit_range.text()) * 3.14 / 180
        self.show_image()

    def x_up_cao(self):
        self.x_angle += int(self.lineEdit_range.text()) * 3.14 / 180
        self.show_image()

    def x_down_cao(self):
        self.x_angle -= int(self.lineEdit_range.text()) * 3.14 / 180
        self.show_image()

    def dis_up_cao(self):
        self.dist += 0.01
        self.show_image()

    def dis_down_cao(self):
        self.dist -= 0.01
        self.show_image()

    def start_cao(self):
        self.show_image()




if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = Window()

    window.show()

    sys.exit(app.exec_())
