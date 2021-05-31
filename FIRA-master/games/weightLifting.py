import cv2
import numpy as np
from library.image_processor import ImageProcessor
#from library.motion import Motion
import time

"""
#----알고리즘----#
# 출발
# 걷기
    # 두걸음 걸을 때 마다 수평 센터 체크
        # 가로 ROI 영역에 하얀색 일정 비율 높아지면 맞추기
    # 한 걸음 걸을 때 마다 노랑색 체크
        # 어느 거리 이상: oblique
        # 어느 거리 이하: down
# 수평, 센터 맞추기 - 노랑색 봉으로
# Pick-up Line 에 위치한 역기 들기 (+ 한발짝)
# 역기 들고 걷기
    # 두걸음 걸을 때 마다 수평 센터 체크
        # 가로 ROI 영역에 하얀색 일정 비율 높아지면 맞추기
    # 한 걸음 걸을 때 마다 흰색 체크
        # 어느 거리 이상: oblique
        # 어느 거리 이하: down
# 수평, 센터 맞추기
# 몇걸음 가기 (Lift Line 밟기)
# 옆에보고 흰색 선 밟았는지 확인
# 역기 머리위로 들기
# 역기 머리위로 들고 걷기
    # 두걸음 걸을 때 마다 수평 센터 체크
        # 가로 ROI 영역에 하얀색 일정 비율 높아지면 맞추기
    # 한 걸음 걸을 때 마다 흰색 체크
        # 어느 거리 이상: oblique
        # 어느 거리 이하: down
        
#----동작----#
# 기본 걷기
# 기본에서 turn, 옆걸음
# 역기 들기
# 역기 들고 걷기
# 역기 들고 turn, 옆걸음
# 역기 머리위로 들기
# 역기 머리위로 들고 걷기
# 역기 머리위로 들고 turn, 옆걸음
"""

