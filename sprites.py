
from constants import *

class Sprite:
    def __init__(self, texture, pos, rot_speed, move_speed):
        self.texture = texture
        self.pos = pos
        self.rot_speed = rot_speed
        self.move_speed = move_speed
        self.angle = 0
        self.direction = 0
        self.size = Vector2(texture.width, texture.height)
        self.center = Vector2(self.size.x // 2, self.size.y // 2)
        self.source_rect = Rectangle(0, 0, self.size.x, self.size.y)

        self.radius = self.size.y / 2
        self.remove = False

    def dest_rect(self):
        return Rectangle(self.pos.x, self.pos.y, self.size.x, self.size.y)

    def wrap_screen(self):
        self.pos.x = 0 if self.pos.x > SCREEN_WIDTH else (SCREEN_WIDTH
        if self.pos.x < 0 else self.pos.x)

        self.pos.y = 0 if self.pos.y > SCREEN_HEIGHT else (SCREEN_HEIGHT
        if self.pos.y < 0 else self.pos.y)

    def move(self, dt):
        self.pos.x += cos(radians(self.direction)) * self.move_speed * dt
        self.pos.y += sin(radians(self.direction)) * self.move_speed * dt

    def check_outbound(self):
        self.remove = self.pos.x < 0 or self.pos.x > SCREEN_WIDTH or \
                      self.pos.y < 0 or self.pos.y > SCREEN_HEIGHT

    def update(self, dt):
        self.move(dt)
        self.check_outbound()

    def draw(self):
        #draw_texture_v(self.texture, self.pos, WHITE)
        draw_texture_pro(self.texture, self.source_rect, self.dest_rect(),
                         self.center, self.angle, WHITE)


class Player(Sprite):
    def __init__(self, texture, pos, player_bullet, hyper_jump):
        super().__init__(texture, pos, PLAYER_ROTATE_SPEED, PLAYER_MOVE_SPEED)
        self.player_bullet = player_bullet
        self.hyper_jump = hyper_jump
        self.move_speed = 0
        self.active = True
        self.is_hit = False
        self.lives = 5
        self.hypj_bonus = 0
        self.live_bonus = 0

    def input(self, dt):
        if is_key_down(KEY_UP):
            self.direction = self.angle - 90   # ship face up so -90
            self.move_speed += PLAYER_MOVE_SPEED * dt
        else:
            self.move_speed -= 35 * dt
            self.move_speed = max(0, min(self.move_speed, PLAYER_MAX_SPEED))

        if is_key_pressed(KEY_DOWN):
           self.hyper_jump()

        if is_key_pressed(KEY_SPACE):
           self.player_bullet(self.pos, self.center, self.angle - 90)

        if is_key_down(KEY_LEFT) or is_key_down(KEY_RIGHT):
           self.angle += (int(is_key_down(KEY_RIGHT)) - int(is_key_down(KEY_LEFT))) * PLAYER_ROTATE_SPEED  * dt
           self.angle %= 360

    def reset(self):
        self.pos = Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.angle, self.move_speed, self.rot_speed = 0, 0, 0
        self.active = True
        self.is_hit = False

    def crash(self):
        self.active = False
        self.is_hit = True
        self.lives -= 1
        self.hypj_bonus = 0
        self.live_bonus = 0

    def update(self, dt):
        self.input(dt)
        self.move(dt)
        self.wrap_screen()


class Bullet(Sprite):
    def __init__(self, texture, pos, center, angle):
        super().__init__(texture, pos, 0, BULLET_SPEED)

        # Calculate bullet spawn position
        offset_x = sin(radians(angle) * center.y)
        offset_y = cos(radians(angle) * center.y)

        self.pos = Vector2(pos.x + offset_x, pos.y + offset_y)
        self.direction = angle

class Asteroid(Sprite):
    def __init__(self, texture, pos, txtr_dict, txtr_index, level, new_level):
       super().__init__(texture, pos, rot_speed=uniform(*ASTEROID_ROT_SPEED),
                         move_speed=uniform(*ASTEROID_MOVE_SPEED)*level)

       self.angle = uniform(*ASTEROID_ANGLE)

       # txtr_dict is the key of the asteroid texture dictionary
       # txtr_index is the value of the texture index
       self.txtr_dict = txtr_dict
       self.txtr_index = txtr_index

       # create Asteroid but prevent them to spawn inside player ship area
       # only apply to new level when the game start
       if new_level:
          self.pos = self.get_spawn_loc()
       else:
          self.pos = pos

       self.direction = self.angle

    def get_spawn_loc(self):
        x = uniform(0, SCREEN_WIDTH - self.size.x)
        y = uniform(0, SCREEN_HEIGHT - self.size.y)

        if x <= SCREEN_WIDTH/2 and x + self.size.x > NSPA_LEFT:
            x = NSPA_LEFT - self.size.x
        elif x > SCREEN_WIDTH/2 and x + self.size.x < NSPA_RIGHT:
            x = NSPA_RIGHT

        if y <= SCREEN_HEIGHT/2 and y + self.size.y > NSPA_TOP:
            y = NSPA_TOP - self.size.y
        elif y > SCREEN_HEIGHT/2 and y < NSPA_BOTTOM:
            y = NSPA_BOTTOM

        return Vector2(x, y)

    def update(self, dt):
        self.angle += self.rot_speed * dt
        self.angle %= 360.0
        self.move(dt)
        self.wrap_screen()

class Animation:
    def __init__(self, textures, pos, speed):
        self.textures = textures
        self.size = Vector2(textures[0].width, textures[0].height)
        # get the center of the texture
        self.pos = Vector2(pos.x - self.size.x // 2, pos.y - self.size.y // 2)

        self.frame = 0
        self.remove = False
        self.speed = speed


    def update(self, dt):
        if self.frame < len(self.textures) - 1:
            self.frame += self.speed * dt
        else:
            self.remove = True

    def draw(self):
        draw_texture_v(self.textures[int(self.frame)], self.pos, WHITE)


class Saucer:
    def __init__(self, texture, pos, direction, saucer_bullet):
        self.texture = texture
        self.pos = pos
        self.direction = direction
        self.size = Vector2(self.texture.width, self.texture.height)
        self.center = Vector2(self.size.x//2, self.size.y//2)
        self.remove = False
        self.saucer_bullet = saucer_bullet
        self.shoot = 1

    def update(self, dt):

        self.pos.x += self.direction * SAUCER_speed * dt
        # amplitude = height of the sine wave
        # frequency = how fast the wave oscillates
        #  y = y + amplitude * sin(frequency * x position)
        self.pos.y = self.pos.y + 0.05  * sin(self.pos.x * 0.02)
        self.remove = self.pos.x < -200 or self.pos.x > SCREEN_WIDTH + 200

        # shoot bullet to player ship
        self.shoot -= 1
        if self.shoot <= 0:
           self.shoot = 3   # delay shooting bullet a little bit
           if randint(-10000, 10000) > 9998:
              self.saucer_bullet(self.pos, self.center)

    def draw(self):
        draw_texture_v(self.texture, self.pos, WHITE)


class Saucer_bullet(Sprite):
    def __init__(self, texture, saucer_pos, saucer_center, player_pos,player_center, speed):
        super().__init__(texture, Vector2(), rot_speed=0, move_speed=speed)

        self.move_speed = speed

        player_center_pos = Vector2(player_pos.x + player_center.x,
                                    player_pos.y + player_center.y)

        self.pos = Vector2(saucer_pos.x + saucer_center.x,
                   saucer_pos.y + saucer_center.y)

        # calculate angle between bullet and player
        x = player_center_pos.x - self.pos.x
        y = player_center_pos.y - self.pos.y
        self.angle = degrees(atan2(y,x))
        self.direction = self.angle

















