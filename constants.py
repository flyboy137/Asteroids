from pyray import *
from raylib import *
from math import atan2, radians, sin, cos, degrees
from random import uniform, randint, choice
import os, csv

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
MAX_LEVEL = 6
BKG_COLOR = (0,0,0)


# Player
PLAYER_ROTATE_SPEED = 100
PLAYER_MOVE_SPEED = 100
PLAYER_MAX_SPEED = 500
PLAYER_ANIM_SPEED = 8

# Textures
SHIP_txtr = 'images/ship.png'
BULLET_txtr = 'images/bullet.png'

# Bullet
BULLET_SPEED = 800

# Saucer
SAUCER_txtr = 'images/saucer.png'
SAUCER_BULLET_txtr = 'images/saucer_bullet.png'
SAUCER_speed = 150
SAUCER_BULLET_SPEED = 400
SAUCER_ANIM_SPEED = 10

# Scoring
INIT_VALUE = 3
MAX_LIVE = 5
MAX_HYPJ = 5
LIVE_BONUS = 10000  # add one live every 10000
HYPJ_BONUS = 5000   # add one hyper jump every 5000

# Asteroid texture dictionary
ASTEROID_MOVE_SPEED = [5,50]
ASTEROID_ROT_SPEED = [-100,100]
ASTEROID_ANGLE = [0, 359]
ASTEROID_TEXTURE_DICT = {
    1:['images/asteroids/astr_01_1.png','images/asteroids/astr_01_2.png','images/asteroids/astr_01_3.png'],
    2:['images/asteroids/astr_02_1.png','images/asteroids/astr_02_2.png','images/asteroids/astr_02_3.png'],
    3:['images/asteroids/astr_03_1.png','images/asteroids/astr_03_2.png','images/asteroids/astr_03_3.png'],
    4:['images/asteroids/astr_04_1.png','images/asteroids/astr_04_2.png','images/asteroids/astr_04_3.png']
}

# Large asteroid = 20, Medium = 50, Small = 100, Saucer = 1000
SCORE_LIST = [20, 50, 100, 1000]
ASTEROID_ANIM_SPEED = 10

# No SPawn Area, size = 150 x 150 pixels
NSPA_LEFT = SCREEN_WIDTH / 2 - 150
NSPA_RIGHT = SCREEN_WIDTH / 2 + 150
NSPA_TOP = SCREEN_HEIGHT / 2 - 150
NSPA_BOTTOM = SCREEN_HEIGHT / 2 + 150