class WeightLifting:
    #def __init__(self, robot, ip):
    def __init__(self, ip):
        #imageProcessor
        self.ip = ip
        #local
        self.mission_finished = 0
        self.case = 0
        self.step_count = 0
        self.yellow_flag = 0
        self.case2_first_flag = 0
        self.case4_first_flag = 0
        self.case9_first_flag = 0
        pass

    def run(self):
        while not self.mission_finished:
            if self.case == 0:
                # 시작 처음 한발짝 내딛기
                print("case 0 집입")
                self.case += self.start_line_0_1_first_step()
                time.sleep(0.5)
            elif self.case == 1:
                #기본 걷기
                # 두걸음 걸을 때 마다 수평 센터 체크
                    # 가로 ROI 영역에 하얀색 일정 비율 높아지면 맞추기
                # 한 걸음 걸을 때 마다 노랑색 체크
                    # 어느 거리 이상: oblique
                    # 어느 거리 이하: down

                # step_count: 걸음 마다 체크하기위한 변수, case 시작시 초기화
                print("case 1 집입")
                if self.case2_first_flag == 0:
                    self.step_count = 0
                    self.case2_first_flag = 1

                straight_flag = 0
                yellow_flag = 0
                frame = self.ip.getFrame()

                if self.step_count % 2 == 0:
                    # 두걸음 걸을 때 마다 수평 센터 체크
                    straight_flag = self.check_straight(frame, "WHITE", 0)

                # 한 걸음 걸을 때 마다 노랑색 체크
                yellow_flag = self.start_line_1_2_check_color_near(frame, "YELLOW")
                self.step_count += 1

                if yellow_flag:
                    self.case += 1
                elif straight_flag and not yellow_flag:
                    self.start_line_1_1_walk()
            elif self.case == 2:
                # 수평, 센터 맞추기 - 노랑색 봉으로, 파랑이로
                straight_flag = 0
                center_flag = 0
                frame = self.ip.getFrame()

                # 파랑으로 센터맞추기
                center_flag = self.check_center(frame)

                # 노란 봉으로 수평 맞추기
                straight_flag = self.check_straight(frame, "YELLOW", 0)

                if straight_flag and center_flag:
                    self.case += 1
            elif self.case == 3:
                # Pick-up Line 에 위치한 역기 들기 (+ 한발짝)
                self.case += self.pick_up_line_3_1_lift_low()
            elif self.case == 4:
                # 역기 들고 걷기
                # 두걸음 걸을 때 마다 수평 센터 체크
                # 가로 ROI 영역에 하얀색 일정 비율 높아지면 맞추기
                # 한 걸음 걸을 때 마다 흰색 체크
                # 어느 거리 이상: oblique
                # 어느 거리 이하: down

                # step_count: 걸음 마다 체크하기위한 변수, case 시작시 초기화
                if self.case4_first_flag == 0:
                    self.step_count = 0
                    self.case4_first_flag = 1

                straight_flag = 0
                lift_line_flag = 0
                frame = self.ip.getFrame()

                if self.step_count % 2 == 0:
                    # 두걸음 걸을 때 마다 수평 센터 체크
                    straight_flag = self.check_straight(frame, "WHITE", 1)

                # 한 걸음 걸을 때 마다 하얀색 체크
                lift_line_flag = self.start_line_1_2_check_color_near(frame, "WHITE")
                self.step_count += 1

                if lift_line_flag:
                    # 고개 숙이기
                    self.set_head("DOWN")
                    self.case += 1
                elif straight_flag and not lift_line_flag:
                    self.pick_up_line_4_1_walk()
            elif self.case == 5:
                # 수평 맞추기
                frame = self.ip.getFrame()
                self.case += self.check_straight(frame, "WHITE", 1)
            elif self.case == 6:
                # 몇걸음 가기 (Lift Line 밟기)
                self.pick_up_line_4_1_walk()
                self.pick_up_line_4_1_walk()
                self.case += 2
            #elif self.case == 7:
                # 옆에보고 흰색 선 밟았는지 확인
                #self.set_head("RIGHT")
                #frame = self.ip.getFrame()
                #self.case += self.lift_line_7_1_check_step_line(frame, "WHITE")
            elif self.case == 8:
                # 역기 머리위로 들기
                self.case += self.lift_line_8_1_lift_high()
            elif self.case == 9:
                # 역기 머리위로 들고 걷기
                # 두걸음 걸을 때 마다 수평 센터 체크
                # 가로 ROI 영역에 하얀색 일정 비율 높아지면 맞추기
                # 한 걸음 걸을 때 마다 흰색 체크
                # 어느 거리 이상: 두걸음 마다 체크
                # 어느 거리 이하: 그냥 쭉 걷기
                if self.case9_first_flag == 0:
                    self.step_count = 0
                    self.case9_first_flag = 1

                straight_flag = 0
                finish_line_flag = 0
                frame = self.ip.getFrame()

                if self.step_count % 2 == 0:
                    # 두걸음 걸을 때 마다 수평 센터 체크
                    straight_flag = self.check_straight(frame, "WHITE", 2)

                # 한 걸음 걸을 때 마다 노랑색 체크
                finish_line_flag = self.start_line_1_2_check_color_near(frame, "WHITE")
                self.step_count += 1

                if finish_line_flag:
                    for i in range(5):
                        self.lift_line_9_1_walk()
                    self.mission_finished = 1
                elif straight_flag and not finish_line_flag:
                    self.lift_line_9_1_walk()


    def start_line_0_1_first_step(self):
        print("start_line_0_1_first_step 호출")
        #return self.robot.wl_first_step()
        return 1

    def start_line_1_1_walk(self):
        print("start_line_1_1_walk: 기본 걷기 (2걸음)")
        #return self.robot.wl_walk(0)
            #base: 0, low: 1, high: 2
        return 1

    def check_straight(self, frame, color, mode):
        print("start_line_1_2_check_straight: 앞 선으로 직각, 센터 맞추기")
        bin = self.ip.getBinImage(frame, color)
        #화면 자르기
        x_block = int((self.ip.width//3)//3)
        x_start = int(self.ip.width//2 - (x_block*1.5))
        y_block = int((self.ip.height//9))
        y_start = 0

        sliced_img = []
        # 영상 분할
        for i in range(9):
            for j in range(3):
                sliced_img.append(frame[y_start+y_block*i:y_start+y_block*(i+1), x_start+x_block*j:x_start+x_block*(j+1)])

        # 박스 그리기 - 디버깅용
        for i in range(9):
            for j in range(3):
                cv2.rectangle(frame, (x_start+x_block*j, y_start+y_block*i), (x_start+x_block*(j+1), y_start+y_block*(i+1)), (0, 0, 255), 2)
        cv2.imshow("result", frame)

        # 흰 선이 위치한 센터 구하기
        cX, cY = self.start_line_1_2_1_getRecCenter(bin)
        cv2.line(frame, (cX, cY), (cX, cY), (0, 255, 0), 4)
        # 흰 선이 위치한 block 파랑으로 색칠
        index = 3*(cY // y_block) + 1   # sliced_img 리스트의 index
        if index == 28:
            index = 25

        # 파랑 block 대각선 위쪽 block 흰색 비율 비교
        upper_left_img = sliced_img[index - 4]
        upper_right_img = sliced_img[index - 2]
        # 둘다 흰색 o
        if self.ip.check_color_ratio(upper_left_img, color, 5) and self.ip.check_color_ratio(upper_right_img, color, 5):
            #uppter_left의 흰색비율과 upper_right의 흰색비율이 30보다 작으면 수평이라 간주함
            if abs(self.ip.check_how_much_color_ratio(upper_left_img, color) - self.ip.check_how_much_color_ratio(upper_right_img, color)) < 30:
                print("수평")
                return 1
            else:
                if self.ip.check_how_much_color_ratio(upper_left_img, color) - self.ip.check_how_much_color_ratio(upper_right_img, color) > 0:
                    # TODO: 오른쪽으로 turn
                    print("오른쪽으로 turn 하는 동작")
                    """
                    if mode == 0:
                        return self.robot.wl_turn(0, 1)
                    elif mode == 1:
                        return self.robot.wl_turn(1, 1)
                    elif mode == 2:
                        return self.robot.wl_turn(2, 1)
                    """
                    return 0
                elif self.ip.check_how_much_color_ratio(upper_left_img, color) - self.ip.check_how_much_color_ratio(upper_right_img, color) < 0:
                    # TODO: 왼쪽으로
                    print("왼쪽으로 turn 하는 동작")
                    """
                    if mode == 0:
                        return self.robot.wl_turn(0, 0)
                    elif mode == 1:
                        return self.robot.wl_turn(1, 0)
                    elif mode == 2:
                        return self.robot.wl_turn(2, 0)
                    """
                    return 0
        #왼쪽만 흰색 o -> 오른쪽으로 turn
        elif self.ip.check_color_ratio(upper_left_img, color, 5):
            #TODO: 오른쪽으로 turn
            print("오른쪽으로 turn 하는 동작")
            """
            if mode == 0:
                return self.robot.wl_turn(0, 1)
            elif mode == 1:
                return self.robot.wl_turn(1, 1)
            elif mode == 2:
                return self.robot.wl_turn(2, 1)
            """
            return 0
        # 오른쪽만 흰색 o -> 왼쪽으로 turn
        elif self.ip.check_color_ratio(upper_right_img, color, 5):
            #TODO: 왼쪽으로
            print("왼쪽으로 turn 하는 동작")
            """
            if mode == 0:
                return self.robot.wl_turn(0, 0)
            elif mode == 1:
                return self.robot.wl_turn(1, 0)
            elif mode == 2:
                return self.robot.wl_turn(2, 0)
            """
            return 0
        elif not self.ip.check_color_ratio(upper_left_img, color, 1) and not self.ip.check_color_ratio(upper_right_img, color, 1):
            print("수평")
            return 1

    def start_line_1_2_1_getRecCenter(self, bin):
        #TODO: 흰선 최대 두께
        success = 0
        for i in range(self.ip.height):
            for j in range(self.ip.width//2 - 3, self.ip.width//2 + 3):
                if bin[self.ip.height - i - 1, j] == 255:
                    success += 1
                if success > 10:
                    return self.ip.width // 2, self.ip.height - i - 1
        return self.ip.width // 2, self.ip.height


    def start_line_1_2_check_color_near(self, frame, color):
        # 역도를 인식하기 위한 함수
        # 밑에서 두번째 행에 오면 return 1
        print("start_line_1_2_check_yellow_near: 역도가 가까이 왔음을 인지하는 함수")

        y_block = int((self.ip.height//9))
        y_start = 0

        # 디버깅용 사각형 그리기
        cv2.rectangle(frame, (0, y_start + y_block*7), (self.ip.width, y_start+y_block*8), (0, 255, 0), 3)
        roi = frame[y_start + y_block*7:y_start+y_block*8, 0:self.ip.width]
        bin = self.ip.getBinImage(roi, color)

        # 색 일정비율 있는지
        if self.ip.check_color_ratio_bin(bin, 20):
            print("노란선 다가옴")
            return 1
        else:
            print("노란선 아직 x")
            return 0

    def check_center(self, frame):
        # 디버깅용 target 좌표
        cv2.line(frame, (ip.width//2, ip.height//2), (ip.width//2, ip.height//2), (0, 0, 255), 7)

        red_yellow_cir, cX, cY = self.contours(frame)

        # 디버깅용 파랑이 중심 좌표
        cv2.line(frame, (cX, cY), (cX, cY), (0, 255, 0), 7)
        cv2.imshow("result", frame)

        gap = 20
        if abs(self.ip.width//2 - cX) < gap:
            print("센터 맞춤")
            return 1
        elif self.ip.width//2 - cX > 0:
            # TODO: 센터맞추기위한 왼쪽으로 옆걸음 동작
            print("파랑센터: 왼쪽으로")
            """
            if mode == 0:
                return self.robot.wl_move(0, 0)
            elif mode == 1:
                return self.robot.wl_move(1, 0)
            elif mode == 2:
                return self.robot.wl_move(2, 0)
            """
            return 0
        elif self.ip.width//2 - cX < 0:
            # TODO: 센터맞추기 위한 오른쪽으로 옆걸음 동작
            print("파랑센터: 오른쪽으로")
            """
            if mode == 0:
                return self.robot.wl_move(0, 1)
            elif mode == 1:
                return self.robot.wl_move(1, 1)
            elif mode == 2:
                return self.robot.wl_move(2, 1)
            """
            return 0

    def contours(self, frame):
        img_blue = self.ip.getBinImage(frame, "BLUE")
        cv2.imshow("bin_blue", img_blue)

        contours, hierarchy = cv2.findContours(img_blue, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cx = 0
        cy = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 5000:
                epsilon = 0.02 * cv2.arcLength(cnt, True)
                x, y, w, h = cv2.boundingRect(cnt)
                cx = x + w//2
                cy = y + h//2
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                M = cv2.moments(cnt)
                if M['m00'] != 0:

                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])

                    cv2.circle(frame, (cx, cy), 3, (0, 0, 255), -1)
                else:
                    pass
        return frame, cx, cy

    def pick_up_line_3_1_lift_low(self):
        print("pick_up_line_3_1_lift_low 호출")
        # return self.robot.wl_lift_low()
        return 1

    def pick_up_line_4_1_walk(self):
        print("pick_up_line_4_1_walk 호출")
        # return self.robot.wl_walk(1)
        # base: 0, low: 1, high: 2
        return 1

    def set_head(self, dir):
        print("head_down: 머리 아래로")
        # return self.robot.wl_head(dir)
        # oblique: 0, down: 1, right: 2
        return 1

    def lift_line_8_1_lift_high(self):
        print("lift_line_7_1_lift_high: 머리 위로 들기")
        # return self.robot.wl_lift_high()
        return 1

    #안되면 수정해서 쓰기
    def lift_line_7_1_check_step_line(self, frame, color):
        bin = self.ip.getBinImage(frame, color)
        #화면 자르기
        x_block = int((self.ip.width//3)//3)
        x_start = int(self.ip.width//2 - (x_block*0.5))
        y_block = int((self.ip.height//9))
        y_start = 0


        #TODO: 밑에쪽 완전히 흰선 안보이는 roi는 그냥 제외 시키기
        sliced_left = []
        sliced_mid = []
        sliced_right = []
        # 영상 분할
        for i in range(9):
            sliced_left.append(frame[y_start+y_block*i:y_start+y_block*(i+1), x_start-x_block:x_start])
            sliced_mid.append(frame[y_start+y_block*i:y_start+y_block*(i+1), x_start:x_start+x_block])
            sliced_right.append(frame[y_start+y_block*i:y_start+y_block*(i+1), x_start+x_block:x_start+x_block*2])

        # 박스 그리기 - 디버깅용
        for i in range(9):
            cv2.rectangle(frame, (x_start, y_start + y_block * i),
                          (x_start + x_block, y_start + y_block * (i + 1)), (0, 0, 255), 2)

        success_left = 0
        success_mid = 0
        success_right = 0

        #TODO: 흰색 ratio 수치 조정
        for i in range(9):
            if self.ip.check_color_ratio(sliced_left[i], color, 20):
                success_left += 1
            if self.ip.check_color_ratio(sliced_mid[i], color, 20):
                success_mid += 1
            if self.ip.check_color_ratio(sliced_right[i], color, 20):
                success_right += 1
            #if success_left > 3:



    def lift_line_9_1_walk(self):
        print("lift_line_9_1_walk 호출")
        # return self.robot.wl_walk(2)
        # base: 0, low: 1, high: 2
        return 1

    def test(self, frame, color):
        #한 화면에서 해당 색이 몇퍼센트인가
        bin = self.ip.getBinImage(frame, color)
        ratio = cv2.countNonZero(bin) / (frame.shape[0]*frame.shape[1])
        print("cv2 사용 퍼센트: ", ratio * 100)







"""
if __name__ == '__main__':
    #robot = Motion()
    ip = ImageProcessor()
    wl = WeightLifting(ip)
    #wl.run()
    while True:
        img = ip.getFrame()
        bin = ip.getBinImage(img, "WHITE")
        x, y = wl.start_line_1_2_1_getRecCenter(bin)

        cv2.line(bin, (x, y), (x, y), (0, 0, 255), 10)
        #wl.check_straight(img, "WHITE")
        #wl.start_line_1_2_check_color_near(img, "YELLOW")
        #wl.check_straight_center(img, "YELLOW")
        #wl.check_center(img)
        #wl.lift_line_7_1_check_step_line(img, "WHITE")
        wl.run()
        cv2.imshow("recCenter", img)
        cv2.imshow("bin", bin)

        if cv2.waitKey(25) >= 0:
            break

    ip.clear()
    cv2.destroyAllWindows()
"""