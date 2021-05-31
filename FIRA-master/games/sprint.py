
# -*- coding: utf-8 -*- # 한글 주석쓰려면 이거 해야함
import cv2  # opencv 사용
import numpy as np
import time


class Sprint:
    def __init__(self, robot):
        self.robot = robot
        pass

    def clear_image(self, cap):
        for _ in range(4):
            cap.read()
        return cap.read()

    def run(self):
        cap = cv2.VideoCapture(0)
        # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)
        # cap.set(5, 90)

        height, width = int(cap.get(4)), int(cap.get(3))
        flag = 0
        finish = 0
        # straight = 0
        # left = 1
        # right = 2

        self.robot.first_init()

        self.robot.walk_init()

        for _ in range(20):
            self.robot.walk_straight(flag)

        for _ in range(5):
            temp = cap.read()
        # self.robot.startThread()

        while True:
            # if self.robot.trip[0]:
            #     self.robot.stopThread()
            #     # 숫자에 따라 일어나는 동작 다르게 self.robot.trip[1]
            #     self.robot.startThread()

            # for _ in range(2):
            #     ret, dst = cap.read()
            #     # cv2.imshow("s", dst)

            image_list = []
            for _ in range(2):
                # temp = cap.read()
                # cv2.imshow("s", temp[1])
                image_list.append(cap.read())

            if image_list[0][0]:
                cr = []
                for _, dst in image_list:
                    cr.append(self.getBinImage(dst, "YELLOW"))
                    # cv2.imshow("s", dst)
                    pass

                cv2.bitwise_or(cr[0], cr[1], cr[0])

                img_yellow = cr[0]
                cv2.imshow("yellow", img_yellow)

                # start = time.time()

                status = True
                areas = [  # left, center, right
                    cv2.countNonZero(img_yellow[0:height, 0:int(width // 2 - 30)]),
                    cv2.countNonZero(img_yellow[0:height, int(width // 2 - 30):int(width // 2 + 30)]),
                    cv2.countNonZero(img_yellow[0:height, int(width // 2 + 30):width]),
                ]

                areas[0] = int(100 * areas[0] / (height * int(width // 2 - 30)))
                areas[1] = int(100 * areas[1] / (height * 60))
                areas[2] = int(100 * areas[2] / (height * (height - int(width // 2 + 30))))

                if areas[1] > 8:
                    obj_x = 0
                else:
                    obj_x = -50 if areas[0] < areas[2] else 50

                # print("\t".join(list(map(lambda x: str(x), areas))))

                # status, obj_area, obj_x, obj_y = self.getObjectAreaAndPoint(img_yellow)
                # print("time :", time.time() - start)

                if status:
                    center = obj_x
                    if abs(center) < 30:
                        # print("C", center)
                        for _ in range(5):
                            self.robot.walk_straight(flag)
                    elif center > 0:
                        # print("L", center)
                        for _ in range(5):
                            self.robot.walk_left(flag)
                    elif center < 0:
                        # print("R", center)
                        for _ in range(5):
                            self.robot.walk_right(flag)
                    else:
                        for _ in range(5):
                            self.robot.walk_straight(flag)

                    area_avg = int(100 * sum(areas) / (height * width))
                    if finish != 2 and area_avg > 50:
                        finish += 1
                        flag = 1 if finish == 2 else 0
                        if finish == 2:
                            self.robot.walk_finish()

                else:
                    # print("C", "\tE")
                    for _ in range(5):
                        self.robot.walk_straight(flag)
            else:
                # print("NO")
                for _ in range(5):
                    self.robot.walk_straight(flag)

            cv2.waitKey(1)
        pass

    def sprint_1_walk_front(self):
        return 0

    def sprint_2_detect_object(self):
        return 0

    def sprint_3_walk_back(self):
        return 0

    def trace_line(self):
        pass

    def getBinImage(self, frame, color):
        if color is None:
            return frame

        HSV = {
            "YELLOW": {
                "hsv": [22, 183, 163],
                "err": [20, 40, 70]
            }
        }

        p = HSV[color]
        h_value, s_value, v_value = p["hsv"]

        img_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        hsv__lower = (h_value - p["err"][0], s_value -
                      p["err"][1], v_value - p["err"][2])
        hsv__upper = (h_value + p["err"][0], s_value +
                      p["err"][1], v_value + p["err"][2])

        mask = cv2.inRange(img_hsv, hsv__lower, hsv__upper)
        # kernel = np.ones((5, 5), np.uint8)
        # mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.erode(mask, None, iterations=3)
        mask = cv2.dilate(mask, None, iterations=5)
        return mask

    def getObjectAreaAndPoint(self, img):
        _, contours, hierarchy = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        status = False
        area = None
        cx = None
        cy = None
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 1000:
                epsilon = 0.02 * cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, epsilon, True)
                cv2.drawContours(img, [approx], 0, (0, 255, 255), 5)
                M = cv2.moments(cnt)
                if M['m00'] != 0:
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])

                    cv2.circle(img, (cx, cy), 3, (0, 0, 255), -1)
                    status = True
                else:
                    pass

        # cv2.imshow("debug", img)

        return status, area, cx, cy


if __name__ == '__main__':
    test = Sprint()
    test.run()
