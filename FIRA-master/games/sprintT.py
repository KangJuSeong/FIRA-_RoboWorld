# -*- coding: utf-8 -*- # 한글 주석쓰려면 이거 해야함
import cv2  # opencv 사용
import time
import numpy as np

#img_yellow[0:height, int(width // 2 - 30):int(width // 2 + 30)]

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
        cap.set(cv2.CAP_PROP_BUFFERSIZE,1)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480) # 480
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 320) # 320
        # cap.set(5, 60)

        height, width = int(cap.get(4)), int(cap.get(3))
        # print(height," ",width)
        flag = 0
        straight = 0
        left = 1
        right = 2
        cnt = 0
        # self.robot.first_init()
        # # print("1")
        #
        # self.robot.walk_init()
        # # print("2")
        #
        # for _ in range(20):
        #     self.robot.walk_straight(flag)
        #
        # # print("3")
        self.robot.action(2)
        self.robot.action(3)
        self.robot.startThread()

        while True:
            # if self.robot.trip[0]:
            #     self.robot.stopThread()
            #     # 숫자에 따라 일어나는 동작 다르게 self.robot.trip[1]
            #     self.robot.startThread()


            for _ in range(1):
                ret, dst = cap.read()
            ret, dst = cap.read()
            #dst = dst[0:height, int(width // 2 - 80 - cnt*2):int(width // 2 + 80 + cnt*2)]

            if ret:
                # print("4")
                img_yellow = self.getBinImage(dst, "YELLOW")
                # cv2.imshow("yellow", img_yellow)
                status, obj_area, obj_x, obj_y = self.getObjectAreaAndPoint(img_yellow)
                # print(obj_area," ",obj_x," ",obj_y)

                if status:
                    center = int(width // 2 - obj_x)
                    if obj_area > 9600 and flag == 0:
                        flag = 1
                        self.robot.stopThread()
                        #time.sleep(0.3)
                        self.robot.action(7)
                        #time.sleep(1)
                        # self.robot.action(8)
                        time.sleep(1)
                        self.robot.action(8)
                        #time.sleep(0.3)
                        self.robot.startThread()
                        self.robot.setConfig(flag, straight)
                        pass

                    elif flag == 0:
                        if abs(center) < 20 + cnt:
                            print("직")
                            self.robot.setConfig(flag, straight)
                        elif center > 0:
                            print("왼")
                            self.robot.setConfig(flag, left)
                            cnt += 1
                        else:
                            print("오")
                            self.robot.setConfig(flag, right)
                            cnt += 1
                    else:
                        if abs(center) < 20 + cnt:
                            print("직")
                            self.robot.setConfig(flag, straight)
                        elif center < 0:
                            print("왼")
                            self.robot.setConfig(flag, left)
                            cnt -= 1
                        else:
                            print("오")
                            self.robot.setConfig(flag, right)
                            cnt -= 1


                else:
                    print("없직")
                    self.robot.setConfig(flag, straight)
            else:
                print("없직")
                self.robot.setConfig(flag, straight)

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
                "hsv": [15, 190, 190],
                "err": [35, 65, 65]
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
        carea = None
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 300:
                epsilon = 0.02 * cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, epsilon, True)
                cv2.drawContours(img, [approx], 0, (0, 255, 255), 5)
                x, y, w, h = cv2.boundingRect(cnt)
                M = cv2.moments(cnt)
                if M['m00'] != 0:
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                    carea = w * h
                    cv2.circle(img, (cx, cy), 3, (0, 0, 255), -1)
                    status = True
                else:
                    pass

        return status, carea, cx, cy


if __name__ == '__main__':
    test = Sprint()
    test.run()
