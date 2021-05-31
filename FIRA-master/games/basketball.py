# -*- coding: utf-8 -*- # 한글 주석쓰려면 이거 해야함
import cv2  # opencv 사용
import numpy as np
import time


class BasketBall:
    def __init__(self, robot):
        self.robot = robot
        pass

    def run(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)
        # cap.set(5, 60)
        height, width = int(cap.get(4)), int(cap.get(3))
        # print(height, " ", width)
        case = 0
        check = 0
        left_c = 0

        start_time = time.time()
        self.robot.bb_checkright(case)
        # print(time.time() - start_time)

        ret, dst = False, None
        while True:
            if time.time() - start_time > 110:
                self.robot.action(56)
                for _ in range(2):
                    self.robot.action(55)
                self.robot.bb_ball(case)
                break

            if case == 0:
                self.robot.bb_checkright(case)
            time.sleep(1.2)
            for _ in range(5):
                ret, dst = cap.read()
                # # cv2.imshow("show", dst)
            if ret:
                if case == 0:
                    img_ball = self.getBinImage(dst, "BALL")
                    status, obj_area, obj_x, obj_y = self.getObjectAreaAndPoint(img_ball)
                    # # cv2.imshow("test", img_ball)
                    # print(obj_area, " ", obj_x, " ", obj_y)
                    if status:
                        center = width // 2 - obj_x
                        if obj_area > 9900 and abs(center) < 60:
                            # 공잡기
                            # print("공잡기")
                            # for _ in range(3):
                            #     self.robot.bb_leftstep(case)
                            #     time.sleep(0.05)
                            self.robot.bb_ball(case)

                            case += 1
                            pass
                        elif abs(center) < 50:
                            if obj_area > 9900:
                                # 공잡기
                                # print("공잡기")
                                # for _ in range(3):
                                #     self.robot.bb_leftstep(case)
                                #     time.sleep(0.05)
                                self.robot.bb_ball(case)

                                case += 1
                                pass
                            else:
                                # if obj_y-height//2 < 0:
                                #     self.robot.bb_ball(case)
                                #     case += 1
                                #     continue
                                # 한발자국
                                # print("한발자국")
                                self.robot.bb_init(case)
                                self.robot.bb_shortwalk(case)
                                pass
                        elif center > 0:
                            # 왼쪽 게발
                            # print("왼쪽 게발")
                            self.robot.bb_init(case)
                            self.robot.bb_leftstep(case)
                            time.sleep(1)
                            pass
                        else:  # center > 0
                            # 오른쪽 게발
                            # print("오른쪽 게발")
                            self.robot.bb_init(case)
                            self.robot.bb_rightstep(case)
                            time.sleep(1)
                            pass
                    else:
                        self.robot.action(52)  # 오른쪽 위
                        time.sleep(0.5)
                        for _ in range(5):
                            ret, dst = cap.read()
                            # # cv2.imshow("show", dst)
                        img_ball = self.getBinImage(dst, "BALL")
                        status, obj_area, obj_x, obj_y = self.getObjectAreaAndPoint(img_ball)
                        # # cv2.imshow("test", img_ball)
                        if status:
                            self.robot.bb_init(case)
                            for _ in range(3):
                                self.robot.bb_shortwalk(case)
                                # time.sleep(0.5)
                            self.robot.bb_checkright(case)
                            continue

                        self.robot.bb_checkdown()
                        time.sleep(0.5)
                        for _ in range(5):
                            ret, dst = cap.read()
                            # # cv2.imshow("show", dst)
                        img_ball = self.getBinImage(dst, "BALL")
                        status, obj_area, obj_x, obj_y = self.getObjectAreaAndPoint(img_ball)
                        # # cv2.imshow("test", img_ball)
                        if status:
                            self.robot.bb_init(case)
                            for _ in range(2):
                                self.robot.action(57)
                            self.robot.bb_checkright(case)
                            continue

                        # self.robot.action(50)  # 중간 위
                        # time.sleep(0.5)
                        # for _ in range(5):
                        #     ret, dst = cap.read()
                        #     # # cv2.imshow("show", dst)
                        # img_ball = self.getBinImage(dst, "BALL")
                        # status, obj_area, obj_x, obj_y = self.getObjectAreaAndPoint(img_ball)
                        # # # cv2.imshow("test", img_ball)
                        # if status:
                        #     self.robot.bb_shortwalk(case)
                        #     self.robot.bb_shortwalk(case)
                        #     for _ in range(3):
                        #         self.robot.bb_leftstep(case)
                        #         time.sleep(0.5)
                        #     continue

                        self.robot.bb_checkleft(case)
                        time.sleep(0.5)
                        for _ in range(5):
                            ret, dst = cap.read()
                            # # cv2.imshow("show", dst)
                        img_ball = self.getBinImage(dst, "BALL")
                        status, obj_area, obj_x, obj_y = self.getObjectAreaAndPoint(img_ball)
                        # # cv2.imshow("test", img_ball)
                        if status:
                            for _ in range(4):
                                self.robot.action(57)
                            time.sleep(0.5)
                            self.robot.bb_checkright(case)
                            left_c = 1
                            continue

                        self.robot.action(51)  # 왼쪽 위
                        time.sleep(0.5)
                        for _ in range(5):
                            ret, dst = cap.read()
                            # # cv2.imshow("show", dst)
                        img_ball = self.getBinImage(dst, "BALL")
                        status, obj_area, obj_x, obj_y = self.getObjectAreaAndPoint(img_ball)
                        # # cv2.imshow("test", img_ball)
                        if status:
                            for _ in range(4):
                                self.robot.action(57)
                            time.sleep(0.5)
                            self.robot.bb_init(case)
                            self.robot.bb_shortwalk(case)
                            self.robot.bb_checkright(case)
                            left_c = 1
                            continue

                        # self.robot.bb_checkright(case)
                        # for _ in range(5):
                        #     ret, dst = cap.read()
                        # img_ball = self.getBinImage(dst, "BALL")
                        # status, obj_area, obj_x, obj_y = self.getObjectAreaAndPoint(img_ball)
                        # if status:
                        #     for _ in range(2):
                        #         self.robot.bb_rightstep(case)
                        #
                        #     self.robot.bb_init(case)
                        #     continue
                        # print("공없네")
                        pass

                if case == 1:
                    time.sleep(0.3)
                    # if left_c == 1:
                    #     time.sleep(0.5)
                    #     for _ in range(5):
                    #         self.robot.action(58)
                    #         time.sleep(0.5)
                    #     left_c = 0
                    # cap.set(cv2.CAP_PROP_AUTO_EXPOSURE,0)
                    img_goalpost1 = self.getBinImage(dst, "GOALPOST")
                    img_goalpost2 = self.getBinImage(dst, "GOALPOST_NEAR")
                    img_goalpost = cv2.bitwise_or(img_goalpost1, img_goalpost2)
                    # # cv2.imshow("test", img_goalpost)
                    status, obj_area, obj_x, obj_y = self.getObjectAreaAndPoint(img_goalpost)
                    print(obj_area, " ", obj_x, " ", obj_y)

                    if status:
                        center = width // 2 - obj_x
                        if obj_area > 50000 and abs(center) < 65:
                            # 골넣기
                            # print("골넣기")
                            # for _ in range(1):
                            #     self.robot.bb_leftstep(case)
                            #     time.sleep(0.05)
                            self.robot.action(56)  # 고개 돌리기
                            for _ in range(5):
                                self.robot.action(55)  # 고개 돌리고 앞으로
                            self.robot.bb_ball(case)
                            break
                            pass
                        elif abs(center) < 60:
                            if check == 0 or check == 1:
                                time.sleep(0.5)
                                self.robot.bb_walkstart(case)
                                for _ in range(9 + left_c + check):
                                    # self.robot.bb_walk(case)
                                    self.robot.action(53)
                                    self.robot.action(54)
                                self.robot.bb_walkfinish(case)
                                time.sleep(1)
                                check += 1
                                continue

                            if obj_area > 50000:
                                # 골넣기
                                # print("골넣기")
                                # for _ in range(1):
                                #     self.robot.bb_leftstep(case)
                                #    time.sleep(0.05)
                                self.robot.action(56)
                                for _ in range(5):
                                    self.robot.action(55)
                                self.robot.bb_ball(case)
                                break
                                pass


                            else:  # obj_area > 10000:
                                # 한발자국
                                # print("한발자국")
                                self.robot.bb_init(case)
                                self.robot.bb_shortwalk(case)
                                pass

                            # elif obj_area > 5000:
                            #     # 한발자국
                            #     print("두발자국")
                            #     self.robot.bb_walkstart(case)
                            #     for _ in range(1):
                            #         # self.robot.bb_walk(case)
                            #         self.robot.action(53)
                            #         self.robot.action(54)
                            #     self.robot.bb_walkfinish(case)
                            #     time.sleep(1)
                            #     pass
                            # elif obj_area > 2000:
                            #     # 세발자국
                            #     print("두발자국")
                            #     self.robot.bb_walkstart(case)
                            #     for _ in range(1):
                            #         # self.robot.bb_walk(case)
                            #         self.robot.action(53)
                            #         self.robot.action(54)
                            #     self.robot.bb_walkfinish(case)
                            #     time.sleep(1)
                            #     pass
                            # else:  # obj_area < 2000:
                            #     # 네발자국
                            #     print("발자국")
                            #     self.robot.bb_walkstart(case)
                            #     for _ in range(1):
                            #         # self.robot.bb_walk(case)
                            #         self.robot.action(53)
                            #         self.robot.action(54)
                            #     self.robot.bb_walkfinish(case)
                            #     time.sleep(1)
                            #     pass


                        elif center > 0:
                            # 왼쪽 게발
                            # print("왼쪽")
                            self.robot.bb_leftturn(case)
                            # time.sleep(0.5)
                            self.robot.bb_leftturn(case)
                            pass
                        else:  # center > 0
                            # print("오른")
                            # 오른쪽 게발
                            self.robot.bb_rightturn(case)
                            # time.sleep(0.5)
                            self.robot.bb_rightturn(case)
                            pass
                    else:

                        self.robot.bb_checkleft(case)
                        time.sleep(0.5)
                        for _ in range(5):
                            ret, dst = cap.read()

                        img_goalpost1 = self.getBinImage(dst, "GOALPOST")
                        img_goalpost2 = self.getBinImage(dst, "GOALPOST_NEAR")
                        img_goalpost = cv2.bitwise_or(img_goalpost1, img_goalpost2)
                        # # cv2.imshow("test", img_goalpost)
                        status, obj_area, obj_x, obj_y = self.getObjectAreaAndPoint(img_goalpost)
                        print(obj_area)
                        if status:
                            for _ in range(3):
                                self.robot.bb_leftturn(case)
                                # time.sleep(0.5)
                            self.robot.bb_init(case)
                            # if check == 0 or check == 1:
                            #     time.sleep(0.5)
                            #     self.robot.bb_walkstart(case)
                            #     for _ in range(6):
                            #         # self.robot.bb_walk(case)
                            #         self.robot.action(53)
                            #         self.robot.action(54)
                            #     self.robot.bb_walkfinish(case)
                            #     time.sleep(1)
                            #     check += 1
                            continue

                        self.robot.bb_checkright(case)
                        time.sleep(0.5)
                        for _ in range(5):
                            ret, dst = cap.read()
                        img_goalpost1 = self.getBinImage(dst, "GOALPOST")
                        img_goalpost2 = self.getBinImage(dst, "GOALPOST_NEAR")
                        img_goalpost = cv2.bitwise_or(img_goalpost1, img_goalpost2)
                        # cv2.imshow("test", img_goalpost)
                        status, obj_area, obj_x, obj_y = self.getObjectAreaAndPoint(img_goalpost)
                        print(obj_area)
                        if status:
                            for _ in range(3):
                                self.robot.bb_rightturn(case)
                                # time.sleep(0.5)
                            self.robot.bb_init(case)
                            # if check == 0 or check == 1:
                            #     time.sleep(0.5)
                            #     self.robot.bb_walkstart(case)
                            #     for _ in range(6):
                            #         # self.robot.bb_walk(case)
                            #         self.robot.action(53)
                            #         self.robot.action(54)
                            #     self.robot.bb_walkfinish(case)
                            #     time.sleep(1)
                            #     check += 1
                            continue
                        pass

                        self.robot.bb_init(case)
                        time.sleep(0.5)
                        for _ in range(5):
                            ret, dst = cap.read()
                        img_goalpost1 = self.getBinImage(dst, "GOALPOST")
                        img_goalpost2 = self.getBinImage(dst, "GOALPOST_NEAR")
                        img_goalpost = cv2.bitwise_or(img_goalpost1, img_goalpost2)
                        # cv2.imshow("test", img_goalpost)
                        status, obj_area, obj_x, obj_y = self.getObjectAreaAndPoint(img_goalpost)
                        print(obj_area)
                        if status:
                            # self.robot.bb_shortwalk(case)
                            self.robot.bb_init(case)
                            if check == 0 or check == 1:
                                time.sleep(0.5)
                                self.robot.bb_walkstart(case)
                                for _ in range(9+left_c+check):
                                    # self.robot.bb_walk(case)
                                    self.robot.action(53)
                                    self.robot.action(54)
                                self.robot.bb_walkfinish(case)
                                time.sleep(1)
                                check += 1
                            continue
                        pass

                    pass
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
            },
            "BALL": {
                "hsv": [15, 190, 190],
                "err": [35, 65, 65]
            },
            "GOALPOST": {
                "hsv": [177, 171, 171],
                "err": [25, 100, 100]
                # "hsv": [172, 175, 175],
                # "err": [35, 70, 70]
                # "hsv": [175, 190, 190],
                # "err": [35, 65, 65]
            },
            "GOALPOST_NEAR": {
                "hsv": [207, 176, 171],
                "err": [40, 80, 80]
                # "hsv": [175, 190, 190],
                # "err": [35, 70, 70]
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
        status = 0
        area = None
        cx = None
        cy = None
        carea = None
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 190:
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
                    status = 1
                else:
                    pass

        return status, carea, cx, cy


if __name__ == '__main__':
    test = BasketBall()
    test.run()
