import cv2
import numpy as np
import time
from library.image_processor import ImageProcessor
#from library.motion import Motion

"""
#----알고리즘----#
# 2초 sleep
# 활 시위 당기기
# 활을 쏘면 맞는 좌표값과 과녁의 중점값의 차이 절댓값이 #이하이면
# 활 쏘기


#----동작----#
# 활 시위 당기기
# 활 쏘기
"""

class Archery:
    def __init__(self,robot, ip):
        #imageProcessor
        self.robot = robot
        self.ip = ip
        #local
        self.mission_finished = 0
        self.case = 0
        #const
        self.targetX = 162  # 화살 쏘면 꽂히는 예상 x죄표
        self.targetY = 110  # 화살 쏘면 꽂히는 예상 y죄표
        self.grap = 20      # 예상 좌표 - 현재과녁 중심 좌표
        self.roi_len_half = 11 # roi 길이 반
        pass

    def run(self):
        while not self.mission_finished:
            if self.case == 0:
                # 3초 sleep
                self.robot.action(61)
                # print("3초기다리기")
                # time.sleep(3)
                self.case += 1
            elif self.case == 1:
                #활 시위 당기기
                #self.case += self.archery_1_1_pull()
                self.case += 1
            elif self.case == 2:
                # 활을 쏘면 맞는 좌표값과 과녁의 중점값의 차이 절댓값이 #이하이면 return 1
                frame = self.ip.getFrame()
                cv2.imshow("ready_raw", frame)
                #contour 사용해서 좌표간의 거리 차이로 하는것
                #self.case += self.archery_2_1_check_ready_to_shoot(frame)
                #roi 영역 지정해서 색 비율로 하는것
                self.case += self.archery_2_1_check_ready_to_shoot_roi(frame)
            elif self.case == 3:
                # 활 쏘기
                time.sleep(0.5)
                self.case += self.archery_3_1_shoot()
                time.sleep(1)
                self.robot.action(61)
                self.mission_finished = 1
            cv2.waitKey(1)

    def archery_1_1_pull(self):
        print("archery_1_1_pull: 활 시위 당기기")
        #return self.robot.a_pull()
        return 1

    def archery_2_1_check_ready_to_shoot(self, frame):
        # 디버깅용 target 좌표
        cv2.line(frame, (self.targetX, self.targetY), (self.targetX, self.targetY), (0, 0, 255), 7)

        red_yellow_cir, cX, cY = self.contours(frame)

        # 디버깅용 과녁 중심 좌표
        cv2.line(frame, (cX, cY), (cX, cY), (0, 255, 0), 7)
        cv2.imshow("archery_2_1_check_ready_to_shoot", frame)

        if abs(self.targetX - cX) < self.grap and abs(self.targetY - cY) < self.grap:
            print("활쏘기")
            return 1
        else:
            print("쏘면 안됌")
            return 0

    def contours(self, frame):
        img_red = self.ip.getBinImage(frame, "RED")
        img_yellow = self.ip.getBinImage(frame, "YELLOW")
        red_yellow_bin = cv2.bitwise_or(img_red, img_yellow)
        cv2.imshow("bin", red_yellow_bin)

        _, contours, hierarchy = cv2.findContours(red_yellow_bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cx = 0
        cy = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 5000:
                epsilon = 0.02 * cv2.arcLength(cnt, True)
                (x, y), radius = cv2.minEnclosingCircle(cnt)
                center = (int(x), int(y))
                radius = int(radius)
                cv2.circle(frame, center, radius, (255, 0, 0), 5)
                M = cv2.moments(cnt)
                if M['m00'] != 0:

                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])

                    cv2.circle(frame, (cx, cy), 3, (0, 0, 255), -1)
                else:
                    pass
        return frame, cx, cy

    def archery_2_1_check_ready_to_shoot_roi(self, frame):
        # 디버깅용 target 좌표, roi 영역
        cv2.line(frame, (self.targetX, self.targetY), (self.targetX, self.targetY), (0, 0, 255), 7)
        cv2.rectangle(frame, (self.targetX - self.roi_len_half, self.targetY - self.roi_len_half), (self.targetX + self.roi_len_half, self.targetY + self.roi_len_half),(0, 0, 255), 1)

        roi = frame[self.targetY - self.roi_len_half:self.targetY + self.roi_len_half, self.targetX - self.roi_len_half:self.targetX + self.roi_len_half]
        img_red = self.ip.getBinImage(roi, "RED")
        img_yellow = self.ip.getBinImage(roi, "YELLOW")
        red_yellow_bin = cv2.bitwise_or(img_red, img_yellow)

        # 디버깅용 bin 화면
        cv2.imshow("bin", red_yellow_bin)
        cv2.imshow("archery_2_1_check_ready_to_shoot_roi", frame)
        if self.ip.check_color_ratio_bin(red_yellow_bin, 80):
            print("활쏘기")
            return 1
        else:
            print("쏘면 안됌")
            return 0

    def archery_3_1_shoot(self):
        print("쏜다!!!!")
        return self.robot.a_shoot()
        #return 1


if __name__ == '__main__':
    #robot = Motion()
    ip = ImageProcessor()
    a = Archery(ip)
    a.run()


