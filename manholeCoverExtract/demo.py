import os.path

import numpy as np
from PyQt5.Qt import *
from UI import *
import cv2
import sys
import threading
from detect_ellipse import *


class Window(QWidget, Ui_Form):

    def __init__(self):
        super(Window, self).__init__()
        self.setupUi(self)
        self.inpath_is_confirmed = False
        self.outpath_is_confrimed = False
        self.button_save_circle_image.setEnabled(False)

        self.in_image_list = None
        self.out_image_path = None
        self.image_num = 0
        self.in_image_p = 0
        self.rec_p = 0
        self.circle_p = 0
        self.current_image_height = None
        self.current_image_width = None
        self.current_image = None
        self.infile_path = None
        self.circle_list = []
        self.circle_image = None
        self.without_circle_list = []
        self.without_circle_image = None
        self.show_width = 0
        self.show_height = 0
        self.M_list = []
        self.M = None
        self.canny_image = None
        self.ellipse_parameter = None
        self.ellipse_in_ori_image = []
        self.angle_offset = 0
        self.a_offset = 0
        self.b_offset = 0
        self.x_offset = 0
        self.y_offset = 0
        self.margin = 0
        self.create_ellipse = None

        self.canny_low_thread = 300
        self.canny_high_thread = 350
        self.lineedit_up_range.setText('10')
        self.lineedit_down_range.setText('10')
        self.lineEdit_margin.setText('20')

        self.button_x_up.setShortcut('d')
        self.button_x_down.setShortcut('a')
        self.button_y_up.setShortcut('s')
        self.button_y_down.setShortcut('w')
        self.button_angle_up.setShortcut('7')
        self.button_angle_down.setShortcut('4')
        self.button_ellipse_a_up.setShortcut('8')
        self.button_ellipse_a_down.setShortcut('5')
        self.button_ellipse_b_up.setShortcut('9')
        self.button_ellipse_b_down.setShortcut('6')



    def select_inpath_cao(self):
        sub_window = QFileDialog(self, '选择文件夹')
        self.infile_path = sub_window.getExistingDirectory(self, '选择破损井盖图片文件夹', r'D:\yanjiu\image_after_photoshhop')
        self.line_edit_file_inpath.setText(self.infile_path)
        self.inpath_is_confirmed = True

        self.in_image_list = os.listdir(self.infile_path)
        image_path = os.path.join(self.infile_path, self.in_image_list[0])
        self.current_image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        self.current_image_width = self.current_image.shape[1]
        self.current_image_height = self.current_image.shape[0]
        if self.current_image_height > self.label_show_image.height() or self.current_image_width > self.label_show_image.width():
            rate_wid = self.current_image_width / self.label_show_image.width()
            rate_hei = self.current_image_height / self.label_show_image.height()
            if rate_hei > rate_wid:
                self.show_height = self.label_show_image.height()
                self.show_width = int(self.current_image_width / rate_hei)
            else:
                self.show_width = self.label_show_image.width()
                self.show_height = int(self.current_image_height / rate_wid)
        else:
            self.show_width = self.current_image_width
            self.show_height = self.current_image_height
        image = cv2.cvtColor(self.current_image, cv2.COLOR_BGRA2RGBA)
        image = QImage(image.data, image.shape[1], image.shape[0], image.shape[1] * 4,
                       QImage.Format_RGBA8888)
        self.label_show_image.setPixmap(QPixmap.fromImage(image).scaled(self.show_width,
                                                                        self.show_height))
        self.label_show_image.rec_the_image_outside(self.show_width, self.show_height)

        self.lineEdit_canny_threshold1.setText(str(self.canny_low_thread))
        self.lineEdit_canny_threshold2.setText(str(self.canny_high_thread))

    def select_outpath_cao(self):
        sub_window = QFileDialog(self, '选择文件夹')
        outfile_paht = sub_window.getExistingDirectory(self, '选择图像保存文件夹')
        self.line_edit_file_outpath.setText(outfile_paht)
        self.out_image_path = outfile_paht
        self.outpath_is_confrimed = True
        self.button_save_circle_image.setEnabled(True)

    def last_image_cao(self):
        if self.in_image_p <= 0:
            return
        self.in_image_p -= 1
        self.circle_p = 0
        self.create_ellipse = None
        self.label_show_image.rec_clean(self.in_image_p, 'last')
        # self.label_show_image.rec_list = self.label_show_image.image_rec[self.in_image_p]

        # 读取图片并显示
        image_path = os.path.join(self.infile_path, self.in_image_list[self.in_image_p])
        self.current_image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        self.current_image_width = self.current_image.shape[1]
        self.current_image_height = self.current_image.shape[0]
        if self.current_image_height > self.label_show_image.height() or self.current_image_width > self.label_show_image.width():
            rate_wid = self.current_image_width / self.label_show_image.width()
            rate_hei = self.current_image_height / self.label_show_image.height()
            if rate_hei > rate_wid:
                self.show_height = self.label_show_image.height()
                self.show_width = int(self.current_image_width / rate_hei)
            else:
                self.show_width = self.label_show_image.width()
                self.show_height = int(self.current_image_height / rate_wid)
        else:
            self.show_width = self.current_image_width
            self.show_height = self.current_image_height
        image = cv2.cvtColor(self.current_image, cv2.COLOR_BGRA2RGBA)
        image = QImage(image.data, image.shape[1], image.shape[0], image.shape[1] * 4,
                       QImage.Format_RGBA8888)
        self.label_show_image.setPixmap(QPixmap.fromImage(image).scaled(self.show_width,
                                                                        self.show_height))
        self.label_show_image.rec_the_image_outside(self.show_width, self.show_height)
        self.label_show_image.update()

    def next_image_cao(self):
        if self.in_image_p >= len(self.in_image_list):
            return
        self.in_image_p += 1
        self.circle_p = 0
        self.create_ellipse = None
        self.label_show_image.rec_clean(self.in_image_p, 'next')

        # 读取图像并显示
        image_path = os.path.join(self.infile_path, self.in_image_list[self.in_image_p])
        self.current_image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        self.current_image_width = self.current_image.shape[1]
        self.current_image_height = self.current_image.shape[0]
        if self.current_image_height > self.label_show_image.height() or self.current_image_width > self.label_show_image.width():
            rate_wid = self.current_image_width / self.label_show_image.width()
            rate_hei = self.current_image_height / self.label_show_image.height()
            if rate_hei > rate_wid:
                self.show_height = self.label_show_image.height()
                self.show_width = int(self.current_image_width / rate_hei)
            else:
                self.show_width = self.label_show_image.width()
                self.show_height = int(self.current_image_height / rate_wid)
        else:
            self.show_width = self.current_image_width
            self.show_height = self.current_image_height
        image = cv2.cvtColor(self.current_image, cv2.COLOR_BGRA2RGBA)
        image = QImage(image.data, image.shape[1], image.shape[0], image.shape[1] * 4,
                       QImage.Format_RGBA8888)
        self.label_show_image.setPixmap(QPixmap.fromImage(image).scaled(self.show_width,
                                                                        self.show_height))
        self.label_show_image.rec_the_image_outside(self.show_width, self.show_height)
        self.label_show_image.update()

    def rec_list_change_cao(self, rec_list, text):
        if text == '重置':
            self.rec_p = int(len(self.label_show_image.rec_list)) - 1
            return
        if len(self.label_show_image.rec_list) <= 0:
            return
        rec, rec_flag = rec_list[-1][0], rec_list[-1][1]
        real_x = rec[0] - 0.5 * self.label_show_image.width() + 0.5 * self.show_width
        real_y = rec[1] - 0.5 * self.label_show_image.height() + 0.5 * self.show_height
        rate = self.current_image_width / self.show_width
        x_in_current_image = int(real_x * rate)
        y_in_current_image = int(real_y * rate)
        xoffset_in_current_image = int(rec[2] * rate)
        yoffset_in_current_image = int(rec[3] * rate)
        image_cut = self.current_image[y_in_current_image: y_in_current_image + yoffset_in_current_image,
                    x_in_current_image: x_in_current_image + xoffset_in_current_image]

        if self.create_ellipse is not None:
            self.margin = int(self.lineEdit_margin.text())
            self.circle_list, self.without_circle_list, \
            self.M_list, self.canny_image, \
            self.ellipse_in_ori_image = ellipse2circle(image_cut,
                                                       self.current_image.copy(),
                                                       x_in_current_image,
                                                       y_in_current_image,
                                                       int(self.lineEdit_canny_threshold1.text()),
                                                       int(self.lineEdit_canny_threshold2.text()),
                                                       angle_offset=self.angle_offset,
                                                       a_offset=self.a_offset,
                                                       b_offset=self.b_offset,
                                                       x_offset=self.x_offset,
                                                       y_offset=self.y_offset,
                                                       output_margin=self.margin,
                                                       create_ellipse=self.create_ellipse)
        else:
            self.margin = int(self.lineEdit_margin.text())
            self.circle_list, self.without_circle_list, \
            self.M_list, self.canny_image, \
            self.ellipse_in_ori_image = ellipse2circle(image_cut,
                                                       self.current_image.copy(),
                                                       x_in_current_image,
                                                       y_in_current_image,
                                                       int(self.lineEdit_canny_threshold1.text()),
                                                       int(self.lineEdit_canny_threshold2.text()),
                                                       angle_offset=self.angle_offset,
                                                       a_offset=self.a_offset,
                                                       b_offset=self.b_offset,
                                                       x_offset=self.x_offset,
                                                       y_offset=self.y_offset,
                                                       output_margin=self.margin)
        # cv2.imshow('ori_list', self.ellipse_in_ori_image[0])
        # cv2.waitKey(1)

        self.canny_image = cv2.cvtColor(self.canny_image, cv2.COLOR_GRAY2RGB)
        self.canny_image = QImage(self.canny_image.data, self.canny_image.shape[1], self.canny_image.shape[0],
                                  self.canny_image.shape[1] * 3,
                                  QImage.Format_RGB888)
        self.label_show_canny_image.setPixmap(
            QPixmap.fromImage(self.canny_image).scaled(self.label_show_canny_image.width(),
                                                       self.label_show_canny_image.height()))
        self.label_show_canny_image.update()
        # print(self.circle_list)
        if len(self.circle_list) < 1:  # 判断当前rec图像是否能检测到椭圆
            return
        # 把椭圆画在原图上
        ellipse_in_ori_image = self.ellipse_in_ori_image[self.circle_p].copy()
        ellipse_in_ori_image = cv2.cvtColor(ellipse_in_ori_image, cv2.COLOR_BGRA2RGBA)
        ellipse_in_ori_image = QImage(ellipse_in_ori_image.data, ellipse_in_ori_image.shape[1],
                                      ellipse_in_ori_image.shape[0], ellipse_in_ori_image.shape[1] * 4,
                                      QImage.Format_RGBA8888)
        self.label_show_image.setPixmap(QPixmap.fromImage(ellipse_in_ori_image).scaled(self.show_width,
                                                                                       self.show_height))
        self.label_show_image.update()

        circle_image = self.circle_list[self.circle_p]
        self.without_circle_image = self.without_circle_list[self.circle_p]
        self.M = self.M_list[0]
        circle_image_width = circle_image.shape[1]
        circle_image_height = circle_image.shape[0]
        circle_image = cv2.cvtColor(circle_image, cv2.COLOR_BGRA2RGBA)
        circle_image = QImage(circle_image.data, circle_image.shape[1], circle_image.shape[0],
                              circle_image.shape[1] * 4,
                              QImage.Format_RGBA8888)
        self.label_show_circle_image.setPixmap(
            QPixmap.fromImage(circle_image).scaled(self.label_show_circle_image.width(),
                                                   self.label_show_circle_image.height()))
        self.label_show_circle_image.update()

    def next_circle_cao(self):
        if self.circle_p >= len(self.circle_list) - 1:
            return
        self.circle_p += 1
        self.circle_image = self.circle_list[self.circle_p]
        self.without_circle_image = self.without_circle_list[self.circle_p]
        self.M = self.M_list[self.circle_p]
        circle_image_width = self.circle_image.shape[1]
        circle_image_height = self.circle_image.shape[0]
        circle_image = cv2.cvtColor(self.circle_image, cv2.COLOR_BGRA2RGBA)
        circle_image = QImage(circle_image.data, circle_image.shape[1], circle_image.shape[0],
                              circle_image.shape[1] * 4, QImage.Format_RGBA8888)
        self.label_show_circle_image.setPixmap(
            QPixmap.fromImage(circle_image).scaled(self.label_show_circle_image.width(),
                                                   self.label_show_circle_image.height()))
        # self.label_show_circle_image.setPixmap(QPixmap.fromImage(circle_image))
        self.label_show_circle_image.update()

        ellipse_in_ori_image = self.ellipse_in_ori_image[self.circle_p].copy()
        ellipse_in_ori_image = cv2.cvtColor(ellipse_in_ori_image, cv2.COLOR_BGRA2RGBA)
        ellipse_in_ori_image = QImage(ellipse_in_ori_image.data, ellipse_in_ori_image.shape[1],
                                      ellipse_in_ori_image.shape[0], ellipse_in_ori_image.shape[1] * 4,
                                      QImage.Format_RGBA8888)
        self.label_show_image.setPixmap(QPixmap.fromImage(ellipse_in_ori_image).scaled(self.show_width,
                                                                                       self.show_height))
        self.label_show_image.update()

    def last_circle_cao(self):
        if self.circle_p <= 0:
            return
        self.circle_p -= 1
        self.circle_image = self.circle_list[self.circle_p]
        self.without_circle_image = self.without_circle_list[self.circle_p]
        self.M = self.M_list[self.circle_p]
        circle_image_width = self.circle_image.shape[1]
        circle_image_height = self.circle_image.shape[0]
        circle_image = cv2.cvtColor(self.circle_image, cv2.COLOR_BGRA2RGBA)
        circle_image = QImage(circle_image.data, circle_image.shape[1], circle_image.shape[0],
                              circle_image.shape[1] * 4,
                              QImage.Format_RGBA8888)
        self.label_show_circle_image.setPixmap(
            QPixmap.fromImage(circle_image).scaled(self.label_show_circle_image.width(),
                                                   self.label_show_circle_image.height()))
        # self.label_show_circle_image.setPixmap(QPixmap.fromImage(circle_image))
        self.label_show_circle_image.update()

        ellipse_in_ori_image = self.ellipse_in_ori_image[self.circle_p].copy()
        ellipse_in_ori_image = cv2.cvtColor(ellipse_in_ori_image, cv2.COLOR_BGRA2RGBA)
        ellipse_in_ori_image = QImage(ellipse_in_ori_image.data, ellipse_in_ori_image.shape[1],
                                      ellipse_in_ori_image.shape[0], ellipse_in_ori_image.shape[1] * 4,
                                      QImage.Format_RGBA8888)
        self.label_show_image.setPixmap(QPixmap.fromImage(ellipse_in_ori_image).scaled(self.show_width,
                                                                                       self.show_height))
        self.label_show_image.update()

    def save_circle_cao(self):
        cls = self.lineEdit_class.text()
        final_circle_image = self.without_circle_image.copy()
        final_circle_image = cv2.cvtColor(final_circle_image, cv2.COLOR_BGR2BGRA)
        r = final_circle_image.shape[0] / 2.
        print(final_circle_image.shape)
        for i in range(final_circle_image.shape[0]):
            for j in range(final_circle_image.shape[1]):
                if ((i - r) ** 2 + (j - r) ** 2) ** 0.5 > (r - self.margin):
                    final_circle_image[i, j, 3] = 0
        cv2.imwrite(os.path.join(self.out_image_path, f'{cls}_{self.in_image_p}_{self.circle_p}.png'),
                    final_circle_image)
        np.savetxt('M.txt', self.M)
        print(f'已保存{cls}_{self.in_image_p}_{self.circle_p}.png')

    def change_canny_thread_cao(self):
        if self.label_show_image.rec:
            self.rec_list_change_cao(self.label_show_image.rec_list, '更改阈值')

    def pop_rec(self):
        self.label_show_image.rec_pop()
        self.rec_p = int(len(self.label_show_image.rec_list)) - 1
        self.circle_p = 0

    def button_canny_up(self):
        self.circle_p = 0
        new_threshold1 = 50 + int(self.lineEdit_canny_threshold1.text())
        new_threshold2 = 50 + int(self.lineEdit_canny_threshold2.text())
        self.lineEdit_canny_threshold1.setText(str(new_threshold1))
        self.lineEdit_canny_threshold2.setText(str(new_threshold2))
        if self.label_show_image.rec:
            self.rec_list_change_cao(self.label_show_image.rec_list, '更改阈值')

    def button_canny_down(self):
        if int(self.lineEdit_canny_threshold1.text()) < 50:
            return
        self.circle_p = 0
        new_threshold1 = int(self.lineEdit_canny_threshold1.text()) - 50
        new_threshold2 = int(self.lineEdit_canny_threshold2.text()) - 50
        self.lineEdit_canny_threshold1.setText(str(new_threshold1))
        self.lineEdit_canny_threshold2.setText(str(new_threshold2))
        if self.label_show_image.rec:
            self.rec_list_change_cao(self.label_show_image.rec_list, '更改阈值')

    def fit_ellipse(self):
        pass
        # points = self.label_show_image.point_list.reshape(-1, 1, 2)
        # self.margin = int(self.lineEdit_margin.text())
        # self.circle_list, self.without_circle_list, self.M_list = ellipse2circle(self.current_image, points=points)
        # if len(self.circle_list) < 1:  # 判断当前rec图像是否能检测到椭圆
        #     print('无法拟合')
        #     return
        #
        # circle_image = self.circle_list[0]
        # self.without_circle_image = self.without_circle_list[0]
        # self.circle_p = 0
        # circle_image_width = circle_image.shape[1]
        # circle_image_height = circle_image.shape[0]
        # circle_image = cv2.cvtColor(circle_image, cv2.COLOR_BGR2RGB)
        # circle_image = QImage(circle_image.data, circle_image.shape[1], circle_image.shape[0],
        #                       circle_image.shape[1] * 3,
        #                       QImage.Format_RGB888)
        # self.label_show_circle_image.setPixmap(
        #     QPixmap.fromImage(circle_image).scaled(self.label_show_circle_image.width(),
        #                                            self.label_show_circle_image.height()))
        # self.label_show_circle_image.update()

    def angle_up(self):
        range = self.lineedit_up_range.text()
        self.angle_offset += int(range)
        if self.label_show_image.rec:
            self.rec_list_change_cao(self.label_show_image.rec_list, '更改阈值')

    def angle_down(self):
        range = self.lineedit_down_range.text()
        self.angle_offset -= int(range)
        if self.label_show_image.rec:
            self.rec_list_change_cao(self.label_show_image.rec_list, '更改阈值')

    def ellipse_a_up(self):
        range = self.lineedit_up_range.text()
        self.a_offset += int(range)
        if self.label_show_image.rec:
            self.rec_list_change_cao(self.label_show_image.rec_list, '更改阈值')

    def ellipse_a_down(self):
        range = self.lineedit_down_range.text()
        self.a_offset -= int(range)
        if self.label_show_image.rec:
            self.rec_list_change_cao(self.label_show_image.rec_list, '更改阈值')

    def ellipse_b_up(self):
        range = self.lineedit_up_range.text()
        self.b_offset += int(range)
        if self.label_show_image.rec:
            self.rec_list_change_cao(self.label_show_image.rec_list, '更改阈值')

    def ellipse_b_down(self):
        range = self.lineedit_down_range.text()
        self.b_offset -= int(range)
        if self.label_show_image.rec:
            self.rec_list_change_cao(self.label_show_image.rec_list, '更改阈值')

    def x_up(self):
        range = self.lineedit_up_range.text()
        self.x_offset += int(range)
        if self.label_show_image.rec:
            self.rec_list_change_cao(self.label_show_image.rec_list, '更改阈值')

    def x_down(self):
        range = self.lineedit_down_range.text()
        self.x_offset -= int(range)
        if self.label_show_image.rec:
            self.rec_list_change_cao(self.label_show_image.rec_list, '更改阈值')

    def y_up(self):
        range = self.lineedit_up_range.text()
        self.y_offset += int(range)
        if self.label_show_image.rec:
            self.rec_list_change_cao(self.label_show_image.rec_list, '更改阈值')

    def y_down(self):
        range = self.lineedit_down_range.text()
        self.y_offset -= int(range)
        if self.label_show_image.rec:
            self.rec_list_change_cao(self.label_show_image.rec_list, '更改阈值')

    def refresh_cao(self):
        if self.label_show_image.rec:
            self.rec_list_change_cao(self.label_show_image.rec_list, '更改阈值')

    def create_ellipse_cao(self):
        if len(self.label_show_image.rec_list) <= 0:
            return
        rec, rec_flag = self.label_show_image.rec_list[-1][0], self.label_show_image.rec_list[-1][1]
        real_x = rec[0] - 0.5 * self.label_show_image.width() + 0.5 * self.show_width
        real_y = rec[1] - 0.5 * self.label_show_image.height() + 0.5 * self.show_height
        rate = self.current_image_width / self.show_width
        x_in_current_image = int(real_x * rate)
        y_in_current_image = int(real_y * rate)
        xoffset_in_current_image = int(rec[2] * rate)
        yoffset_in_current_image = int(rec[3] * rate)
        image_cut = self.current_image[y_in_current_image: y_in_current_image + yoffset_in_current_image,
                    x_in_current_image: x_in_current_image + xoffset_in_current_image]

        # 手动生成椭圆
        self.create_ellipse = ((int(xoffset_in_current_image / 2), int(yoffset_in_current_image / 2)),
                               (int(xoffset_in_current_image / 2), int(yoffset_in_current_image / 2)), 0)

        self.margin = int(self.lineEdit_margin.text())
        self.circle_list, self.without_circle_list, \
        self.M_list, self.canny_image, \
        self.ellipse_in_ori_image = ellipse2circle(image_cut,
                                                   self.current_image.copy(),
                                                   x_in_current_image,
                                                   y_in_current_image,
                                                   int(self.lineEdit_canny_threshold1.text()),
                                                   int(self.lineEdit_canny_threshold2.text()),
                                                   angle_offset=self.angle_offset,
                                                   a_offset=self.a_offset,
                                                   b_offset=self.b_offset,
                                                   x_offset=self.x_offset,
                                                   y_offset=self.y_offset,
                                                   output_margin=self.margin,
                                                   create_ellipse=self.create_ellipse)
        # cv2.imshow('ori_list', self.ellipse_in_ori_image[0])
        # cv2.waitKey(1)

        self.canny_image = cv2.cvtColor(self.canny_image, cv2.COLOR_GRAY2RGB)
        self.canny_image = QImage(self.canny_image.data, self.canny_image.shape[1], self.canny_image.shape[0],
                                  self.canny_image.shape[1] * 3,
                                  QImage.Format_RGB888)
        self.label_show_canny_image.setPixmap(
            QPixmap.fromImage(self.canny_image).scaled(self.label_show_canny_image.width(),
                                                       self.label_show_canny_image.height()))
        self.label_show_canny_image.update()
        # print(self.circle_list)
        if len(self.circle_list) < 1:  # 判断当前rec图像是否能检测到椭圆
            return
        # 把椭圆画在原图上
        ellipse_in_ori_image = self.ellipse_in_ori_image[self.circle_p].copy()
        ellipse_in_ori_image = cv2.cvtColor(ellipse_in_ori_image, cv2.COLOR_BGRA2RGBA)
        ellipse_in_ori_image = QImage(ellipse_in_ori_image.data, ellipse_in_ori_image.shape[1],
                                      ellipse_in_ori_image.shape[0], ellipse_in_ori_image.shape[1] * 4,
                                      QImage.Format_RGBA8888)
        self.label_show_image.setPixmap(QPixmap.fromImage(ellipse_in_ori_image).scaled(self.show_width,
                                                                                       self.show_height))
        self.label_show_image.update()

        circle_image = self.circle_list[self.circle_p]
        self.without_circle_image = self.without_circle_list[self.circle_p]
        self.M = self.M_list[0]
        circle_image_width = circle_image.shape[1]
        circle_image_height = circle_image.shape[0]
        circle_image = cv2.cvtColor(circle_image, cv2.COLOR_BGRA2RGBA)
        circle_image = QImage(circle_image.data, circle_image.shape[1], circle_image.shape[0],
                              circle_image.shape[1] * 4,
                              QImage.Format_RGBA8888)
        self.label_show_circle_image.setPixmap(
            QPixmap.fromImage(circle_image).scaled(self.label_show_circle_image.width(),
                                                   self.label_show_circle_image.height()))
        self.label_show_circle_image.update()

    def jump_cao(self):
        index = self.lineEdit_jump.text()
        self.in_image_p = int(index) - 1
        self.next_image_cao()



if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = Window()

    window.show()

    sys.exit(app.exec_())
