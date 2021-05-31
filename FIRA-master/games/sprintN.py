# -*- coding: utf-8 -*- # 한글 주석쓰려면 이거 해야함
import cv2  # opencv 사용
import numpy as np
import time


class Sprint:
    def __init__(self, robot):
        self.robot = robot
        pass

    def run(self):

        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)
        # cap.set(5, 90)

        height, width = int(cap.get(4)), int(cap.get(3))
        flag = 0
        # straight = 0
        # left = 1
        # right = 2

        # for _ in range(5):
        #     temp = cap.read()
        # self.robot.startThread()
        #self.robot.action(2)
        self.robot.action(3)

        while True:
            ret, dst = cap.read()
            cv2.imshow("real", dst)
            if ret:
                img_object = self.getBinImage(dst, "BALL")
                cv2.imshow("test", img_object)
                status, obj_area, obj_x, obj_y = self.getObjectAreaAndPoint(img_object)
                print(obj_area, " ", obj_x, " ", obj_y)
                cnt = 0
                # center = int(width//2 - obj_x)
                if status:
                    center = int(width // 2 - obj_x)
                    if obj_area > 50000 and flag == 0:
                        flag = 1
                        self.robot.action(7)
                        self.robot.action(8)
                    pass

                    if flag == 0:
                        if abs(center) < 40 + cnt:
                            print("직")
                            self.robot.action(5)
                            self.robot.action(6)
                        elif center > 0:
                            print("왼")
                            self.robot.action(11)
                            self.robot.action(12)
                            cnt += 1
                        else:
                            print("오")
                            self.robot.action(13)
                            self.robot.action(14)
                            cnt += 1
                    else:
                        self.robot.action(9)
                        self.robot.action(10)

                else:

                    if flag == 0:
                        self.robot.action(5)
                        self.robot.action(6)
                    else:
                        self.robot.action(9)
                        self.robot.action(10)
            cv2.waitKey(1)
        pass

    def getBinImage(self, frame, color):
        if color is None:
            return frame

        HSV = {
            "YELLOW": {
                "hsv": [22, 183, 163],
                "err": [20, 40, 70]
            },
            "BALL": {
                "hsv": [15, 190, 190],
                "err": [35, 65, 65]
            },
            "GOALPOST": {
                "hsv": [177, 171, 171],
                "err": [25, 100, 100]
            },
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
        status = 0
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
                    status = 1
                else:
                    pass

        return status, area, cx, cy


if __name__ == '__main__':
    test = Sprint()
    test.run()
