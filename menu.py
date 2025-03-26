
from constants import *


class Intro:
    def __init__(self, texture, center_text_pos, font, size):
        self.texture = texture
        self.font = font
        self.size = size
        self.pos = center_text_pos("HIGH SCORE : 0000000", self.font, self.size, 4, 10)

    def update(self):
        return is_key_pressed(KEY_ENTER)

    def draw(self, high_score):
        draw_texture(self.texture, 0, 0, WHITE)
        draw_text_ex(self.font, f'HIGH SCORE : {int(high_score):07}', self.pos, self.size, 4, WHITE)

class Manual:
    def __init__(self, texture):
        self.texture = texture

    def update(self):
        return is_key_pressed(KEY_SPACE)

    def draw(self):
        draw_texture(self.texture, 0, 0, WHITE)

class Display_top_ten:
    def __init__(self, font1, size1, font2, size2, center_text_pos, box_image):
        self.font1 = font1
        self.size1 = size1
        self.font2 = font2
        self.size2 = size2
        self.center_text_pos = center_text_pos
        self.box_image = box_image
        self.box_image_pos = Vector2(SCREEN_WIDTH // 2 - self.box_image.width // 2,
                                     SCREEN_HEIGHT // 2 - self.box_image.height // 2)

        self.text = "Press Space to Continue ....."
        self.pos = self.center_text_pos(self.text, self.font2, self.size2, 4, 800)

        self.top_ten_list = []
        self.alpha = 255

    def update(self, dt, top_ten_list):
        self.top_ten_list = top_ten_list
        self.alpha -= 200 * dt
        if self.alpha <= 0: self.alpha = 255

        self.draw()

        return is_key_pressed(KEY_SPACE)

    def draw(self):
        draw_texture_v(self.box_image, self.box_image_pos, WHITE)
        pos_y = 238
        for i in range(len(self.top_ten_list)):
            # center_text_pos(text, font, size, space, pos_y):
            line_no = f'{i+1:02}.   '
            name  = self.top_ten_list[i][0] + "   "
            # convert the score back to int
            score = f'{int(self.top_ten_list[i][1]):07}'

            pos = self.center_text_pos(line_no+name+score, self.font1, self.size1, 4, pos_y)

            draw_text_ex(self.font1, line_no+name+score, pos, self.size1, 4, WHITE)
            pos_y += 50

        draw_text_ex(self.font2, self.text, self.pos, self.size2, 4, (255, 255, 255, int(self.alpha)))


class Game_over:
    def __init__(self, textures, sound, font, size, center_text_pos):

       self.textures = textures

       self.pos_x = SCREEN_WIDTH//2 - self.textures[0].width//2
       self.pos_y = SCREEN_HEIGHT//2 - self.textures[0].height//2
       self.frame = 1
       self.alpha = 0
       self.sound = sound
       self.font = font
       self.size = size
       self.center_text_pos = center_text_pos
       self.text = "Press Space to Continue ....."
       # center_text_pos(text, font, size, space, pos_y):
       self.pos = self.center_text_pos(self.text, self.font, self.size, 4, 800)

    def update(self, dt):
        # play animation and game over sound
        if self.frame == 1: play_sound(self.sound)  # enable it later
        if self.frame < len(self.textures) - 1:
           self.frame += 10 * dt
        else:
           self.alpha -= 200 * dt
           if self.alpha < 0: self.alpha = 255

           return is_key_pressed(KEY_SPACE)


    def draw(self):
        draw_texture(self.textures[int(self.frame)], self.pos_x, self.pos_y, WHITE)
        draw_text_ex(self.font, self.text, self.pos, self.size, 4, (255,255,255,int(self.alpha)))


class Top_ten:
    def __init__(self, font1, size1, font2, size2, center_text_pos):
        self.file = 'file/top_10.csv'
        self.score = 0
        self.font1 = font1
        self.size1 = size1
        self.font2 = font2
        self.size2 = size2

        self.dt = 0
        self.display_tp = False
        self.input_name = False

        self.center_text_pos = center_text_pos
        # center_text_pos(text, font, size, space, pos_y):
        self.text_1 = "Final Score : 0000000"
        self.text_2 = "(A-Z, 0-9, Backspace to backward, Return to confirm)"

        # center_text_pos(text, font, size, space, pos_y):
        self.pos_1 = self.center_text_pos(self.text_1, self.font2, self.size2, 4, 10)
        self.pos_2 = self.center_text_pos(self.text_2,self.font2, self.size2, 4, 670)

        self.cursor = [885, 920, 955, 990]
        self.cursor_pos = 0
        self.name = [" ", " ", " ", " "]
        self.alpha = 255

    def reset(self):
        self.cursor_pos = 0
        self.name = [" ", " ", " ", " "]
        self.alpha = 255

    def read_file(self):
        file_list = []
        try:
           with open(self.file, 'r') as file:
               reader = csv.reader(file)
               file_list = [row for row in reader]
        except FileNotFoundError:
            # if not exists, create a dummy file
            [file_list.append(['----', 0]) for i in range(10)]
            self.write_file(file_list)

        return file_list

    def write_file(self, file_list):
        # write to file
        with open(self.file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(file_list)

    def input_player_name(self, top_ten_list):
        self.alpha -= 150 * self.dt
        if self.alpha <= 0: self.alpha = 255

        # read character input
        key = get_key_pressed()

        if (65 <= key <= 90) or (48 <= key <= 57):  # A-Z, 0-9
           self.name[self.cursor_pos] = chr(key)
           self.cursor_pos += 1
           if self.cursor_pos > 3: self.cursor_pos = 3

        if is_key_pressed(KEY_BACKSPACE):
           self.name[self.cursor_pos] = " "
           self.cursor_pos -= 1
           if self.cursor_pos < 0: self.cursor_pos = 0

        if is_key_pressed(KEY_ENTER):
           # concatenate self.name
           name = ''.join(self.name)
           if not ' ' in name:
               # delete last item in top_ten_list
               # and add this one
               del top_ten_list[-1]
               top_ten_list.append([name, self.score])

               # Sort the list in reverse order (descending order)
               top_ten_list.sort(key=lambda x: int(x[1]), reverse=True)

               self.write_file(top_ten_list)

               # input name and write to file completed
               self.reset()
               self.input_name = True

    def update(self, dt, score, top_ten_list):
        self.score = score
        self.dt = dt

        if not self.input_name:
           self.input_player_name(top_ten_list)
        # else:
        #    return self.input_name

        self.draw()

    def draw(self):
        if not self.input_name:
            draw_text_ex(self.font2, f'Final score : {self.score:07}', self.pos_1, self.size2, 4, WHITE)
            draw_text_ex(self.font2, "Enter your name : ", Vector2(520,360), self.size2, 4, WHITE)
            draw_text_ex(self.font2, self.text_2, self.pos_2, self.size2, 4, WHITE)

            for i in range(0,len(self.name)):
                draw_text_ex(self.font1, self.name[i], Vector2(self.cursor[i], 360), 36, 15, WHITE)

            # draw_text_ex(self.font, self.name[0], Vector2(self.cursor[0], 360), 36, 15, WHITE)
            # draw_text_ex(self.font, self.name[1], Vector2(self.cursor[1], 360), 36, 15, WHITE)
            # draw_text_ex(self.font, self.name[2], Vector2(self.cursor[2], 360), 36, 15, WHITE)
            # draw_text_ex(self.font, self.name[3], Vector2(self.cursor[3], 360), 36, 15, WHITE)

            # draw cursor
            draw_line_ex(Vector2(self.cursor[self.cursor_pos],400), Vector2(self.cursor[self.cursor_pos]+25,400),
                         4, (255,255,255,int(self.alpha)))




