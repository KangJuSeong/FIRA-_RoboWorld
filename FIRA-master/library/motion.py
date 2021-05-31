# from .consts import *
import serial
import threading
import time

# TODO: Add stable check decorator
SPRINT = {

    "INIT": 2,
    "W_INIT": 3,
    "F": {
        "STRAIGHT": 4,
        "LEFT": 5,
        "RIGHT": 6,
    },
    "FINISH": 8,
    "B": {
        "STRAIGHT": 9,
        "LEFT": 10,
        "RIGHT": 11
    }
}
WEIGHTLIFTING = {
    "INIT": 11,
    "BASIC": {
        "WALK": 12,
        "TURN": {
            "LEFT": 13,
            "RIGHT": 14,
        },
        "MOVE": {
            "LEFT": 15,
            "RIGHT": 16,
        }
    },
    "LOW": {
        "LIFT": 17,
        "WALK": 18,
        "TURN": {
            "LEFT": 19,
            "RIGHT": 20,
        },
        "MOVE": {
            "LEFT": 21,
            "RIGHT": 22,
        }
    },
    "HIGH": {
        "LIFT": 7,
        "WALK": 8,
        "TURN": {
            "LEFT": 9,
            "RIGHT": 10,
        },
        "MOVE": {
            "LEFT": 11,
            "RIGHT": 12,
        }
    },
    "HEAD": {
        "OBLIQUE": 13,
        "DOWN": 14,
        "RIGHT": 15
    }
}

ARCHERY = {
    "SHOOT": 65
}

OBSTACLERUN = {
    "STEP": {
        "FIRST": 75,   # 100
        "LAST": 77,    # 102
    },
    "WALK": 76,    # 101
    "MOVE": {
        "LEFT": 78,    # 103
        "RIGHT": 79    # 104
    },
    "HEAD": {
        "DOWN": 70,
        "OBLIQUE": 71,
        "UP": 72,
        "LEFT": 73,
        "RIGHT": 74,
        "REDUP": 87
    },
    "TURN":{
        "LEFT": 80,    # 103
        "RIGHT": 81    # 104
    },
    "WALKLEFT": 82,
    "WALKRIGHT": 83,
    "CRAWL":{
        "INIT": 84,
        "KNEEL": 85,
        "CRAWL": 86,
        "CRAWLSHORT": 89,
    }
}


BASKETBALL = {
    "INIT": {
        "DOWN": 16,
        "UP": 17
    },
    "STRAIGHT": {
        "DOWN": 18,
        "UP": 19
    },
    "BALL": {
        "PICKUP": 24,
        "GOAL": 26
    },
    "LEFTSTEP": {
        "DOWN": 29,
        "UP": 31
    },
    "RIGHTSTEP": {
        "DOWN": 30,
        "UP": 32
    },
    "LEFTTURN": {
        "DOWN": 35,
        "UP": 37
    },
    "RIGHTTURN": {
        "DOWN": 34,
        "UP": 36
    },
    "SHORTWALK": {
        "DOWN": 43,
        "UP": 44
    },
    "WALKSTART": {
        "DOWN": 20,
        "UP": 21
    },
    "WALKFINISH": {
        "DOWN": 22,
        "UP": 23
    },
    "CHECK": {
        "LEFT_D": 46,
        "RIGHT_D": 45,
        "DOWN": 47,
        "RIGHT_U": 48,
        "LEFT_U": 49
    }

}


