import cv2
import numpy as np
import time
import datetime
from library.motion import Motion
from library.image_processor import ImageProcessor
from library.motion import Motion

"""
#----알고리즘----#
# 노랑 or 파랑, 빨강 장애물이 나올 때 까지 걷기 /멈추기: thread walk
# 노랑 or 파랑 장애물
    # 5걸음 앞으로
    # 밑에 보고 영상 저장, 왼쪽, 오른쪽 체크해서 방향 정함
        # 왼쪽, 오른쪽 둘다 선 없으면 밑에보고 저장한 영상으로 더 효율적인 방향 정하기
    # escape roi 영상에 장애물 없으면 theadwalk로 다시 가기
#빨강색 장애물
    # 빨강색을 센터로 
    # 앞에 보고 양옆에 파랑색 안보이는지
    # 기어감
    # theadwalk로 다시 가기

#----동작----#
# 앞으로 걷기
# move 오른쪽
# move 왼쪽
# 고개 - 오블리큐, 업, 왼, 오 
"""


# =========================================#
# 1. obs_0_1_check_obstacle_front()
#    - oblique로 앞에 노랑, 파랑 장애물이 있는지 체크 (up할 때 안보이는 시야 체크)
#
# 2. obs_0_2_walk_until_obstacle()
#    - 노랑 or 파랑, 빨강 장애물이 나올 때 까지 걷기 /멈추기
#      | yellow_blue_ratio: 노랑 or 파랑 장애물 thershold
#      | red_ratio: 빨강 장애물 thershold
#    - 빨강 발견: 6걸음 걷기
#    - 노랑 or 파랑 발견: 2걸음 걷기
#
# 3. obs_1_1_choose_direction()
#     - 장애물을 어느 방향으로 피할지 결정
#      | roiL: 노랑 선 판별 왼쪽 영역
#      | roiR: 노랑 선 판별 오른쪽 영역
#      - "down" 영상갱신
#      | 1) 노랑선 없는 쪽으로
#      | 2) 둘다 노랑선 없으면 "down"해서 영상 찍은걸로 오, 왼 중 색 비율 낮은 roi 방향으로
#      | 3) 둘다 있으면 비율 낮은 쪽으로
#
# 4. obs_1_3_escape_and_check_obstacle()
#     - "down" 영상갱신
#      | roi_E: 로봇이 직진할 때 장애물에 부딪히지 않고 갈 수 있는 영역
#     - roi_E에 장애물 없다면 장애물 완전히 피하기
#      | 피한 방향의 반대 방향 보고 영상갱신
#      | side_blue_ratio: 파랑 색
#      | 바로 옆 위치 시야에 장애물 걸리면 장애물 피해서 옆걸음 더 함
#     - 빨강이 가까이 있는지 체크함
#
# 5. obs_3_1_check_red_center_blue_side()
#     - 빨강 센터 맞추기
#      | 양 1/3 범위 비교해서 빨강 비율차이 체크
#      |  비율 차이 40 퍼센트 이하이면 빨강 가까이 있는지 체크하며서 앞으로감
#     - 양쪽 파랑색 장애물 체크
#      | roi_L: 왼쪽 파랑 장애물 체크 영역
#      | roi_R: 오른쪽 파랑 장애물 체크 영역
# 6. obs_4_1_crawl()
#     - 구르기
# =========================================#

