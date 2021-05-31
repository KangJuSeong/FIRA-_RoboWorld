# from .consts import COLOR
import cv2


class ImageProcessor:
    def __init__(self):

        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        self.cap.set(cv2.CAP_PROP_EXPOSURE, 0)
        # self.cap.set(cv2.CAP_PROP_AUTO_WB, 0)
        self.ip = None
        self.height = int(self.cap.get(4))
        self.width = int(self.cap.get(3))
        pass

    def getFrame(self):
        ret, frame = self.cap.read()
        return frame

    def clear(self):
        self.cap.read()
        self.cap.read()
        self.cap.read()
        self.cap.read()

    def getBinImage(self, frame, color):
        if color is None:
            return frame
        """
        if color == "WHITE":
            gray_img = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)  # 흑백이미지로 변환
            ret, mask = cv2.threshold(gray_img, 200, 255, cv2.THRESH_BINARY)
            return mask
        """

        HSV = {
            "RED": {
                "hsv": [177, 170, 170],
                "err": [25, 80, 80]
            },
            "DARK RED": {
                "hsv": [177, 186, 171],
                "err": [20, 60, 90]
            },
            "YELLOW": {
                # 경기장 라인 값(20)
                "hsv": [22, 163, 163],
                "err": [20, 70, 60]
                # 경기장 라인 값(17)
                # "hsv": [22, 183, 163],
                # "err": [20, 40, 70]
            },
            "OB_YELLOW": {
                # OBSTACLERUN
                "hsv": [15, 200, 200],
                "err": [35, 55, 55]
            },
            "OB_BLUE": {
                # OBSTACLERUN
                "hsv": [100, 200, 200],
                "err": [20, 55, 55]
            },
            "OB_RED": {
                # OBSTACLERUN
                "hsv": [177, 200, 200],
                "err": [20, 55, 55]
            },
            "BLUE": {
                # 경기장 라인 값(20)
                "hsv": [100, 163, 163],
                "err": [20, 65, 70]
                # 경기장 라인 값(17)
                # "hsv": [22, 183, 163],
                # "err": [20, 40, 70]
            },
            "WHITE": {
                # 경기장 라인 값(20)
                "hsv": [68, 167, 167],
                "err": [20, 87, 87]
                # 경기장 라인 값(17)
                # "hsv": [22, 183, 163],
                # "err": [20, 40, 70]
            },

            "VALVE_NEAR": {
                # 경기장 값(20)
                "hsv": [177, 186, 171],
                "err": [20, 60, 90]
                # 경기장 값(17)
                # "hsv": [177, 186, 171],
                # "err": [20, 60, 90]
                # 코봇방 값(17)
                # "hsv": [172, 157, 177],
                # "err": [20, 60, 90]
            },
            "VALVE_FAR": {
                # 코방값(17)
                #
                "hsv": [172, 157, 177],
                "err": [20, 60, 90]
            }
        }

        p = HSV[color]
        h_value, s_value, v_value = p["hsv"]

        img_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        hsv__lower = (h_value - p["err"][0], s_value -
                      p["err"][1], v_value - p["err"][2])
        hsv__upper = (h_value + p["err"][0], s_value +
                      p["err"][1], v_value + p["err"][2])
        rgb__lower = (200, 200, 200)
        rgb__upper = (255, 255, 255)

        # kernel = np.ones((5, 5), np.uint8)
        # mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        if color == "WHITE":
            mask = cv2.inRange(frame, rgb__lower, rgb__upper)
        else:
            mask = cv2.inRange(img_hsv, hsv__lower, hsv__upper)

        mask = cv2.dilate(mask, None, iterations=3)
        mask = cv2.erode(mask, None, iterations=1)
        mask = cv2.dilate(mask, None, iterations=3)

        # if color == "WHITE":
        #    mask = cv2.bitwise_not(mask)

        return mask

    def weighted_img(self, frame, initial_img, α=1, β=1., λ=0.):  # 두 이미지 operlap 하기
        return cv2.addWeighted(initial_img, α, frame, β, λ)

    # 한 화면에서 해당 색이 정해진 퍼센트 이상인가?
    def check_color_ratio(self, frame, color, ratio):
        bin = self.getBinImage(frame, color)
        frame_ratio = cv2.countNonZero(bin) / (frame.shape[0] * frame.shape[1]) * 100
        if frame_ratio >= ratio:
            return 1
        else:
            return 0

    # 한 화면에서 해당 색이 정해진 퍼센트 이상인가? - bin 화면 입력
    def check_color_ratio_bin(self, bin, ratio):
        frame_ratio = cv2.countNonZero(bin) / (bin.shape[0] * bin.shape[1]) * 100
        if frame_ratio >= ratio:
            return 1
        else:
            return 0

    # 한 화면에서 해당 색이 몇퍼센트 이상인가?
    # TODO: 2 픽셀 건더뛰기로 효율 높일 수 있음
    def check_how_much_color_ratio(self, frame, color):
        bin = self.getBinImage(frame, color)
        return cv2.countNonZero(bin) / (frame.shape[0] * frame.shape[1]) * 100

    def check_how_much_color_ratio_bin(self, bin):
        return cv2.countNonZero(bin) / (bin.shape[0] * bin.shape[1]) * 100


"""
if __name__ == '__main__':
    pr = ImageProcessor()
    # pr.robot.init()
    # pr.robot.head(view=MOTION["VIEW"]["DOWN"])
    # pr.command(func=FUNCS["SET_YELLOW_LINE"], debug=True)
    while True:
        frame = pr.getFrame()
        bin = pr.getBinImage(frame, "WHITE")
        cv2.imshow("image", frame)
        cv2.imshow("bin", bin)
        if cv2.waitKey(25) >= 0:
            break
"""
