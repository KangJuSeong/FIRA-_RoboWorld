from enum import Enum


####################################
#            M O T I O N           #
####################################

# INIT-- OB, UP, DOWN

# WALK--+
#       | SLOW - START, L2R, R2L, END
#       | FAST - START, L2R, R2L, END
#

# MOVE--+
#       | LONG - LEFT, RIGHT
#       | SHORT - LEFT, RIGHT

# TURN--+
#       | LONG - LEFT, RIGHT
#       | SHORT - LEFT, RIGHT

# ATTACH
####################################

class ACTION(Enum):
    WALK = 0
    MOVE = 1
    TURN = 2
    INIT = 3


class HEAD(Enum):
    DOWN = 0
    OBSTACLE = 1
    UP = 2


class DIRECTION(Enum):
    LEFT = 0
    RIGHT = 1


class GO(Enum):
    FRONT = 0
    BACK = 1


class SPEED(Enum):
    SLOW = 0
    FAST = 1


class SCOPE(Enum):
    SHORT = 0
    LONG = 1


class STATUS(Enum):
    FAIL = 0
    SUCCESS = 18


class COLOR(Enum):
    RED = 0
    GREEN = 1
    WHITE = 2