class ObstacleRun:
    def __init__(self, robot, ip):
        # imageProcessor
        self.robot = robot
        self.ip = ip
        # local
        self.mission_finished = 0
        self.case = 0
        self.red_after_blue = 0  # 파랑 장애물 마주치고 빨강 장애물 마주치면 기는 횟수 4번 적게
        # self.red_finished = 0  # 빨강 장애물은 하나기 때문에

        # 색상 비율
        self.yellow_blue_ratio = 3
        self.red_ratio = 70
        self.red_up_ratio = 62  # 빨강 장애물에 충분히 다가가는지 체크
        self.side_blue_yellow_ratio = 10  # 장애물 완전히 피했는지 체크
        self.blue_ratio_before_crawl = 60  # 빨강 엎드리기 전에 옆에 파랑 체크

        self.now = datetime.datetime.now().strftime("day:%d h:%H m:%M s:%S")

        # roi1: 노랑, 파랑 장애물; front, thread
        # front: 전방 28~50 cm
        # thread: 전방 50~ cm
        self.roi1_x_start = int(self.ip.width // 6.5)
        self.roi1_x_end = self.ip.width - int(self.ip.width // 6.5)
        self.roi1_y_start_front = self.ip.height - int(self.ip.height // 3.5)
        self.roi1_y_start_thread = self.ip.height - int(self.ip.height // 4.3)
        self.roi1_y_end = self.ip.height
        # roi2: 빨강 장애물
        self.roi2_x_start = 0
        self.roi2_x_end = self.ip.width
        self.roi2_y_start = 0
        self.roi2_y_end = int(self.ip.height // 5.3)
        # roiL: 왼쪽 밑 구석
        self.roiL_x_start = 0
        self.roiL_x_end = 3 * int(self.ip.width // 4)
        self.roiL_y_start = self.ip.height - int(self.ip.height // 3)
        self.roiL_y_end = self.ip.height
        # roiR: 오른쪽 밑 구석
        self.roiR_x_start = int(self.ip.width // 4)
        self.roiR_x_end = self.ip.width
        self.roiR_y_start = self.ip.height - int(self.ip.height // 3)
        self.roiR_y_end = self.ip.height
        # escape roi: 가도되는지
        self.roiE_x_start = int(self.ip.width // 4.4)
        self.roiE_x_end = self.ip.width - int(self.ip.width // 4.4)
        self.roiE_y_start = int(self.ip.height * 0.65)
        self.roiE_y_end = self.ip.height
        # roiS_L: side roi: 빨강 엎드리기 전, 노랑, 파랑 장애물 피하고 옆면 체크
        self.roiS_L_x_start = int(self.ip.width // 5)
        self.roiS_L_x_end = 2 * int(self.ip.width // 5)
        self.roiS_L_y_start = 0
        self.roiS_L_y_end = 2 * int(self.ip.height // 3)
        # roiS_R: side roi: 빨강 엎드리기 전, 노랑, 파랑 장애물 피하고 옆면 체크
        self.roiS_R_x_start = 3 * int(self.ip.width // 5)
        self.roiS_R_x_end = 4 * int(self.ip.width // 5)
        self.roiS_R_y_start = 0
        self.roiS_R_y_end = 2 * int(self.ip.height // 3)

    def run(self):
        while not self.mission_finished:
            self.ip.clear()
            # 노랑 or 파랑 / 빨강 장애물이 나올 때 까지 걷기; 멈추기
            if self.case == 0:
                self.set_head("oblique")
                time.sleep(0.3)
                is_obstacle = self.obs_0_1_check_obstacle_front()
                if is_obstacle:
                    self.case = 1
                else:
                    self.set_head("up")
                    time.sleep(0.3)
                    self.case += self.obs_0_2_walk_until_obstacle()  # return = 1 or 3
            elif self.case == 1:
                # 노랑 or 파랑일 경우
                self.set_head("down")
                time.sleep(0.3)
                self.ip.clear()
                frame = self.ip.getFrame()
                direction = self.obs_1_1_choose_direction(frame)  # return = 2 or 3
                self.obs_1_2_move(direction)
                self.set_head("down")
                time.sleep(0.3)
                self.case += self.obs_1_3_escape_and_check_obstacle(direction)
            elif self.case == 2:
                # case 0으로 돌아가기
                self.case = 0
            elif self.case == 3:
                # 빨강일 경우
                # 센터맞추기
                self.case += self.obs_3_1_check_red_center_blue_side()
            elif self.case == 4:
                # 기어가는 동작, 일어서기
                self.case += self.obs_4_1_crawl()
                # self.red_finished = 1 # 빨강장애물은 하나밖에 없으므로
            elif self.case == 5:
                # case 0 으로 돌아가기
                self.case = 0

    def obs_0_1_check_obstacle_front(self):
        # print("check_obstacle_front 함수 호출")
        yellow_blue_obstacle_flag = 0
        self.ip.clear()
        frame = self.ip.getFrame()

        success = 0
        for i in range(2):
            self.ip.clear()
            frame = self.ip.getFrame()
            # roi_1: 로봇이 직진할 떄 장애물에 부딪히지 않고 갈 수 있는 시야영역
            roi_1 = frame[int(self.roi1_y_start_front):int(self.roi1_y_end), int(self.roi1_x_start):int(self.roi1_x_end)]
            yellow_blue_bin = self.get_yellow_blue_bin(roi_1)
            # cv2.imshow("bin", yellow_blue_bin)

            # roi_1 영역에 노랑, 파랑 장애물 유무 판단
            if self.ip.check_color_ratio_bin(yellow_blue_bin, self.yellow_blue_ratio):
                success += 1
            if success > 1:
                yellow_blue_obstacle_flag = 1
                # cv2.imwrite(str(self.now) + "yell_blue_obstacle.png", frame)
                break

        # 디버깅 용 출력 화면
        # cv2.rectangle(frame, (self.roi1_x_start, self.roi1_y_start_front), (self.roi1_x_end, self.roi1_y_end), (0, 0, 255), 1)
        # cv2.imshow("test", frame)
        # cv2.imwrite(str(self.now) + "front", frame)
        # cv2.waitKey(1)
        ###############################################

        if yellow_blue_obstacle_flag:
            # print("check_obstacle_front: 앞에 노랑, 파랑색 장애물 있음")
            # cv2.imwrite(str(self.now) + "front.png", frame)
            return True
        else:
            # print("check_obstacle_front: 없음")
            return False

    def obs_0_2_walk_until_obstacle(self):
        # print("walk_until_obstacle 호출")
        yellow_blue_obstacle_flag = 0
        red_obstacle_flag = 0

        self.robot.ob_startThread()
        while True:
            self.ip.clear()
            frame = self.ip.getFrame()

            # roi_1: 로봇이 직진할 떄 장애물에 부딪히지 않고 갈 수 있는 시야영역
            # 고개 up이기 때문에 oblique 때 보다 roi 세로 높이 낮춤
            roi_1 = frame[self.roi1_y_start_thread:self.roi1_y_end, self.roi1_x_start:self.roi1_x_end]
            # roi_2: 빨강 탐색 영역
            roi_2 = frame[self.roi2_y_start:self.roi2_y_end, self.roi2_x_start:self.roi2_x_end]

            # roi_1 영역에 노랑, 파랑 장애물 유무 판단
            yellow_blue_bin = self.get_yellow_blue_bin(roi_1)
            # print("roi 내 노랑 파랑비율: ", self.ip.check_how_much_color_ratio_bin(yellow_blue_bin))
            if self.ip.check_how_much_color_ratio_bin(yellow_blue_bin) > self.yellow_blue_ratio:
                # success1 += 1
                self.robot.ob_stopThread()
                yellow_blue_obstacle_flag = 1
            # roi_2 영역에 빨강 장애물 유무 판단
            # print("roi 내 빨강비율: ", self.ip.check_how_much_color_ratio(roi_2, "RED"))
            if self.ip.check_how_much_color_ratio(roi_2, "RED") > self.red_ratio:
                self.robot.ob_stopThread()
                red_obstacle_flag = 1

            # 디버깅 용 출력 화면
            # cv2.rectangle(frame, (self.roi1_x_start, self.roi1_y_start_thread), (self.roi1_x_end, self.roi1_y_end),
            #              (0, 0, 255), 2)
            # cv2.rectangle(frame, (self.roi2_x_start, self.roi2_y_start), (self.roi2_x_end, self.roi2_y_end),
            #              (0, 255, 0), 2)

            # cv2.imshow("test", frame)
            # yellow_blue_bin = self.get_yellow_blue_bin(frame)
            # red_bin = self.ip.getBinImage(frame, "RED")
            # red_yellow_blue_bin = cv2.bitwise_or(yellow_blue_bin, red_bin)
            # cv2.imshow("test2", red_yellow_blue_bin)
            # cv2.imwrite(str(self.now) + "red_obstacle.png", frame)
            # cv2.waitKey(1)
            ########################################################

            # if red_obstacle_flag and not self.red_finished:
            if yellow_blue_obstacle_flag:
                # print("walk_until_obstacle: 파랑색 장애물 때문")
                # TODO: 앞으로 몇걸음 가기 (고개를 up 한상태로 본거라 장애물이 좀 멀리 있을것이기 때문)
                self.robot.ob_walk(3)
                time.sleep(0.3)
                return 1
            elif red_obstacle_flag:
                # print("walk_until_obstacle: 빨강색 장애물 때문")
                # self.robot.ob_walk(7)
                time.sleep(0.3)
                self.robot.ob_walk(3)
                self.check_red_near("thread")
                return 3
            else:
                # print("walk_until_obstacle: 걷는중")
                pass

    def obs_1_1_choose_direction(self, frame):
        y_start = int((self.ip.height * 0.75) // 3)

        self.set_head("left")  # 왼쪽 방향 보기
        time.sleep(0.3)
        self.ip.clear()
        left_img = self.ip.getFrame()
        # cv2.rectangle(left_img, (self.roiL_x_start, self.roiL_y_start), (self.roiL_x_end, self.roiL_y_end), (0, 0, 255), 2)
        # cv2.imshow("test", left_img)
        # cv2.imwrite(str(self.now) + "left.png", left_img)
        left_img = left_img[self.roiL_y_start:self.roiL_y_end, self.roiL_x_start:self.roiL_x_end]
        left_ratio = self.ip.check_how_much_color_ratio(left_img, "YELLOW")

        self.set_head("right")  # 오른쪽 방향 보기
        time.sleep(0.3)
        self.ip.clear()
        right_img = self.ip.getFrame()
        # cv2.rectangle(right_img, (self.roiR_x_start, self.roiR_y_start), (self.roiR_x_end, self.roiR_y_end), (0, 0, 255), 2)
        # cv2.imshow("test", right_img)
        # cv2.imwrite(str(self.now) + "right.png", right_img)
        right_img = right_img[self.roiR_y_start:self.roiR_y_end, self.roiR_x_start:self.roiR_x_end]
        right_ratio = self.ip.check_how_much_color_ratio(right_img, "YELLOW")

        # self.set_head("down")

        # print("choose_direction 왼쪽 노랑 비율: ", left_ratio)
        # print("choose_direction 오른쪽 노랑 비율: ", right_ratio)
        # left: 2, right: 3
        if left_ratio > 2 and right_ratio < 1:
            # 노랑이 왼쪽 o, 오른쪽 x
            # print("choose_direction: 노랑이 왼쪽 o, 오른쪽 x")
            return 3
        elif left_ratio < 1 and right_ratio > 2:
            # 노랑이 왼쪽 x, 오른쪽 o
            # print("choose_direction: 노랑이 왼쪽 x, 오른쪽 o")
            return 2
        elif left_ratio < 1 and right_ratio < 1:
            # print("choose_direction: roi 3등분 해서 장애물 없는 쪽으로")
            roi_1_L = frame[int(self.ip.height // 2):self.roi1_y_end, 0:int(self.ip.width // 4)]
            roi_1_R = frame[int(self.ip.height // 2):self.roi1_y_end,
                      self.ip.width - int(self.ip.width // 4):self.ip.width]
            roi_1_L = self.get_yellow_blue_bin(roi_1_L)
            roi_1_R = self.get_yellow_blue_bin(roi_1_R)
            # print("choose_direction roi 왼쪽 노랑, 파랑 비율: ", self.ip.check_how_much_color_ratio_bin(roi_1_L))
            # print("choose_direction roi 오른쪽 노랑, 파랑 비율: ", self.ip.check_how_much_color_ratio_bin(roi_1_R))
            if abs(self.ip.check_how_much_color_ratio_bin(roi_1_L) - self.ip.check_how_much_color_ratio_bin(
                    roi_1_R)) < 5:
                return 2
            elif self.ip.check_how_much_color_ratio_bin(roi_1_L) < self.ip.check_how_much_color_ratio_bin(roi_1_R):
                return 2
            else:
                return 3
        elif left_ratio > right_ratio:
            # 노랑이 왼쪽이 많음
            # print("choose_direction: 노랑이 왼쪽이 많음")
            return 3
        elif left_ratio < right_ratio:
            # 노랑이 오른쪽이 많음
            # print("choose_direction: 노랑이 오른쪽이 많음")
            return 2

    def obs_1_2_move(self, direction):
        self.set_head("oblique")
        time.sleep(0.2)
        self.robot.ob_move(direction)
        self.robot.ob_move(direction)
        self.robot.ob_move(direction)
        self.robot.ob_move(direction)
        if direction == 3:
            self.robot.ob_move(direction)
        # time.sleep(0.3)
        # if direction == 2:
        #     self.robot.action(80)
        # elif direction == 3:
        #     self.robot.action(81)

    def obs_1_3_escape_and_check_obstacle(self, direction):
        escape_flag = 0
        self.ip.clear()

        success = 0
        for i in range(2):
            self.ip.clear()
            frame = self.ip.getFrame()
            # 로봇이 직진할 떄 장애물에 부딛히지 않고 갈 수 있는 시야영역
            roi_E = frame[self.roiE_y_start:self.roiE_y_end, self.roiE_x_start:self.roiE_x_end]
            yellow_blue_bin = self.get_yellow_blue_bin(roi_E)

            # roi_E 영역에 노랑, 파랑 장애물 유무 판단
            if self.ip.check_how_much_color_ratio_bin(yellow_blue_bin) < 6:
                success += 1
            if success > 1:
                escape_flag = 1
                # cv2.imwrite(str(self.now) + "escape_go.png", frame)
                break

        # 디버깅용 출력 화면
        # cv2.rectangle(frame, (self.roiE_x_start, self.roiE_y_start), (self.roiE_x_end, self.roiE_y_end), (0, 0, 255), 2)
        # cv2.imshow("test", frame)
        # cv2.waitKey(1)

        if escape_flag:
            # print("escape_and_check_obstacle: 앞으로 가도됨")
            # 장애물 완전히 피하기
            if direction == 2:
                # left
                self.set_head("right")
                self.ip.clear()
                frame = self.ip.getFrame()
                roi = frame[self.roiS_L_y_start:self.roiS_L_y_end, self.roiS_L_x_start:self.roiS_L_x_end]
                roi_bin = self.get_yellow_blue_bin(roi)
                # print("피하고 오른쪽 마지막 체크 비율", self.ip.check_how_much_color_ratio_bin(roi_bin))
                if self.ip.check_how_much_color_ratio_bin(roi_bin) > self.side_blue_yellow_ratio:
                    # print("escape_and_check_obstacle: 덜피해서 왼쪽으로 더 피함")
                    self.set_head("oblique")
                    time.sleep(0.3)
                    self.robot.ob_move(direction)
                    self.robot.ob_move(direction)
                    time.sleep(0.2)
            elif direction == 3:
                # right
                self.set_head("left")
                self.ip.clear()
                frame = self.ip.getFrame()
                roi = frame[self.roiS_R_y_start:self.roiS_R_y_end, self.roiS_R_x_start:self.roiS_R_x_end]
                roi_bin = self.get_yellow_blue_bin(roi)
                # print("피하고 왼쪽 마지막 체크 비율", self.ip.check_how_much_color_ratio_bin(roi_bin))
                if self.ip.check_how_much_color_ratio_bin(roi_bin) > self.side_blue_yellow_ratio:
                    # print("escape_and_check_obstacle: 덜피해서 오른쪽으로 더 피함")
                    self.set_head("oblique")
                    time.sleep(0.3)
                    self.robot.ob_move(direction)
                    self.robot.ob_move(direction)
                    time.sleep(0.2)

            if self.check_red_near("escape"):
                # print("escape_and_check_obstacle: 파랑 노랑 넘고 빨강 발견함")
                self.red_after_blue = 1
                return 3
            return 1
        else:
            # print("escape_and_check_obstacle: 옆으로 더가야함")
            return 0

    def obs_3_1_check_red_center_blue_side(self):
        self.ip.clear()
        frame = self.ip.getFrame()
        # 화면을 세로로 나눠서 왼, 오 중 빨간색이 더 많은 쪽으로 옆걸음
        x_block = int(self.ip.width // 3)

        left_img = frame[0:self.ip.height // 2, 0:x_block]
        right_img = frame[0:self.ip.height // 2, x_block * 2:self.ip.width]

        left_ratio = self.ip.check_how_much_color_ratio(left_img, "RED")
        right_ratio = self.ip.check_how_much_color_ratio(right_img, "RED")

        # 디버깅용 화면
        # cv2.rectangle(frame, (0, 0), (x_block, self.ip.height//2), (0, 0, 255), 2)
        # cv2.rectangle(frame, (x_block*2, 0), (self.ip.width, self.ip.height//2), (0, 0, 255), 2)
        # cv2.imwrite(str(self.now) + "ready_crawl_check_red_center.png", frame)
        # cv2.imshow("test", frame)
        # cv2.waitKey(1)

        # print("ready_crawl: 왼, 오 빨강 비율 차이: ", abs(left_ratio - right_ratio))
        if abs(left_ratio - right_ratio) < 40:
            # print("ready_crawl: 빨강 센터: 맞음")

            self.set_head("left")
            time.sleep(0.3)
            self.ip.clear()
            frame = self.ip.getFrame()
            roi_L = frame[self.roiS_L_y_start:self.roiS_L_y_end, self.roiS_L_x_start:self.roiS_L_x_end]
            if self.ip.check_how_much_color_ratio(roi_L, "OB_BLUE") > self.blue_ratio_before_crawl:
                # print("ready_crawl: 오른쪽편 파랑 있음: 왼쪽으로")
                # cv2.rectangle(frame, (self.roiS_L_x_start, self.roiS_L_y_start), (self.roiS_L_x_end, self.roiS_L_y_end), (0, 0, 255), 2)
                # cv2.imshow("test", frame)
                self.set_head("oblique")
                time.sleep(0.3)
                self.robot.ob_move(3)
                self.robot.ob_move(3)
                # time.sleep(0.3)

            self.set_head("right")
            time.sleep(0.3)
            self.ip.clear()
            frame = self.ip.getFrame()
            roi_R = frame[self.roiS_R_y_start:self.roiS_R_y_end, self.roiS_R_x_start:self.roiS_R_x_end]
            if self.ip.check_how_much_color_ratio(roi_R, "OB_BLUE") > self.blue_ratio_before_crawl:
                # print("ready_crawl: 왼쪽편 파랑 있음: 오른쪽으로")
                # cv2.rectangle(frame, (self.roiS_R_x_start, self.roiS_R_y_start), (self.roiS_R_x_end, self.roiS_R_y_end), (0, 0, 255), 2)
                # cv2.imshow("test", frame)
                self.set_head("oblique")
                time.sleep(0.3)
                self.robot.ob_move(2)
                self.robot.ob_move(2)
                # time.sleep(0.3)
            return 1
        elif left_ratio < right_ratio:
            # TODO: 센터맞추기 위한 오른쪽으로 옆걸음 동작
            # print("ready_crawl: 빨강센터: 오른쪽으로")
            self.robot.ob_move(3)
            return 0
        elif left_ratio > right_ratio:
            # TODO: 센터맞추기 위한 왼쪽으로 옆걸음 동작
            # print("ready_crawl: 빨강센터: 왼쪽으로")
            self.robot.ob_move(2)
            return 0

    def obs_4_1_crawl(self):
        # 30cm 가야댐
        if self.red_after_blue == 1:
            self.robot.ob_crawl_short()
            self.red_after_blue = 0
        else:
            self.robot.ob_crawl()
        # return 1

    def get_yellow_blue_bin(self, frame):
        yellow_bin = self.ip.getBinImage(frame, "OB_YELLOW")
        blue_bin = self.ip.getBinImage(frame, "OB_BLUE")
        return cv2.bitwise_or(yellow_bin, blue_bin)

    def set_head(self, direction):
        # oblique: 0, up: 1, left: 2, right: 3
        if direction == "oblique":
            return self.robot.ob_head(0)
            # return 1
        elif direction == "up":
            return self.robot.ob_head(1)
            # return 1
        elif direction == "left":
            return self.robot.ob_head(2)
            # return 1
        elif direction == "right":
            return self.robot.ob_head(3)
            # return 1
        elif direction == "down":
            return self.robot.ob_head(4)
        elif direction == "red_up":
            return self.robot.ob_head(5)
            # return 1

    def check_red_near(self, mode):
        time.sleep(0.2)
        self.robot.action(87)  # 고개 드는 동작
        # print("고개들고 빨강 체크")
        time.sleep(0.3)
        self.ip.clear()
        frame = self.ip.getFrame()
        roi_up = frame[self.roi2_y_start:2 * self.roi2_y_end, self.roi2_x_start:self.roi2_x_end]
        roi_up_below = frame[int((self.ip.height // 4)):2 * int(self.ip.height // 4), self.roi2_x_start:self.roi2_x_end]
        # cv2.rectangle(frame, (self.roi2_x_start, self.roi2_y_start), (self.roi2_x_end, 2*self.roi2_y_end), (255, 0, 0), 2)
        # cv2.rectangle(frame, (self.roi2_x_start, int((self.ip.height // 4))), (self.roi2_x_end, 2*int(self.ip.height//4)), (255, 0, 0), 2)
        # cv2.imwrite(str(self.now) + "escape_up_up.png", frame)
        # print("고개들었을때 위쪽 빨강 비율:", self.ip.check_how_much_color_ratio(roi_up, "RED"))
        # print("고개들었을 때 아래쪽 빨강 비율: ", self.ip.check_how_much_color_ratio(roi_up_below, "RED"))
        if self.ip.check_how_much_color_ratio(roi_up, "RED") > self.red_up_ratio and self.ip.check_how_much_color_ratio(
                roi_up_below, "RED") > self.red_up_ratio:
            return 1
        elif self.ip.check_how_much_color_ratio(roi_up,
                                                "RED") > self.red_up_ratio or self.ip.check_how_much_color_ratio(
                roi_up_below, "RED") > self.red_up_ratio:
            for i in range(8):
                # print("고개 들었을 때 한 영역만 빨강비율 높아서 더 다가감")
                time.sleep(0.2)
                if self.check_red_front():
                    break
                self.set_head("oblique")
                time.sleep(0.2)
                self.robot.ob_walk(3)
                time.sleep(0.2)
            return 1
        else:
            if mode == "thread":
                for i in range(8):
                    # print("고개 들었을 때 한 영역만 빨강비율 높아서 더 다가감")
                    time.sleep(0.2)
                    if self.check_red_front():
                        break
                    self.set_head("oblique")
                    time.sleep(0.2)
                    self.robot.ob_walk(3)
                    time.sleep(0.2)
            return 0

    def check_red_front(self):
        # self.set_head("red_up")
        self.robot.action(87)  # 고개 드는 동작
        # print("고개들고 빨강 체크")
        time.sleep(0.3)
        self.ip.clear()
        frame = self.ip.getFrame()
        roi_up = frame[self.roi2_y_start:self.roi2_y_end, self.roi2_x_start:self.roi2_x_end]
        roi_up_below = frame[int((self.ip.height // 4)):2 * int(self.ip.height // 4), self.roi2_x_start:self.roi2_x_end]
        # cv2.rectangle(frame, (self.roi2_x_start, self.roi2_y_start), (self.roi2_x_end, self.roi2_y_end), (0, 0, 255), 2)
        # cv2.imwrite(str(self.now) + "escape_up_up.png", frame)
        # print("고개들었을때 위쪽 빨강 비율:", self.ip.check_how_much_color_ratio(roi_up, "RED"))
        # print("고개들었을 때 아래쪽 빨강 비율: ", self.ip.check_how_much_color_ratio(roi_up_below, "RED"))
        if self.ip.check_how_much_color_ratio(roi_up, "RED") > self.red_up_ratio and self.ip.check_how_much_color_ratio(
                roi_up_below, "RED") > self.red_up_ratio:
            return 1
        else:
            return 0


# cam = cv2.VideoCapture(0)
#
# if __name__ == '__main__':
#     # robot = Motion()
#     ip = ImageProcessor()
#     ob = ObstacleRun(ip)
#     mission_finished = 0
#     while not mission_finished:
#         # img = ip.getFrame()
#         # yellow_blue_bin = ob.get_yellow_blue_bin(img)
#
#         # red_bin = ip.getBinImage(img, "RED")
#
#         # ob.walk_until_obstacle()
#         # ob.choose_direction(img)
#         # ob.escape_and_check_obstacle(2)
#         # ob.ready_crawl(img)
#         # ob.check_obstacle_front()
#         # roi = ob.region_of_interest(img, [ob.vertices_L])
#         # cv2.imshow("red bin", red_bin)
#         # ob.run()
#
#         if cv2.waitKey(25) >= 0:
#             break
#
#     ip.clear()
#     cv2.destroyAllWindows()