from library.motion import Motion
from library.image_processor import ImageProcessor

# from games.sprint import Sprint
from games.weightLifting import WeightLifting
from games.archery import Archery
from games.obstacleRun import ObstacleRun
from games.basketball import BasketBall
from games.sprintT import Sprint


if __name__ == '__main__':
    robot = Motion()
    while True:
        if robot.uart.inWaiting() > 0:
            tmp = robot.uart.read(1)
            if tmp == b'\x12':
                print("시작!")
                break
    # ip = ImageProcessor()
    # game = Archery(robot,ip)
    # game.run()
    # game = BasketBall(robot)
    # game.run()

    # game = Sprint(robot)
    # game.run()

    # game = WeightLifting(robot, ip)

    # game.run()

    # game = Archery(robot, ip)
    # game.run()
    ip = ImageProcessor()
    game = ObstacleRun(robot, ip)
    game.run()
