# tetge - tetris + dodge
import os
import random
import sys
import threading
import time
from random import randint
import pygame
from PyQt5.QtWidgets import QFileDialog, QWidget


class Button():
    def __init__(self, color, x, y, width, height, text=''):
        self.color = color
        self.ogcol = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, ui, outline=None):
        # Call this method to draw the button on the screen
        if outline:
            pygame.draw.rect(ui, outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 0)

        pygame.draw.rect(ui, self.color, (self.x, self.y, self.width, self.height), 0)

        if self.text != '':
            font = pygame.font.SysFont('Arial', 24)
            text = font.render(self.text, 1, (0, 0, 0))
            ui.blit(text, (
            self.x + (self.width / 2 - text.get_width() / 2), self.y + (self.height / 2 - text.get_height() / 2)))

    def isOver(self, pos):
        global STATE
        # Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                self.color = (128, 128, 128)
            else:
                self.color = self.ogcol
        else:
            self.color = self.ogcol

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pos[0] > self.x and pos[0] < self.x + self.width:
                    if pos[1] > self.y and pos[1] < self.y + self.height:
                        return True

class MainMenu(QWidget):
    def __init__(self):
        super().__init__()
        btn_start = Button((100,100,100),150,100,150,50,text="Начать")
        btn_start.draw(win)
        btn_character = Button((100,100,100),150,200,150,50,text="Персонаж")
        btn_character.draw(win)
        btn_exit = Button((100,100,100),150,300,150,50,text="Выйти")
        btn_exit.draw(win)
        pygame.display.update()
        while True:
            eve = pygame.mouse.get_pos()

            if btn_start.isOver(eve):
                tetge()

            if btn_character.isOver(eve):
                fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                          "All Files (*);;PNG (*.png);;JPG (*.jpg)")
                img = pygame.image.load(fileName)  # выведим игрока
                img = pygame.transform.scale(img, (50, 50))  # подгоняем размеры
                img_pos = img.get_rect()
                win.blit(img,img_pos)
                pygame.display.update()

            if btn_exit.isOver(eve):
                pygame.quit()
                sys.exit()

