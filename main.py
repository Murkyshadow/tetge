# tetge - tetris + dodge
import os
import threading
import time
from random import randint
import pygame


class tetge():
    def __init__(self):
        self.blocks = [[[1, 1], [1, 1]],    [[1, 1], [1], [1]],    [[1], [1, 1, 1]],    [[1, 1, 1], [0, 0, 1]],     [[0, 1], [0, 1], [1, 1]],    [[1, 1, 1], [0, 1]],    [[1], [1, 1], [1]],    [[0, 1], [1, 1, 1]],    [[0, 1], [1, 1], [0, 1]],     [[1], [1], [1], [1]],     [[1, 1, 1, 1]],     [[1, 1], [0, 1], [0, 1]],    [[0, 0, 1], [1, 1, 1]],    [[1, 1, 1], [1]],      [[1], [1], [1, 1]]]  # записаны столбики каждого блока
        self.max_h = 11     # значение максимальной достигнутой высоты персонажем               высота верхнего слоя, изменяется при изменении максимальной достигнутой высоты
        self.field = []
        self.now_blocks = []
        self.now_animation = False
        for i in range(18):
            self.field.append([0]*28)     # одновременно видно будет только 24 клетки (вверх)
        self.height = [0]*18        # высота каждого столбца
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.max_h += 1
                        print(self.max_h)
            if len(self.now_blocks) < 2:
                self.generation_field()  # создаем поток для функции first (target (указываем название функции без скобок), args (переменные, передаваемые в функцию), name (название потока))

            if not self.now_animation:
                thr_fall = threading.Thread(target=self.fall_blocks, args=(), name="fall")
                thr_fall.start()
            if self.max_h >= 12 and len(self.field[0]) - self.max_h <= 16:
                up = len(self.field[0]) - self.max_h - 15
                print('up', up)
                for k in range(up):
                    for i in range(18):
                        self.field[i].append([0])
                for i in range(len(self.now_blocks)):
                    self.now_blocks[i][4] += up
                self.update_win()


    def update_win(self):
        """при смене уровня карты, перерисовывает все окно"""
        color_block = pygame.image.load('img/cube_red.png')      # блок 24 на 24 пикселя
        win.fill((0, 0, 0))
        y_win = 24
        for y in range(len(self.field[0])-28, len(self.field[0])-4):
            y_win -= 1
            # win.fill((0, 0, 0), (x*24, y_win*24, 24, 24))
            for x in range(len(self.field)):
                if self.field[x][y] == 1:
                    win.blit(color_block, (x*24, y_win*24))
                    pygame.display.update()


    def fall_blocks(self):
        """вызываем перерисовку для всех блоков находящихся в падении"""
        self.now_animation = True
        for self.i, n_b in enumerate(self.now_blocks, 0):
            self.fall(n_b[0], n_b[1], n_b[2], n_b[3], n_b[4])
        time.sleep(0.05)
        self.now_animation = False

    def place_fall(self, block):
        """выбираем место для падения блока"""
        min_height = min(self.height)
        min_now = randint(1, self.height.count(min_height)) # если минимальных чисел несколько, то среди них выбираем рандомно
        count_same = 0
        for i, h in enumerate(self.height):
            if h == min_height:
                count_same += 1
                if count_same == min_now:
                    if len(block) + i > 17:  # если блок заходит за пределы карты, смещаем место падения
                        return i-((len(block) + i) - 18)
                    return i

    def generation_field(self):
        """генерирует блок и место, где остановится блок"""
        block = self.blocks[randint(0, len(self.blocks)-1)]     # блок, который будет падать
        y = 23
        place = self.place_fall(block)   # координата, где будет падать блок
        maximum_h = self.height[place]+y
        before = maximum_h + 1
        for i, b in enumerate(block):
            if maximum_h+b.count(0)-self.height[place+i] <= before:
                before = maximum_h+b.count(0)-self.height[place+i]
                stop_h = self.height[place+i] - b.count(0)   # высота, на которой остановиться блок после падении
        for i in range(len(block)):
            self.height[place + i] = stop_h+len(block[i])    # пересчитываем высоту после падения блока
        self.now_blocks.append([block, stop_h, place, len(self.field[0])-5, 0])

    def fall(self, block, stop_h, place, y, y_win):
        """анимация падения блока"""
        color_block = pygame.image.load('img/cube_red.png')      # блок 24 на 24 пикселя

        if y > stop_h:
            for x in range(len(block)):
                for i, b in enumerate(block[x]):    # стираем поле, где блок
                    if b == 1:
                        self.field[place+x][y + i] = 0
                        win.fill((0, 0, 0), ((place+x)*24, (y_win-i)*24, 24, 24))
            y-=1
            y_win += 1
            for x in range(len(block)):             # заполняем поле блоком в текущем y
                for i, b in enumerate(block[x], 0):
                    if b == 1:
                        self.field[place+x][y+i] = 1
                        win.blit(color_block, ((place+x)*24, (y_win-i)*24))
            pygame.display.update()
            # time.sleep(0.1)
            self.now_blocks[self.i] = [block, stop_h, place, y, y_win]

        else:
            self.now_blocks.remove([block, stop_h, place, y, y_win])
            # self.update_win()


if __name__ == "__main__":
    win = pygame.display.set_mode((24*18, 24*24))
    # color_block = pygame.image.load('img/cube_red.png')  # блок 24 на 24 пикселя
    # win.blit(color_block, (50, 50))
    # win.fill((0, 0, 0))
    # pygame.display.update()
    game = tetge()