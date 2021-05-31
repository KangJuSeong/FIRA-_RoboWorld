import cv2
import numpy as np
import time
import datetime
from library.motion import Motion
from library.image_processor import ImageProcessor
from library.motion import Motion

"""
#----알고리즘----#
# 노랑 or 파랑 장애물이 나올 때 까지 걷기 /멈추기
# 빨강색 있음? # 고개 들어야하나..?
    # 오른쪽 왼쪽 선 탐색 후 어디로 이동할 지 정함
    # 많이 이동
#빨강색 없음
    # 오른쪽 왼쪽 선 탐색 후 어디로 이동할 지 정함
    # 장애물 시야에서 없어질 때 까지 이동

* 빨강 기어가는 곳이 필수적이 아닌 경우

* 빨강 기어가는 곳이 필수적인 경우

#----동작----#
# 앞으로 걷기
# move 오른쪽
# move 왼쪽
# 고개 - 오블리큐, 업, 왼, 오 
"""

class ObstacleRun:
    def __init__(self, robot, ip):
        # imageProcessor
        self.robot = robot
        self.ip = ip
        #local
        self.mission_finished = 0
        self.case = 0
        self.red_finished = 0  # 빨강 장애물은 하나기 때문에

        self.yellow_blue_ratio = 10
        self.red_ratio = 30

        self.now = datetime.datetime.now().strftime("day:%d h:%H m:%M s:%S")

        # roi1
        self.roi1_x_start = int(self.ip.width//10)
        self.roi1_x_end = self.ip.width - int(self.ip.width//10)
        self.roi1_y_start_front = int(self.ip.height//2)
        self.roi1_y_start_thread = int(self.ip.height*0.65)
        self.roi1_y_end = self.ip.height
        # roi2
        self.roi2_x_start = 0
        self.roi2_x_end = self.ip.width
        self.roi2_y_start = 0
        self.roi2_y_end = int(self.ip.height // 4)
        # 옆걸음 때 왼쪽 roi 삼각형 좌표: 중간 밑, 오른쪽 밑, 오른쪽 높이*0.3
        #self.vertices_L = np.array([[self.ip.width//2, self.ip.height], [self.ip.width, self.ip.height],
        #                 [self.ip.width, int(self.ip.height*0.3)]], np.int32)
        self.roiL_x_start = 0
        self.roiL_x_end = int(self.ip.width//6)
        self.roiL_y_start = int(self.ip.height // 4)
        self.roiL_y_end = self.ip.height
        # 옆걸음 때 오른쪽 roi 삼각형 좌표: 중간 밑, 왼쪽 밑, 왼쪽 높이*0.3
        #self.vertices_R = np.array([[self.ip.width//2, self.ip.height], [0, self.ip.height],
        #                 [0, int(self.ip.height*0.3)]], np.int32)
        self.roiR_x_start = self.ip.width - int(self.ip.width//6)
        self.roiR_x_end = self.ip.width
        self.roiR_y_start = int(self.ip.height // 4)
        self.roiR_y_end = self.ip.height

    def run(self):
        while not self.mission_finished:
            # 노랑 or 파랑 / 빨강 장애물이 나올 때 까지 걷기; 멈추기
            if self.case == 0:
                self.set_head("oblique")
                time.sleep(1)
                is_obstacle = self.check_obstacle_front()
                if is_obstacle:
                    # 장애물로 넘어감
                    self.case = 1
                else:
                    self.set_head("up")
                    time.sleep(1)
                    self.case += self.walk_until_obstacle() # return = 1 or 3
                    print("walk_until_obstacle값: ", self.case)
            elif self.case == 1:
                # 노랑 or 파랑일 경우 - 위 case 문으로
                # 양 옆 선 체크 - 방향정하기 (default = left)
                # 시야의 움직이는 방향 반대편으로 3/1이하가 되도록 걷기
                self.set_head("down")
                time.sleep(1)
                frame = self.ip.getFrame()
                direction = self.choose_direction(frame) # return = 2 or 3
                self.move(direction)
                self.set_head("down")
                time.sleep(1)
                frame = self.ip.getFrame()
                self.case += self.escape_and_check_obstacle(frame)
            elif self.case == 2:
                # case 0으로 돌아가기
                self.case = 0
            elif self.case == 3:
                # 빨강일 경우
                # 센터맞추기
                frame = self.ip.getFrame()
                self.case += self.ready_crawl(frame)
            elif self.case == 4:
                # 기어가는 동작, 일어서기
                self.case += self.crawl()
                self.red_finished = 1 # 빨강장애물은 하나밖에 없으므로
            elif self.case == 5:
                # case 0 으로 돌아가기
                self.case = 0

    def check_obstacle_front(self):
        print("check_obstacle_front 함수 호출")
        yellow_blue_obstacle_flag = 0
        frame = self.ip.getFrame()

        success = 0
        for i in range(5):
            frame = self.ip.getFrame()
            # roi_1: 로봇이 직진할 떄 장애물에 부딪히지 않고 갈 수 있는 시야영역
            roi_1 = frame[self.roi1_y_start_front:self.roi1_y_end, self.roi1_x_start:self.roi1_x_end]
            yellow_blue_bin = self.get_yellow_blue_bin(roi_1)

            # roi_1 영역에 노랑, 파랑 장애물 유무 판단
            if self.ip.check_color_ratio_bin(yellow_blue_bin, self.yellow_blue_ratio):
                success += 1
            if success > 3:
                yellow_blue_obstacle_flag = 1
                cv2.imwrite(str(self.now) + "yell_blue_obstacle.png", frame)
                break

        # 디버깅 용 출력 화면
        cv2.rectangle(frame, (self.roi1_x_start, self.roi1_y_start_front), (self.roi1_x_end, self.roi1_y_end), (0, 0, 255), 3)
        cv2.imshow("front", frame)
        #cv2.imshow("front roi yellow blue bin", yellow_blue_bin)
        cv2.waitKey(1)

        if yellow_blue_obstacle_flag:
            print("check_obstacle_front: 앞에 노랑, 파랑색 장애물 있음")
            return True
        else:
            print("check_obstacle_front: 없음")
            return False

    def walk_until_obstacle(self):
        print("walk_until_obstacle 호출")
        yellow_blue_obstacle_flag = 0
        red_obstacle_flag = 0

        self.robot.ob_startThread()
        while True:
            frame = self.ip.getFrame()
            print("쓰레드 도는중")

            success1 = 0
            success2 = 0
            for i in range(5):
                frame = self.ip.getFrame()
                # roi_1: 로봇이 직진할 떄 장애물에 부딪히지 않고 갈 수 있는 시야영역
                # 고개 up이기 때문에 oblique 때 보다 roi 세로 높이 낮춤
                roi_1 = frame[self.roi1_y_start_thread:self.roi1_y_end, self.roi1_x_start:self.roi1_x_end]
                # roi_2: 빨강 탐색 영역
                roi_2 = frame[self.roi2_y_start:self.roi2_y_end, self.roi2_x_start:self.roi2_x_end]
                yellow_blue_bin = self.get_yellow_blue_bin(roi_1)

                # roi_1 영역에 노랑, 파랑 장애물 유무 판단
                if self.ip.check_color_ratio_bin(yellow_blue_bin, self.yellow_blue_ratio):
                    success1 += 1
                # roi_2 영역에 빨강 장애물 유무 판단
                if self.ip.check_color_ratio(roi_2, "RED", self.red_ratio):
                    success2 += 1
                if success1 > 3:
                    self.robot.ob_stopThread()
                    yellow_blue_obstacle_flag = 1
                    print("쓰레드에서 노랑, 파랑 장애물 발견")
                    cv2.imwrite(str(self.now) + "t_yell_blue_obstacle.png", frame)

                if success2 > 3:
                    self.robot.ob_stopThread()
                    red_obstacle_flag = 1
                    print("쓰레드에서 빨강 장애물 발견")
                    cv2.imwrite(str(self.now) + "t_red_obstacle.png", frame)
                    break

            # 디버깅 용 출력 화면
            cv2.rectangle(frame, (self.roi1_x_start, self.roi1_y_start_thread), (self.roi1_x_end, self.roi1_y_end),
                          (0, 0, 255), 3)
            cv2.rectangle(frame, (self.roi2_x_start, self.roi2_y_start), (self.roi2_x_end, self.roi2_y_end),
                          (0, 255, 0), 3)
            cv2.imshow("thread walk", frame)
            yellow_blue_bin = self.get_yellow_blue_bin(frame)
            cv2.imshow("thread yellow blue bin", yellow_blue_bin)
            #cv2.imshow("thread walk: roi yellow blue bin", yellow_blue_bin)



            cv2.waitKey(1)

            if red_obstacle_flag and not self.red_finished:
                print("walk_until_obstacle: 빨강색 장애물 때문")
                return 3
            elif yellow_blue_obstacle_flag:
                print("walk_until_obstacle: 파랑색 장애물 때문")
                # TODO: 앞으로 몇걸음 가기 (고개를 up 한상태로 본거라 장애물이 좀 멀리 있을것이기 때문)
                #self.robot.ob_walk()
                return 1
            else:
                print("walk_until_obstacle: 걷는중")
                pass

    def choose_direction(self, frame):
        y_start = int((self.ip.height * 0.75) // 3)

        self.set_head("left")    # 왼쪽 방향 보기
        time.sleep(1)
        left_img = self.ip.getFrame()
        left_img = left_img[int(self.roiL_y_start * 0.5):self.roiL_y_end, self.roiL_x_start:self.roiL_x_end]
        left_ratio = self.ip.check_how_much_color_ratio(left_img, "YELLOW")

        print("왼쪽캡쳐")
        cv2.imwrite(str(self.now) +"left.png", left_img)

        self.set_head("right")    # 오른쪽 방향 보기
        time.sleep(1)
        right_img = self.ip.getFrame()
        right_img = right_img[int(self.roiR_y_start * 0.5):self.roiR_y_end, self.roiR_x_start:self.roiR_x_end]
        right_ratio = self.ip.check_how_much_color_ratio(right_img, "YELLOW")

        print("오른쪽캡쳐")
        cv2.imwrite(str(self.now) +"right.png", right_img)

        self.set_head("down")

        # left: 2, right: 3
        if left_ratio > 10 and right_ratio < 5:
            # 노랑이 왼쪽 o, 오른쪽 x
            print("choose_direction: 노랑이 왼쪽 o, 오른쪽 x")
            return 3
        elif left_ratio < 5 and right_ratio > 10:
            # 노랑이 왼쪽 x, 오른쪽 o
            print("choose_direction: 노랑이 왼쪽 x, 오른쪽 o")
            return 2
        elif left_ratio < 5 and right_ratio < 5:
            print("choose_direction: roi 3등분 해서 장애물 없는 쪽으로")
            roi_1_L = frame[self.roi1_y_start_thread:self.roi1_y_end, self.roi1_x_start:self.roi1_x_start+int((self.roi1_x_end-self.roi1_x_start)*0.3)]
            roi_1_R = frame[self.roi1_y_start_thread:self.roi1_y_end, self.roi1_x_start+int((self.roi1_x_end-self.roi1_x_start)*0.6):self.roi1_x_end]
            roi_1_L = self.get_yellow_blue_bin(roi_1_L)
            roi_1_R = self.get_yellow_blue_bin(roi_1_R)
            if self.ip.check_how_much_color_ratio_bin(roi_1_L) < self.ip.check_how_much_color_ratio_bin(roi_1_R):
                return 2
            else:
                return 3
        elif left_ratio > right_ratio:
            # 노랑이 왼쪽이 많음
            print("choose_direction: 노랑이 왼쪽이 많음")
            return 3
        elif left_ratio < right_ratio:
            # 노랑이 오른쪽이 많음
            print("choose_direction: 노랑이 오른쪽이 많음")
            return 2

    def get_yellow_blue_bin(self, frame):
        yellow_bin = self.ip.getBinImage(frame, "YELLOW")
        blue_bin = self.ip.getBinImage(frame, "BLUE")
        return cv2.bitwise_or(yellow_bin, blue_bin)

    def region_of_interest(self, frame, vertices, color3=(255, 255, 255), color1=255):  # ROI 셋팅

        mask = np.zeros_like(frame)  # mask = img와 같은 크기의 빈 이미지

        if len(frame.shape) > 2:  # Color 이미지(3채널)라면 :
            color = color3
        else:  # 흑백 이미지(1채널)라면 :
            color = color1

        # vertices에 정한 점들로 이뤄진 다각형부분(ROI 설정부분)을 color로 채움
        cv2.fillPoly(mask, vertices, color)

        # 이미지와 color로 채워진 ROI를 합침
        ROI_image = cv2.bitwise_and(frame, mask)
        return ROI_image

    def set_head(self, direction):
        # oblique: 0, up: 1, left: 2, right: 3
        if direction == "oblique":
            return self.robot.ob_head(0)
            #return 1
        elif direction == "up":
            return self.robot.ob_head(1)
            #return 1
        elif direction == "left":
            return self.robot.ob_head(2)
            #return 1
        elif direction == "right":
            return self.robot.ob_head(3)
            #return 1
        elif direction == "down":
            print("고개 down")
            return self.robot.ob_head(4)
            #return 1

    def move(self, direction):
        self.set_head("oblique")
        time.sleep(0.5)
        self.robot.ob_move(direction)
        time.sleep(0.5)
        self.robot.ob_move(direction)
        time.sleep(0.5)
        self.robot.ob_move(direction)
        time.sleep(0.5)
        if direction == 2:
            self.robot.action(80)  # left turn
            self.robot.action(80)
        elif direction == 3:
            self.robot.action(81)  # right turn

    def escape_and_check_obstacle(self, frame):
        print("escape_and_check_obstacle 호출")
        # 휴대폰 자판 5, 8번 이미지 - 로봇이 직진할 떄 장애물에 부딪히지 않고 갈 수 있는 시야영역
        #roi_1 = frame[self.roi1_x_start:self.roi1_y_end, self.roi1_x_start:self.roi1_x_end]

        #cv2.rectangle(frame, (self.roi1_x_start, self.roi1_y_start), (self.roi1_x_end, self.roi1_y_end), (0, 0, 255), 3)
        cv2.imshow("escape_and_check_obstacle", frame)
        cv2.waitKey(1)

        yellow_blue_bin = self.get_yellow_blue_bin(frame)
        if self.ip.check_how_much_color_ratio_bin(yellow_blue_bin) < 5:
            # 30cm 더 가야함
            print("escape_and_check_obstacle: 앞으로 가도됨")
            cv2.imwrite(str(self.now) +"escape_go.png", frame)
            return 1
        else:
            print("escape_and_check_obstacle: 옆으로 더가야함")
            cv2.imwrite(str(self.now) + "escape_avoid.png", frame)
            return 0

    def ready_crawl(self, frame):
        # 화면을 세로로 나눠서 왼, 오 중 빨간색이 더 많은 쪽으로 옆걸음
        x_block = int(self.ip.width // 3)
        x_start = 0

        left_img = frame[0:self.ip.height//2, 0:x_block]
        right_img = frame[0:self.ip.height//2, x_block*2:self.ip.width]

        left_ratio = self.ip.check_how_much_color_ratio(left_img, "RED")
        right_ratio = self.ip.check_how_much_color_ratio(right_img, "RED")

        #디버깅용 화면
        cv2.rectangle(frame, (0, 0), (x_block, self.ip.height//2), (0, 0, 255), 3)
        cv2.rectangle(frame, (x_block*2, 0), (self.ip.width, self.ip.height//2), (0, 0, 255), 3)
        cv2.imshow("ready_crawl", frame)

        cv2.waitKey(1)

        if abs(left_ratio - right_ratio) < 10:
            print("ready_crawl: 빨강 센터: 맞음")
            return 1
        elif left_ratio < right_ratio:
            # TODO: 센터맞추기 위한 오른쪽으로 옆걸음 동작
            print("ready_crawl: 빨강센터: 오른쪽으로")
            self.robot.ob_move(3)
            return 0
        elif left_ratio > right_ratio:
            # TODO: 센터맞추기 위한 왼쪽으로 옆걸음 동작
            print("ready_crawl: 빨강센터: 왼쪽으로")
            self.robot.ob_move(2)
            return 0

    def crawl(self):
        # 30cm 가야댐
        return self.robot.ob_crawl()
        #return 1


#cam = cv2.VideoCapture(0)

if __name__ == '__main__':
    robot = Motion()
    ip = ImageProcessor()
    ob = ObstacleRun(robot, ip)
    mission_finished = 0
    while not mission_finished:
        #img = ip.getFrame()
        #yellow_blue_bin = ob.get_yellow_blue_bin(img)

        #red_bin = ip.getBinImage(img, "RED")

        #ob.walk_until_obstacle()
        #ob.choose_direction(img)
        #ob.escape_and_check_obstacle(2)
        #ob.ready_crawl(img)
        ob.check_obstacle_front()
        #roi = ob.region_of_interest(img, [ob.vertices_L])
        #cv2.imshow("red bin", red_bin)

        if cv2.waitKey(25) >= 0:
            break

    ip.clear()
    cv2.destroyAllWindows()