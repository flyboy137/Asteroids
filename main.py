
from constants import *
from sprites import Player, Bullet, Asteroid, Animation, Saucer, Saucer_bullet
from Timer import Timer
from menu import Intro, Manual, Game_over, Top_ten, Display_top_ten

class Game:
    def __init__(self):

        init_window(SCREEN_WIDTH, SCREEN_HEIGHT, 'Asteroid')
        init_audio_device()

        self.font_dict = {
            'font1': load_font_ex('font/Disket-Mono-Regular.ttf', 32, ffi.NULL, 0),
            'font2' : load_font_ex('font/ChargeVector.otf', 36, ffi.NULL, 0)
        }

        self.animation_dict = {
            # 1:asteroid explosion, 2:player ship explosion, 3:saucer explosion, 4:hyper jump, 5:game over
            1: [load_texture('images/animations/asteroid/' f'a_exp_{i}.png') for i in range(1, 8)],
            2: [load_texture('images/animations/ship/' f's_exp_{i}.png') for i in range(1, 9)],
            3: [load_texture('images/animations/saucer/' f'saur_{i}.png') for i in range(1, 7)],
            4: [load_texture('images/animations/hyper_jump/' f'hyper_jump_{i}.png') for i in range(1, 20)],
            5: [load_texture('images/animations/game_over' f'/go_{i}.png') for i in range(1,16)],
        }

        self.audio_dict = {
            'slow': load_sound('audio/slow.mp3'),
            'medium': load_sound('audio/medium.mp3'),
            'fast': load_sound('audio/fast.mp3'),
            'player_shoot': load_sound('audio/player_shoot.mp3'),
            'split' : load_sound('audio/split.mp3'),
            'explosion' : load_sound('audio/explosion.mp3'),
            'hyper_jump' : load_sound('audio/hyper_jump.mp3'),
            'saucer_move' : load_sound('audio/saucer_move.mp3'),
            'saucer_shoot' : load_sound('audio/saucer_shoot.mp3'),
            'game_over' : load_sound('audio/game_over.mp3')
        }

        self.small_ship = load_texture('images/small_ship.png')
        self.small_hypj = load_texture('images/small_hyper_jump.png')


        self.level, self.score = 0, 0

        self.intro = Intro(load_texture('images/intro.png'), self.center_text_pos,
                           self.font_dict['font2'], 36)

        self.manual = Manual(load_texture('images/manual.png'))
        self.manual_on = False

        # Background music
        self.bgm = self.audio_dict['slow']

        self.total_astrs = 0

        # Player and Bullet
        self.player = Player(load_texture(SHIP_txtr), Vector2(SCREEN_WIDTH // 2,
                             SCREEN_HEIGHT // 2), self.player_bullet, self.hyper_jump)

        self.player.lives = 0

        self.bullet_list, self.asteroid_list, self.explosion_list = [],[],[]
        self.saucer_list, self.saucer_bullet_list = [],[]

        # Hyper jump
        self.hyper_jump = None
        self.hyper_jump_active = None
        self.hyper_jump_count = 0
        self.hyper_jump_size = Vector2(self.animation_dict[4][0].width, self.animation_dict[4][0].height)
        self.hyper_jump_radius = self.animation_dict[4][0].height / 2
        self.hyper_jump_pos = Vector2()

        # Saucer
        self.saucer_time = Timer(30, self.saucer)

        # Game over and Top 10
        self.game_over_animation = Game_over(self.animation_dict[5], self.audio_dict['game_over'],
                                             self.font_dict['font2'], 36, self.center_text_pos)


        # game state:
        # 1 = normal, 2 = level clear, 3 = game over, 4 = input name, 5 = intro
        self.game_state = 5

        # Top 10
        self.display_tp = Display_top_ten(self.font_dict['font1'], 32, self.font_dict['font2'], 36,
                                          self.center_text_pos, load_texture('images/top_ten_box.png'))

        self.display_tp_on = False

        self.top_ten = Top_ten(self.font_dict['font1'], 36, self.font_dict['font2'], 36, self.center_text_pos)
        # Read the file and store data to the list for top ten list displaying
        # and checking whether the player's score has reached top ten.
        self.top_ten_list = self.top_ten.read_file()
        # get high score
        self.high_score = int(self.top_ten_list[0][1])

        # Init and setup
        self.init()

    def init(self):
        self.level = 1
        self.score = 0
        self.player.lives =  INIT_VALUE
        self.hyper_jump_count = INIT_VALUE

        self.player.hypj_bonus = 0
        self.player.live_bonus = 0

        self.game_over_animation.frame = 1
        self.total_astrs = 0

        self.setup()

    def setup(self):
        if self.game_state < 3:
            self.clear_list()

            self.hyper_jump_active = False


            if self.game_state == 2:
               self.level = min(self.level+1, MAX_LEVEL)
               self.game_state = 1     # reset to normal

            self.player.reset()

            if self.level > 3:    # saucer spawn start from level 4
               self.saucer_time.start()

            # create new Asteroid list
            # prevent them to spawn inside the restricted area
            self.total_astrs = 0
            for i in range(1, (10 + self.level)):   #10 + self.level
                dict = randint(1,4)   # get a random texture from the dict
                index = 0             # index of the texture name list
                self.asteroid_list.append(Asteroid(load_texture(ASTEROID_TEXTURE_DICT[dict][0]),
                Vector2(), dict, index, self.level, True))

                # calculate total smallest asteroids in the list
                self.total_astrs += 4

    def center_text_pos(self, text, font, size, space, pos_y):
        size = measure_text_ex(font, text, size, space)
        return Vector2(SCREEN_WIDTH // 2 - size.x // 2, pos_y)

    def clear_list(self):
        self.bullet_list.clear()
        self.asteroid_list.clear()
        self.explosion_list.clear()
        self.saucer_list.clear()
        self.saucer_bullet_list.clear()
        stop_sound(self.audio_dict['saucer_move'])
        stop_sound(self.bgm)
        self.saucer_time.stop()

    def player_bullet(self, pos, center, angle):
        self.bullet_list.append(Bullet(load_texture(BULLET_txtr), pos, center, angle))
        play_sound(self.audio_dict['player_shoot'])

    def saucer_bullet(self, pos, center):
        # shoot bullet to player
        self.saucer_bullet_list.append(Saucer_bullet(load_texture(SAUCER_BULLET_txtr),
                                       pos, center, self.player.pos, self.player.center,
                                       SAUCER_BULLET_SPEED))
        play_sound(self.audio_dict['saucer_shoot'])

    def hyper_jump(self):
        if not self.hyper_jump_active and self.hyper_jump_count > 0:
           play_sound(self.audio_dict['hyper_jump'])

           self.hyper_jump_active = True
           self.hyper_jump_count -= 1

           pos_x = uniform(0, SCREEN_WIDTH  - self.hyper_jump_size.x)
           pos_y = uniform(0, SCREEN_HEIGHT - self.hyper_jump_size.y)

           # get hyper jump topleft position for collision checking
           self.hyper_jump_pos = Vector2(pos_x,pos_y)
           self.hyper_jump = Animation(self.animation_dict[4],self.hyper_jump_pos,15)

           # move player ship inside the hyper_jump ring
           self.player.active = False
           self.player.pos = self.hyper_jump_pos
           self.player.move_speed = 0


    def collisions(self):
        # hyper_jump vs asteroid, saucer and saucer bullet
        # remove any asteroids within the ring
        if self.hyper_jump_active:
            for asteroid in self.asteroid_list:
                if check_collision_circles(self.hyper_jump_pos, self.hyper_jump_radius, asteroid.pos, asteroid.radius):
                    asteroid.remove = True

            for sprite in self.saucer_list + self.saucer_bullet_list:
                if check_collision_circle_rec(self.hyper_jump_pos, self.hyper_jump_radius,
                Rectangle(sprite.pos.x, sprite.pos.y, sprite.size.x, sprite.size.y)):
                    sprite.remove = True
                    stop_sound(self.audio_dict['saucer_move'])

        # bullet vs asteroid and saucer
        for bullet in self.bullet_list:
            for asteroid in self.asteroid_list:
               if check_collision_circles(bullet.pos, bullet.radius, asteroid.pos, asteroid.radius) and \
               not asteroid.remove:

                  bullet.remove, asteroid.remove = True, True
                  self.score += SCORE_LIST[asteroid.txtr_index]
                  self.player.hypj_bonus += SCORE_LIST[asteroid.txtr_index]
                  self.player.live_bonus += SCORE_LIST[asteroid.txtr_index]

                  # next asteroid style
                  if asteroid.txtr_index + 1 <= 2:
                     play_sound(self.audio_dict['split'])
                     asteroid.txtr_index += 1

                     # split to two smaller asteroids
                     pos = Vector2(asteroid.pos.x-4, asteroid.pos.y-4)
                     self.asteroid_list.append(Asteroid(load_texture(ASTEROID_TEXTURE_DICT \
                     [asteroid.txtr_dict][asteroid.txtr_index]),pos, asteroid.txtr_dict,
                     asteroid.txtr_index, self.level, False))

                     pos = Vector2(asteroid.pos.x+4, asteroid.pos.y+4)
                     self.asteroid_list.append(Asteroid(load_texture(ASTEROID_TEXTURE_DICT \
                     [asteroid.txtr_dict][asteroid.txtr_index]), pos, asteroid.txtr_dict,
                     asteroid.txtr_index, self.level, False))
                  else:
                     play_sound(self.audio_dict['explosion'])
                     self.explosion_list.append(Animation(self.animation_dict[1], asteroid.pos, ASTEROID_ANIM_SPEED))

            for saucer in self.saucer_list:
               if check_collision_circle_rec(bullet.pos,bullet.radius,
               Rectangle(saucer.pos.x,saucer.pos.y,saucer.size.x,saucer.size.y)) \
               and not saucer.remove:
                   bullet.remove, saucer.remove = True, True
                   play_sound(self.audio_dict['explosion'])
                   stop_sound(self.audio_dict['saucer_move'])

                   # saucer explosion animation
                   self.explosion_list.append(Animation(self.animation_dict[3], saucer.pos, SAUCER_ANIM_SPEED))
                   self.score += SCORE_LIST[-1]
                   self.player.hypj_bonus += SCORE_LIST[-1]
                   self.player.live_bonus += SCORE_LIST[-1]

        # asteroid vs player ship
        for asteroid in self.asteroid_list:
           if check_collision_circles(self.player.pos, self.player.radius, asteroid.pos, asteroid.radius) \
           and not self.player.is_hit and self.player.active:
               play_sound(self.audio_dict['explosion'])
               self.explosion_list.append(Animation(self.animation_dict[2], self.player.pos, PLAYER_ANIM_SPEED))
               self.player.crash()
               self.hypj_bonus = 0
               self.live_bonus = 0

        # saucer, saucer bullet vs player ship
        for sprite in self.saucer_list + self.saucer_bullet_list:
           if check_collision_circle_rec(self.player.pos, self.player.radius,
           Rectangle(sprite.pos.x, sprite.pos.y, sprite.size.x, sprite.size.y)) and \
           not self.player.is_hit and self.player.active:
               play_sound(self.audio_dict['explosion'])
               if sprite in self.saucer_bullet_list: sprite.remove = True
               self.explosion_list.append(Animation(self.animation_dict[2], self.player.pos, PLAYER_ANIM_SPEED))
               self.player.crash()

        if self.player.lives <= 0: self.game_state = 3   # game over

    def scoring(self):
        if self.score > 9999999 : self.score = 9999999
        if self.player.hypj_bonus >= HYPJ_BONUS:
           if self.hyper_jump_count < MAX_HYPJ:
               self.hyper_jump_count += 1
           self.player.hypj_bonus = 0

        if self.player.live_bonus >= LIVE_BONUS:
           if self.player.lives < MAX_LIVE:
              self.player.lives += 1
           self.player.live_bonus = 0

        draw_text_ex(self.font_dict['font2'],f'{self.score:07}',Vector2(4,9),36,4, (255,255,255,128))
        pos = self.center_text_pos("00", self.font_dict['font2'], 48, 0, 9)
        draw_text_ex(self.font_dict['font2'],f'{len(self.asteroid_list):02}', pos,36,4,(255,255,255,128))

        for i in range(self.player.lives):
            draw_texture_v(self.small_ship, Vector2(i*35, 53), (255,255,255,128))
        for i in range(self.hyper_jump_count):
            draw_texture_v(self.small_hypj, Vector2(i*35, 90), (255,255,255,128))

    def remove_sprites(self):
        self.bullet_list = [bullet for bullet in self.bullet_list if not bullet.remove]
        self.asteroid_list = [asteroid for asteroid in self.asteroid_list if not asteroid.remove]
        self.explosion_list = [explosion for explosion in self.explosion_list if not explosion.remove]
        self.saucer_list = [saucer for saucer in self.saucer_list if not saucer.remove]
        self.saucer_bullet_list = [bullet for bullet in self.saucer_bullet_list if not bullet.remove]

        # reset player to active when hyper_jump is finished
        if self.hyper_jump_active and self.hyper_jump.remove:
           self.hyper_jump = None
           self.hyper_jump_active = False
           self.player.active = True

    def saucer(self):
        pos = Vector2(choice([-120, SCREEN_WIDTH]),randint(100, SCREEN_HEIGHT - 100))
        direction = 1 if pos.x < 0 else -1
        self.saucer_list.append(Saucer(load_texture(SAUCER_txtr), pos, direction, self.saucer_bullet))
        play_sound(self.audio_dict['saucer_move'])

    def change_bgm(self):
        # change bgm to slow, medium or fast base on
        # how many asteroid remaining
        astr_remain = 0
        for asteroid in self.asteroid_list:
            if asteroid.txtr_index == 0:
                astr_remain += 4
            elif asteroid.txtr_index == 1:
                astr_remain += 2
            else:
                astr_remain += 1

        percentage = (astr_remain / self.total_astrs) * 100

        if percentage > 50:
            self.bgm = self.audio_dict['slow']
        elif percentage <= 50 and percentage > 20:
            self.bgm = self.audio_dict['medium']
        else:
            self.bgm = self.audio_dict['fast']

    def update(self):
        dt = get_frame_time()
        if not self.manual_on and not self.display_tp_on:
            if not is_sound_playing(self.bgm) and self.game_state < 3:
               play_sound(self.bgm)

            self.remove_sprites()

            [sprite.update(dt)
              for sprite in self.bullet_list + self.asteroid_list + self.explosion_list+ \
              self.saucer_bullet_list + self.saucer_list
            ]

            if self.game_state < 3:
                if self.player.active: self.player.update(dt)
                if self.hyper_jump_active: self.hyper_jump.update(dt)

                self.saucer_time.update()

                # check collision
                self.collisions()
                self.change_bgm()

                # level clear
                if self.asteroid_list == []:
                   self.game_state = 2
                   self.setup()

                # if player is hit, let explosion animation completed first
                if self.player.is_hit and self.explosion_list == []:
                   self.setup()

            if self.game_state == 3:
               # game over
               if self.explosion_list == []:
                  self.clear_list()

                  # play game over animation
                  if self.game_over_animation.update(dt):
                     poll_input_events()  # clear key queue
                     # input player's name
                     # if player score reached top 10 list
                     if self.score > int(self.top_ten_list[-1][1]):
                        self.top_ten.input_name = False
                        self.game_state = 4
                     else:
                        self.game_state = 5   # return to intro

            if self.game_state == 4:
               if not self.top_ten.input_name:
                  self.top_ten.update(dt, self.score, self.top_ten_list)
               else:
                   # display top ten list
                   self.high_score = int(self.top_ten_list[0][1])
                   if self.display_tp.update(dt, self.top_ten_list):
                      self.game_state = 5

        else:
            if self.manual_on and self.manual.update():
                self.manual_on = False
                if self.level > 3 and self.saucer_time.is_pause: self.saucer_time.resume()

            if self.display_tp_on and self.display_tp.update(dt, self.top_ten_list):
                self.display_tp_on = False
                if self.level > 3 and self.saucer_time.is_pause: self.saucer_time.resume()

        if not self.manual_on and self.game_state != 4 and is_key_pressed(KEY_F1):
           self.manual_on = True
           if self.level > 3 and not self.saucer_time.is_pause:
              self.saucer_time.pause()
           # don't let top ten list cover center part of the manual
           if self.display_tp_on: self.display_tp_on = False

        if not self.display_tp_on and self.game_state != 4 and is_key_pressed(KEY_F2):
           self.display_tp_on = True
           if self.level > 3 and not self.saucer_time.is_pause:
              self.saucer_time.pause()
           self.display_tp.update(dt, self.top_ten_list)

        if self.game_state == 5:
           if self.intro.update():
              self.game_state = 1
              self.init()

    def draw(self):
        begin_drawing()
        clear_background(BKG_COLOR)

        if not self.manual_on and not self.display_tp_on:
           if self.hyper_jump_active: self.hyper_jump.draw()
           if self.player.active: self.player.draw()
           if self.game_state < 3: self.scoring()

           [sprite.draw()
               for sprite in self.bullet_list + self.asteroid_list + self.explosion_list + \
               self.saucer_bullet_list + self.saucer_list
           ]

           # let animation completed first
           if self.game_state == 3 and self.explosion_list == []:
              self.game_over_animation.draw()

           if self.game_state == 4:
              self.top_ten.draw()

           if self.game_state == 5:
              self.intro.draw(self.high_score)

        else:
            if self.manual_on: self.manual.draw()
            if self.display_tp_on: self.display_tp.draw()


        end_drawing()

    def run(self):
        while not window_should_close():
            self.update()
            self.draw()

        close_audio_device()
        unload_font(self.font_dict['font1'])
        unload_font(self.font_dict['font2'])
        close_window()


if __name__ == '__main__':
   game = Game()
   game.run()