class tetge():
    def __init__(self):
        self.blocks_old = [[[1, 1], [1, 1]], [[1, 1], [1], [1]], [[1], [1, 1, 1]], [[1, 1, 1], [0, 0, 1]],
                           [[0, 1], [0, 1], [1, 1]], [[1, 1, 1], [0, 1]], [[1], [1, 1], [1]], [[0, 1], [1, 1, 1]],
                           [[0, 1], [1, 1], [0, 1]], [[1], [1], [1], [1]], [[1, 1, 1, 1]], [[1, 1], [0, 1], [0, 1]],
                           [[0, 0, 1], [1, 1, 1]], [[1, 1, 1], [1]],
                           [[1], [1], [1, 1]]]  # записаны столбики каждого блока

        self.blocks = [[[1, 1], [1, 1]],  # квадрат
                       [[1, 1], [1, 0], [1, 0]],  # Г фигура
                       [[1, 1], [0, 1], [0, 1]],  # Г фигура перевернутая
                       [[1, 1, 1], [0, 1, 0]],  # э т о
                       [[1, 1, 1, 1]],  # палка
                       [[0, 1, 1], [1, 1, 0]],  # зигзаг
                       [[1, 1, 0], [0, 1, 1]]]  # зигзаг другой
        win.fill((0, 0, 0))
        self.max_h = 0  # значение максимальной достигнутой высоты персонажем
        self.field = []  # поле 24 на 18
        self.now_blocks = []  # блоки в падении
        self.now_animation = False  # обозначает, что сейчас не происходит прорисовка падения блоков
        self.now_jump = False
        height_jump = 55
        max_jump = 55
        size_pl = [17, 20]  # размер персонажа в пикселях
        pygame.font.init()
        self.stop = False

        self.coor_player = [192, 552]
        self.player_img = pygame.image.load('img/918.png')  # выведим игрока
        self.player_img = pygame.transform.scale(self.player_img, (size_pl[0], size_pl[1]))  # подгоняем размеры

        for i in range(18):
            self.field.append([0] * 28)  # одновременно видно будет только 24 клетки (вверх) и 18 клеток в ширину
        self.height = [0] * 18  # высота каждого столбца

        while 1:
            col_pl = self.coor_player[0] // 24  # X персонажа
            row_pl = len(self.field[0]) - self.coor_player[1] // 24 - 5  # Y персонажа
            pygame.time.delay(5)
            self.score()
            win.blit(self.player_img, self.coor_player)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    # if event.key == pygame.K_DOWN:
                    #     self.max_h += 1
                    #     print(self.max_h)
                    if event.key == pygame.K_UP and not self.now_jump:  # прыжок
                        self.now_jump = True
                        height_jump = 0
                    if event.key == pygame.K_SPACE:  # ставим синий блок
                        # win.blit(pygame.image.load('img/cube_blue.png'), (col_pl * 24, (23 - row_pl) * 24))
                        # print(col_pl, row_pl)
                        # pygame.display.update()
                        print("высота сейчас", self.max_h)
            if self.field[(self.coor_player[0] + 1) // 24][row_pl] != 0 or self.field[(self.coor_player[0] + 15) // 24][
                row_pl] != 0:  # если достигает блока сверху, то сразу опускается вниз
                height_jump = max_jump
            if self.now_jump and height_jump < max_jump and self.field[col_pl][row_pl] == 0 and \
                    self.field[(self.coor_player[0] + size_pl[0] - 2) // 24][row_pl] == 0:  # взлет прыжка
                win.fill((0, 0, 0), (self.coor_player[0], self.coor_player[1], size_pl[0], size_pl[1]))
                self.coor_player[1] -= 1
                win.blit(self.player_img, self.coor_player)
                pygame.display.update()
                height_jump += 1
            elif self.coor_player[1] != 552 and (row_pl != 0 and self.field[col_pl][row_pl - 1] == 0 and
                                                 self.field[(self.coor_player[0] + size_pl[0] - 2) // 24][
                                                     row_pl - 1] == 0):  # падение
                # self.now_jump = True
                win.fill((0, 0, 0), (self.coor_player[0], self.coor_player[1], size_pl[0], size_pl[1]))
                self.coor_player[1] += 1
                win.blit(self.player_img, self.coor_player)
                pygame.display.update()
            else:
                self.now_jump = False

            if pygame.key.get_pressed()[pygame.K_LEFT] and self.coor_player[0] != 0 and \
                    self.field[(self.coor_player[0] - 1) // 24][
                        len(self.field[0]) - (self.coor_player[1] + 18) // 24 - 5] == 0 and self.field[col_pl][
                row_pl] == 0:  # ходьба в лево
                win.fill((0, 0, 0), (self.coor_player[0], self.coor_player[1], size_pl[0], size_pl[1]))
                self.coor_player[0] -= 1
                win.blit(self.player_img, self.coor_player)
                pygame.display.update()
            elif pygame.key.get_pressed()[pygame.K_RIGHT] and self.coor_player[0] != 415 and (col_pl == 17 or (
                    self.field[col_pl + 1][len(self.field[0]) - (self.coor_player[1] + 18) // 24 - 5] == 0 and
                    self.field[col_pl + 1][row_pl] == 0) or (col_pl) * 24 + 8 != self.coor_player[0]):  # ходьба в право
                win.fill((0, 0, 0), (self.coor_player[0], self.coor_player[1], size_pl[0], size_pl[1]))
                self.coor_player[0] += 1
                win.blit(self.player_img, self.coor_player)
                pygame.display.update()

            if len(self.now_blocks) < 1:
                self.new_generation_field()

            if not self.now_animation:  # обрабатываем анимацию падения блоков в отдельном потоке
                self.now_animation = True
                thr_fall = threading.Thread(target=self.fall_blocks, args=(), name="fall_block")
                thr_fall.start()

    def score(self):
        my_font = pygame.font.SysFont('Comic Sans MS', 30)
        win.fill((0, 0, 0), (0, 0, 170, 35))
        text_surface = my_font.render('Счёт: ' + str(self.max_h), False, (242, 243, 244))
        win.blit(text_surface, (0, 0))

    def update_win(self):
        """при смене уровня карты, перерисовывает все окно"""
        color_block = pygame.image.load('img/cube_red.png')  # блок 24 на 24 пикселя
        win.fill((0, 0, 0))
        y_win = 24
        for y in range(len(self.field[0]) - 28, len(self.field[0]) - 4):
            y_win -= 1
            for x in range(len(self.field)):
                if self.field[x][y] == 1:
                    win.blit(color_block, (x * 24, y_win * 24))
                    pygame.display.update()
                # elif self.field[x][y] == 2:
                #     win.blit(pygame.image.load('img/cube_blue.png'), (x * 24, y_win * 24))
                #     pygame.display.update()
        # win.blit(self.player_img, self.coor_player)
        # self.coor_player[1] += 24  # смещаем персонажа на 1 блок вниз
        # win.blit(self.player_img, self.coor_player)
        # pygame.display.update()

    def fall_blocks(self):
        """вызываем перерисовку для всех блоков находящихся в падении"""
        for self.i, n_b in enumerate(self.now_blocks, 0):
            self.fall(n_b[0], n_b[1], n_b[2], n_b[3], n_b[4])
        time.sleep(0.05)
        self.now_animation = False

    def place_fall(self, block):
        """выбираем место для падения блока"""
        min_height = min(self.height)
        min_now = randint(1, self.height.count(
            min_height))  # если минимальных чисел несколько, то среди них выбираем рандомно
        count_same = 0
        for i, h in enumerate(self.height):
            if h == min_height:
                count_same += 1
                if count_same == min_now:
                    if len(block) + i > 17:  # если блок заходит за пределы карты, смещаем место падения
                        return i - ((len(block) + i) - 18)
                    return i

    def new_generation_field(self):
        block = self.blocks[randint(0, len(self.blocks) - 1)]  # блок, который будет падать
        self.now_block = block
        x_info = [0, 1000, 1000]  # x, space, высота остановки
        for rt in range(4):
            block = self.rotate_block(self.now_block, rt)
            max_x = 18 - len(block)

            for x in range(0, max_x + 1):
                now_space = 0
                maximum_h = self.height[x] + 23
                before = maximum_h + 1
                for i, b in enumerate(block):
                    if maximum_h + b.count(0) - self.height[x + i] <= before:
                        before = maximum_h + b.count(0) - self.height[x + i]
                        stop_h = self.height[x + i] - b.count(0)  # высота, на которой остановиться блок после падении
                for i in range(0, len(block)):
                    now_space += (stop_h + block[i].count(0) - self.height[x + i])
                if now_space < x_info[1] or (now_space == x_info[1] and stop_h < x_info[2]):
                    x_info[2] = stop_h
                    x_info[1] = now_space
                    x_info[0] = x
                    now_block = block
        for i in range(len(now_block)):
            self.height[x_info[0] + i] = x_info[2] + len(now_block[i])  # пересчитываем высоту после падения блока
        print(x_info)
        self.now_blocks.append([now_block, x_info[2], x_info[0], len(self.field[0]) - 5, 0])

    def rotate_block(self, block, rt):
        rotated = block
        for r in range(rt + 1):
            rotated = list(zip(*rotated))[::-1]
        rotated = [list(i) for i in rotated]
        for y, yb in enumerate(rotated):
            for x, b in enumerate(yb):
                if b == 1 and x < len(yb) - 1:
                    for i in range(x, len(yb) - 1):
                        if rotated[y][i + 1] == 1:
                            break
                    else:
                        for i in range(x, len(yb) - 1):
                            rotated[y].pop(x + 1)

        return rotated

    def generation_field(self):
        """генерирует блок и место, где остановится блок"""
        block = self.blocks[randint(0, len(self.blocks) - 1)]  # блок, который будет падать
        y = 23
        place = self.place_fall(block)  # координата, где будет падать блок
        maximum_h = self.height[place] + y
        before = maximum_h + 1
        for i, b in enumerate(block):
            if maximum_h + b.count(0) - self.height[place + i] <= before:
                before = maximum_h + b.count(0) - self.height[place + i]
                stop_h = self.height[place + i] - b.count(0)  # высота, на которой остановиться блок после падении
        for i in range(len(block)):
            self.height[place + i] = stop_h + len(block[i])  # пересчитываем высоту после падения блока
        self.now_blocks.append([block, stop_h, place, len(self.field[0]) - 5, 0])

    def fall(self, block, stop_h, place, y, y_win):
        """анимация падения блока"""
        color_block = pygame.image.load('img/cube_red.png')  # блок 24 на 24 пикселя

        if y > stop_h:
            for x in range(len(block)):
                for i, b in enumerate(block[x]):  # стираем поле, где блок
                    if b == 1:
                        self.field[place + x][y + i] = 0
                        win.fill((0, 0, 0), ((place + x) * 24, (y_win - i) * 24, 24, 24))
            y -= 1
            y_win += 1
            for x in range(len(block)):  # заполняем поле блоком в текущем y
                for i, b in enumerate(block[x], 0):
                    if b == 1:
                        self.field[place + x][y + i] = 1
                        win.blit(color_block, ((place + x) * 24, (y_win - i) * 24))
                        if ((self.coor_player[0] + 1) // 24 == place + x or (
                                self.coor_player[0] + 15) // 24 == place + x) and len(self.field[0]) - (
                                self.coor_player[1] + 20) // 24 - 5 == y + i:
                            print('вы проиграли! Ваша максимальная высота:', self.max_h)
                            self.score()
                            pygame.quit()

            pygame.display.update()
            self.now_blocks[self.i] = [block, stop_h, place, y, y_win]
        else:
            try:
                self.now_blocks.remove([block, stop_h, place, y, y_win])
            except ValueError:
                pass

        row_pl = len(self.field[0]) - self.coor_player[1] // 24 - 5  # Y персонажа
        self.max_h = max(self.max_h, row_pl)

        if row_pl - (len(self.field[0]) - 28) > 10:
            self.max_h += 1

        if self.max_h >= 12 and len(self.field[0]) - self.max_h <= 16:
            up = len(self.field[0]) - self.max_h - 15

            for k in range(up):
                for i in range(18):
                    self.field[i].append([0])
                # for _ in range(up):
                for i in range(len(self.now_blocks)):
                    self.now_blocks[i][4] += 1
                self.update_win()
                win.fill((0, 0, 0), (self.coor_player[0], self.coor_player[1], 17, 20))
                self.coor_player[1] += 24
                win.blit(self.player_img, (self.coor_player[0], self.coor_player[1]))
                pygame.display.update()


if __name__ == "__main__":
    pygame.init()
    win = pygame.display.set_mode((24 * 18, 24 * 24))
    game = MainMenu()