class Motion:
    def __init__(self):
        self.uart = serial.Serial('/dev/ttyAMA0', 57600, timeout=0.001)
        self.uart.flush()
        self.config = {
            "flag": 0,
            "direction": 0,
            "finish": 0
        }
        self.thread = None
        self.trip = [False, -1]
        pass

    def action(self, data):
        # while self.do:
        #     pass
        line = [0, 0, 0, 0, 0, 0]
        try:
            # if self.uart.inWaiting() > 0:
            #     self.uart.read(1)

            low = data
            high = 0
            if low > 255:
                high = low - 255
                low -= 255
                if high > 255:
                    high = 0

            b = [b'\xff', b'U', bytes([low]), bytes([255 - low]), bytes([high]), bytes([255 - high])]

            for item in b:
                self.uart.write(item)
                # print(item)
            # print("보냄")
        finally:
            pass

        try:
            while True:
                if self.uart.inWaiting() > 0:
                    tmp = self.uart.read(1)
                    if tmp == b'\x12':
                        # print("왔음")
                        return
                        # line[0] = tmp
                        # for i in range(1, 6):
                        #     line[i] = self.uart.read(1)
                        # rString = self.integerToBytes(line)
                        # print(rString)

                        # state, r = self.action(199)
                        # state   : True (넘어짐)
                        # r -1    : 정상
                        # r 1     : 앞으로 넘어짐
                        # r 2     : 뒤로 넘어짐
                        #
                        # if line[2] == b'\x12':
                        #     return False, -1
                        # elif line[2] == b'\x13':
                        #     return True, 1
                        # elif line[2] == b'\x14':
                        #     return True, 2
            pass
        finally:
            pass

    def integerToBytes(self, line):
        return "\t".join(str(int.from_bytes(b, byteorder='big', signed=True)) for b in line)

    def setConfig(self, flag, direction):
        self.config = {
            "flag": flag,
            "direction": direction
        }
        pass

    def first_init(self):
        self.action(SPRINT["INIT"])
        pass

    def walk_init(self):
        self.action(SPRINT["W_INIT"])
        pass

    def walk_straight(self, flag):
        self.action(SPRINT["F" if flag == 0 else "B"]["STRAIGHT"])
        pass

    def walk_left(self, flag):
        self.action(SPRINT["F" if flag == 0 else "B"]["LEFT"])
        pass

    def walk_right(self, flag):
        self.action(SPRINT["F" if flag == 0 else "B"]["LEFT"])
        pass

    def walk_finish(self):
        self.action(SPRINT["FINISH"])
        pass

    def test_walk_s(self):
        self.action(SPRINT["F"]["STRAIGHT"])
        pass

    def test_walk_l(self):
        self.action(SPRINT["F"]["LEFT"])
        pass

    def test_walk_r(self):
        self.action(SPRINT["F"]["RIGHT"])
        pass

    # flag, direction, finish
    def threadWalk(self):
        #self.walk_init()
        t = threading.currentThread()

        self.trip = [False, -1]

        while getattr(t, "run", True):
            local_config = self.config
            flag = local_config["flag"]
            direction = local_config["direction"]

            if flag == 0:
                if direction == 0:
                    # self.action(5)
                    # self.action(6)
                    mn = 5
                elif direction == 1:
                    # self.action(11)
                    # self.action(12)
                    mn = 11
                elif direction == 2:
                    # self.action(13)
                    # self.action(14)
                    mn = 13
            elif flag == 1:
                if direction == 0:
                    # self.action(9)
                    # self.action(10)
                    mn = 9
                elif direction == 1:
                    mn = 100
                elif direction == 2:
                    mn = 102
                # elif direction == 1:
                #     mn = SPRINT["B"]["LEFT"]
                # elif direction == 2:
                #     mn = SPRINT["B"]["RIGHT"]
            self.action(mn)
            self.action(mn + 1)
            # self.trip = self.action(mn)
            # if self.trip[0]:
            #     break
            pass

        pass

    #################
    #  BASKETBALL  #
    #################
    def bb_init(self, flag):
        self.action(BASKETBALL["INIT"]["DOWN" if flag == 0 else "UP"])
        pass

    def bb_walk(self, flag):
        self.action(BASKETBALL["STRAIGHT"]["DOWN" if flag == 0 else "UP"])
        pass

    def bb_ball(self, flag):
        self.action(BASKETBALL["BALL"]["PICKUP" if flag == 0 else "GOAL"])
        pass

    def bb_leftstep(self, flag):
        self.action(BASKETBALL["LEFTSTEP"]["DOWN" if flag == 0 else "UP"])
        pass

    def bb_rightstep(self, flag):
        self.action(BASKETBALL["RIGHTSTEP"]["DOWN" if flag == 0 else "UP"])
        pass

    def bb_leftturn(self, flag):
        self.action(BASKETBALL["LEFTTURN"]["DOWN" if flag == 0 else "UP"])
        pass

    def bb_rightturn(self, flag):
        self.action(BASKETBALL["RIGHTTURN"]["DOWN" if flag == 0 else "UP"])
        pass

    def bb_shortwalk(self, flag):
        self.action(BASKETBALL["SHORTWALK"]["DOWN" if flag == 0 else "UP"])
        pass

    def bb_walkstart(self, flag):
        self.action(BASKETBALL["WALKSTART"]["DOWN" if flag == 0 else "UP"])
        pass

    def bb_walkfinish(self, flag):
        self.action(BASKETBALL["WALKFINISH"]["DOWN" if flag == 0 else "UP"])
        pass

    def bb_checkdown(self):
        self.action(BASKETBALL["CHECK"]["DOWN"])
        pass

    def bb_checkleft(self, flag):
        self.action(BASKETBALL["CHECK"]["LEFT_D" if flag == 0 else "LEFT_U"])
        pass

    def bb_checkright(self, flag):
        self.action(BASKETBALL["CHECK"]["RIGHT_D" if flag == 0 else "RIGHT_U"])
        pass

    #################
    # WEIGHTLIFTING #
    #################
    def wl_first_step(self):
        self.action(WEIGHTLIFTING["INIT"])
        return 1

    def wl_walk(self, flag):
        self.action(WEIGHTLIFTING["BASIC" if flag == 0 else ("LOW" if flag == 1 else "HIGH")]["WALK"])
        return 1

    def wl_turn(self, flag, dire):
        self.action(WEIGHTLIFTING["BASIC" if flag == 0 else ("LOW" if flag == 1 else "HIGH")]["TURN"][
                        "LEFT" if dire == 1 else "RIGHT"])
        return 1

    def wl_move(self, flag, dire):
        self.action(WEIGHTLIFTING["BASIC" if flag == 0 else ("LOW" if flag == 1 else "HIGH")]["MOVE"][
                        "LEFT" if dire == 1 else "RIGHT"])
        return 1

    def wl_lift_low(self):
        self.action(WEIGHTLIFTING["LOW"]["LIFT"])
        return 1

    def wl_head(self, flag):
        self.action(WEIGHTLIFTING["OBLIQUE" if flag == 0 else ("DOWN" if flag == 1 else "RIGHT")])
        return 1

    def wl_lift_high(self):
        self.action(WEIGHTLIFTING["HIGH"]["LIFT"])
        return 1

    #################
    #    ARCHERY    #
    #################

    # def a_pull(self):
    #     self.action(ARCHERY["PULL"])
    #     return 1

    def a_shoot(self):
        self.action(ARCHERY["SHOOT"])
        return 1

    #################
    #  OBSTACLERUN  #
    #################

    #################
    #  OBSTACLERUN  #
    #################
    def ob_walk(self, repeat):
        self.action(OBSTACLERUN["STEP"]["FIRST"])
        for i in range(repeat):
            self.action(OBSTACLERUN["WALKLEFT"])
            self.action(OBSTACLERUN["WALKRIGHT"])
        self.action(OBSTACLERUN["STEP"]["LAST"])
        return 1

    def ob_startThread(self):

        if self.isThreadRun():
            self.stopThread()
            pass

        callback = self.ob_threadWalk

        self.thread = threading.Thread(target=callback)
        self.thread.start()
        pass

    def ob_threadWalk(self):
        self.action(OBSTACLERUN["STEP"]["FIRST"])
        t = threading.currentThread()

        while getattr(t, "run", True):
            self.action(OBSTACLERUN["WALKLEFT"])
            self.action(OBSTACLERUN["WALKRIGHT"])
            pass
        pass

    def ob_stopThread(self):
        if not self.isThreadRun():
            return
        #print("쓰레드 끝!")
        self.thread.run = False
        self.thread.join()
        self.thread = None

        self.action(OBSTACLERUN["STEP"]["LAST"])
        pass

    def ob_head(self, direction):
        if direction == 0:
            self.action(OBSTACLERUN["HEAD"]["OBLIQUE"])
        elif direction == 1:
            self.action(OBSTACLERUN["HEAD"]["UP"])
        elif direction == 2:
            self.action(OBSTACLERUN["HEAD"]["LEFT"])
        elif direction == 3:
            self.action(OBSTACLERUN["HEAD"]["RIGHT"])
        elif direction == 4:
            self.action(OBSTACLERUN["HEAD"]["DOWN"])
        elif direction == 5:
            self.action(OBSTACLERUN["HEAD"]["REDUP"])
        return 1

    def ob_move(self, direction):
        if direction == 2:
            self.action(OBSTACLERUN["MOVE"]["LEFT"])
        elif direction == 3:
            self.action(OBSTACLERUN["MOVE"]["RIGHT"])
        return 1

    def ob_crawl(self):
        self.action(OBSTACLERUN["CRAWL"]["INIT"])
        self.action(OBSTACLERUN["CRAWL"]["KNEEL"])
        self.action(OBSTACLERUN["CRAWL"]["CRAWL"])
        return 1

    def ob_crawl_short(self):
        self.action(OBSTACLERUN["CRAWL"]["INIT"])
        self.action(OBSTACLERUN["CRAWL"]["KNEEL"])
        self.action(OBSTACLERUN["CRAWL"]["CRAWLSHORT"])
        return 1

    def attach(self, scope):
        # TODO: call attach motion
        pass

    def stable(self):
        # TODO: call stable motion
        pass

    def startThread(self):
        if self.isThreadRun():
            self.stopThread()
            pass

        callback = self.threadWalk

        self.thread = threading.Thread(target=callback)
        self.thread.start()
        pass

    def stopThread(self):
        if not self.isThreadRun():
            return

        self.thread.run = False
        self.thread.join()
        self.thread = None
        self.setConfig(1,0)

        pass

    def isThreadRun(self):
        return self.thread is not None


if __name__ == '__main__':
    robot = Motion()
    robot.action(21)
    for _ in range(20):
        robot.action(53)
        robot.action(54)
    #robot.action(7)
    # time.sleep(1)
    # for _ in range(20):
    #     robot.action(11)
    #     robot.action(12)

    # robot.action(7)
