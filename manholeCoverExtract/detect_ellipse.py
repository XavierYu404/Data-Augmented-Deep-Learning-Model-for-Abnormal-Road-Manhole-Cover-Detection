import cv2
import numpy as np
import math
import copy

margin = 20


def ellipse2circle(image=None,
                   current_image=None,
                   x_in_current_image=None,
                   y_in_current_image=None,
                   threshold1=None,
                   threshold2=None,
                   points=None,
                   angle_offset=0,
                   a_offset=0,
                   b_offset=0,
                   x_offset=0,
                   y_offset=0,
                   output_margin=20,
                   create_ellipse=None):

    ellipse_list = []
    circle_list = []
    without_circle_list = []
    M_list = []
    ellipse_in_ori_image = []
    canny_image_list = []

    if points is not None:
        pass
        # ellipse = cv2.fitEllipse(points)
        # if ellipse[1][0] > image.shape[1] / 2 and ellipse[1][1] > image.shape[1] / 2 and ellipse[2] > 0:
        #     ellipse_list.append(ellipse)
        # for i, ellipse in enumerate(ellipse_list):
        #
        #     # 4 画椭圆
        #     image_ellipse = image.copy()
        #     image_without_ellipse = image.copy()
        #     cv2.ellipse(image_ellipse, ellipse, color=(0, 0, 255), thickness=2)
        #     # print(ellipse)
        #     # cv2.imshow('ellipse', image_ellipse)
        #
        #     # 5 旋转图像
        #     ellipse_center, ellipse_angle = ellipse[0], ellipse[2]
        #     M = cv2.getRotationMatrix2D(ellipse_center, ellipse_angle - 90, 1)
        #     image_without_ellipse = cv2.warpAffine(image_without_ellipse, M, (image.shape[1], image.shape[0]))
        #     image_ellipse = cv2.warpAffine(image_ellipse, M, (image.shape[1], image.shape[0]))
        #     # cv2.imshow('rotate image', image_ellipse)
        #
        #     # 6 透视变换
        #
        #     # 6.1 确认椭圆长短轴
        #     if ellipse[1][0] < ellipse[1][1]:
        #         ellipse_b = ellipse[1][0] / 2
        #         ellipse_a = ellipse[1][1] / 2
        #         ellipse_center_x = ellipse[0][0]
        #         ellipse_center_y = ellipse[0][1]
        #     else:
        #         ellipse_a = ellipse[1][0] / 2
        #         ellipse_b = ellipse[1][1] / 2
        #         ellipse_center_x = ellipse[0][0]
        #         ellipse_center_y = ellipse[0][1]
        #     if ellipse_a > 1000 or ellipse_b > 1000:
        #         continue
        #
        #     top_left = np.array([ellipse_center_x - ellipse_a, ellipse_center_y - ellipse_b])
        #     top_right = np.array([ellipse_center_x + ellipse_a, ellipse_center_y - ellipse_b])
        #     bottom_left = np.array([ellipse_center_x - ellipse_a, ellipse_center_y + ellipse_b])
        #     bottom_right = np.array([ellipse_center_x + ellipse_a, ellipse_center_y + ellipse_b])
        #     # print(type(top_left), type(ellipse_center_x))
        #
        #     # 6.2 原图顶点和在目标图像中的位置
        #     src = np.array([top_left, top_right, bottom_left, bottom_right], dtype='float32')
        #     # print(src)
        #     margin = 20
        #     dst = np.array(
        #         [[0. + margin, 0. + margin], [2 * ellipse_a - margin, 0. + margin],
        #          [0. + margin, 2 * ellipse_a - margin],
        #          [2 * ellipse_a - margin, 2 * ellipse_a - margin]], dtype='float32')
        #     print(src, dst)
        #
        #     # 6.3 变换
        #     M = cv2.getPerspectiveTransform(src, dst)
        #
        #     image_without_ellipse = cv2.warpPerspective(image_without_ellipse, M,
        #                                                 (int(2 * ellipse_a), int(2 * ellipse_a)))
        #     image_ellipse = cv2.warpPerspective(image_ellipse, M, (int(2 * ellipse_a), int(2 * ellipse_a)))
        #     circle_list.append(image_ellipse)
        #     without_circle_list.append(image_without_ellipse)
        #     M_list.append(M)
        #
        #     del image_ellipse, image_without_ellipse
        # return circle_list, without_circle_list, M_list
    # ----------------------------------------------暂时关闭右键自选点功能--------------------------------------------------

    if threshold1 is None:
        threshold1 = 300
    if threshold2 is None:
        threshold2 = 350

    # 判断是自动拟合椭圆还是手动创建椭圆
    if create_ellipse is None:
        image = copy.deepcopy(image)
        # 1 边缘检测
        image2 = cv2.Canny(image, threshold1=threshold1, threshold2=threshold2)
        # 2 找点
        cnts, _ = cv2.findContours(image2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)

        for i, cnt in enumerate(cnts):
            if len(cnt) < 5:
                continue

            # 3 找椭圆
            ellipse = cv2.fitEllipse(cnt)
            if ellipse[1][0] > image.shape[1] / 2 and ellipse[1][1] > image.shape[1] / 2 and ellipse[2] > 0:
                ellipse_list.append(ellipse)
    else:
        image = copy.deepcopy(image)
        # 1 边缘检测
        image2 = cv2.Canny(image, threshold1=threshold1, threshold2=threshold2)
        ellipse_list.append(create_ellipse)

    for i, ellipse in enumerate(copy.deepcopy(ellipse_list)):
        # 4 画椭圆
        # current
        ellipse_center_xy_l = list(ellipse[0])
        ellipse_ab_l = list(ellipse[1])
        ellipse_angle_l = ellipse[2]

        # new
        ellipse_center_x = ellipse_center_xy_l[0] + x_offset
        ellipse_center_y = ellipse_center_xy_l[1] + y_offset
        ellipse_aa = ellipse_ab_l[0] + a_offset
        ellipse_bb = ellipse_ab_l[1] + b_offset
        ellipse_angle = angle_offset + ellipse_angle_l
        ellipse = ((ellipse_center_x, ellipse_center_y), (ellipse_aa, ellipse_bb), ellipse_angle)

        ellipse_ori_center_xy = (ellipse_center_x + x_in_current_image,
                                 ellipse_center_y + y_in_current_image)
        ellipse_ori_ab = (ellipse_aa, ellipse_bb)
        ellipse_ori_angle = ellipse_angle
        ellipse_ori = (ellipse_ori_center_xy, ellipse_ori_ab, ellipse_ori_angle)
        print('ellipse', ellipse)
        print('ellipse_ori', ellipse_ori)
        print(f'x_in_current_image={x_in_current_image}, y_in_current_image={y_in_current_image}')
        print(f'x_offset={x_offset}, y_offset={y_offset}')

        image_ellipse = copy.deepcopy(image)
        image_without_ellipse = image
        ori_image = current_image.copy()
        thickness_image = int(max(max(image_ellipse.shape[0], image_ellipse.shape[1]) * 0.003, 2))
        cv2.ellipse(image_ellipse, ellipse, color=(0, 0, 255, 255), thickness=thickness_image)
        thickness = int(max(max(ori_image.shape[0], ori_image.shape[1]) * 0.003, 2))
        cv2.ellipse(ori_image, ellipse_ori, color=(0, 0, 255, 255), thickness=thickness)

        # 4.2 -> old 6.1 确认椭圆长短轴
        if ellipse[1][0] < ellipse[1][1]:
            ellipse_b = ellipse[1][0] / 2
            ellipse_a = ellipse[1][1] / 2
            ellipse_center_x = ellipse[0][0]
            ellipse_center_y = ellipse[0][1]
        else:
            ellipse_a = ellipse[1][0] / 2
            ellipse_b = ellipse[1][1] / 2
            ellipse_center_x = ellipse[0][0]
            ellipse_center_y = ellipse[0][1]
        if ellipse_a > 3000 or ellipse_b > 3000:
            continue
        ellipse_in_ori_image.append(ori_image)
        # 5 旋转图像
        if ellipse_center_x < ellipse_a:
            dx = ellipse_a - ellipse_center_x
            if dx < 0:
                dx = abs(dx) + ellipse_a
            image_ellipse = cv2.copyMakeBorder(image_ellipse, 0, 0, int(dx + 10), 0, cv2.BORDER_CONSTANT, value=[0, 0, 0, 255])
            image_without_ellipse = cv2.copyMakeBorder(image_without_ellipse, 0, 0, int(dx + 10), 0, cv2.BORDER_CONSTANT,
                                               value=[0, 0, 0])
            ellipse_center_x += int(dx + 10)
            ellipse = ((ellipse_center_x, ellipse_center_y), (ellipse_aa, ellipse_bb), ellipse_angle)



        if image.shape[1] - ellipse_center_x < ellipse_a:
            dx = image.shape[1] - ellipse_center_x
            if dx < 0:
                dx = abs(dx) + ellipse_a
            image_ellipse = cv2.copyMakeBorder(image_ellipse, 0, 0, 0, int(dx + 10), cv2.BORDER_CONSTANT, value=[0, 0, 0, 255])
            image_without_ellipse = cv2.copyMakeBorder(image_without_ellipse, 0, 0, 0, int(dx + 10), cv2.BORDER_CONSTANT,
                                               value=[0, 0, 0])
        if ellipse_center_y < ellipse_b:
            dy = ellipse_b - ellipse_center_y
            if dy < 0:
                dy = abs(dy) + ellipse_b
            image_ellipse = cv2.copyMakeBorder(image_ellipse, int(dy + 10), 0, 0, 0, cv2.BORDER_CONSTANT, value=[0, 0, 0, 255])
            image_without_ellipse = cv2.copyMakeBorder(image_without_ellipse, int(dy + 10), 0, 0, 0, cv2.BORDER_CONSTANT,
                                               value=[0, 0, 0])
            ellipse_center_y += int(dy + 10)
            ellipse = ((ellipse_center_x, ellipse_center_y), (ellipse_aa, ellipse_bb), ellipse_angle)
        if image.shape[0] - ellipse_center_y < ellipse_b:
            dy = image.shape[0] - ellipse_center_y
            if dy < 0:
                dy = abs(dy) + ellipse_b
            image_ellipse = cv2.copyMakeBorder(image_ellipse, 0, int(dy + 10), 0, 0, cv2.BORDER_CONSTANT, value=[0, 0, 0, 255])
            image_without_ellipse = cv2.copyMakeBorder(image_without_ellipse, 0, int(dy + 10), 0, 0, cv2.BORDER_CONSTANT,
                                               value=[0, 0, 0])

        ellipse_center, ellipse_angle = ellipse[0], ellipse[2]
        M = cv2.getRotationMatrix2D(ellipse_center, ellipse_angle - 90, 1)
        new_weidth = image.shape[1] * abs(np.cos(ellipse_angle - 90)) + image.shape[0] * abs(np.sin(ellipse_angle - 90))
        new_height = image.shape[1] * abs(np.sin(ellipse_angle - 90)) + image.shape[0] * abs(np.cos(ellipse_angle - 90))

        image_without_ellipse = cv2.warpAffine(image_without_ellipse, M, (image_ellipse.shape[1], image_ellipse.shape[0]))
        image_ellipse = cv2.warpAffine(image_ellipse, M, (image_ellipse.shape[1], image_ellipse.shape[0]))


        # shape[0] 高   shape[1] 宽  平移矩阵 [[1,0,x],[0,1,y]]
        move2new_center_x = int(abs(new_height - image.shape[1]) / 2)
        move2new_center_y = int(abs(new_weidth - image.shape[0]) / 2)


        # 6 透视变换

        top_left = np.array(
            [ellipse_center_x - ellipse_a, ellipse_center_y - ellipse_b])
        top_right = np.array(
            [ellipse_center_x + ellipse_a, ellipse_center_y - ellipse_b])
        bottom_left = np.array(
            [ellipse_center_x - ellipse_a, ellipse_center_y + ellipse_b])
        bottom_right = np.array(
            [ellipse_center_x + ellipse_a, ellipse_center_y + ellipse_b])
        # print(type(top_left), type(ellipse_center_x))

        # 6.2 原图顶点和在目标图像中的位置
        src = np.array([top_left, top_right, bottom_left, bottom_right], dtype='float32')
        # print(src)
        margin = output_margin
        dst = np.array(
            [[0. + margin, 0. + margin], [2 * ellipse_a - margin, 0. + margin], [0. + margin, 2 * ellipse_a - margin],
             [2 * ellipse_a - margin, 2 * ellipse_a - margin]], dtype='float32')
        # print(src, dst)

        # 6.3 变换
        M = cv2.getPerspectiveTransform(src, dst)

        image_without_ellipse = cv2.warpPerspective(image_without_ellipse, M, (int(2 * ellipse_a), int(2 * ellipse_a)))
        image_ellipse = cv2.warpPerspective(image_ellipse, M, (int(2 * ellipse_a), int(2 * ellipse_a)))
        # cv2.imshow('circle', image_ellipse)
        circle_list.append(image_ellipse)
        without_circle_list.append(image_without_ellipse)
        M_list.append(M)

        del image_ellipse, image_without_ellipse, ori_image

    return circle_list, without_circle_list, M_list, image2, ellipse_in_ori_image
