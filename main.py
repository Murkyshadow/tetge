# tetge - tetris + dodge
import os
import time
from random import randint
import pygame


class tetge():
    def __init__(self):
        self.blocks = [[[1, 1], [1, 1]],    [[1, 1], [1], [1]],    [[1], [1, 1, 1]],    [[1, 1, 1], [0, 0, 1]],     [[0, 1], [0, 1], [1, 1]],    [[1, 1, 1], [0, 1]],    [[1], [1, 1], [1]],    [[0, 1], [1, 1, 1]],    [[0, 1], [1, 1], [0, 1]],     [[1], [1], [1], [1]],     [[1, 1, 1, 1]],     [[1, 1], [0, 1], [0, 1]],    [[0, 0, 1], [1, 1, 1]],    [[1, 1, 1], [1]],      [[1], [1], [1, 1]]]  # записаны столбики каждого блока
        self.max_h = 23     # высота верхнего слоя, изменяется при изменении максимальной достигнутой высоты
        self.field = []
        for i in range(18):
            self.field.append([0]*28)     # одновременно видно будет только 24 клетки (вверх)
        self.height = [0]*18        # высота каждого столбца
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
            self.generation_field()

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
        self.fall(block, stop_h, place)

    def fall(self, block, stop_h, place):
        """анимация падения блока"""
        y = len(self.field[0])-5
        y_win = 0
        color_block = pygame.image.load('img/cube_red.png')      # блок 24 на 24 пикселя

        while y > stop_h:
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

            # os.system('cls')
            # print('стоп -', stop_h)
            # print('y -', y)
            # print('место падения -', place)
            # print('блок -', block)
            # print(*self.height)
            # print()

            # for j in range(len(self.field[0])-1, -1, -1):    # вывод в консоль
            #     for g in range(len(self.field)):
            #         print(self.field[g][j], end=' ')
            #     print()
            time.sleep(0.1)


if __name__ == "__main__":
    win = pygame.display.set_mode((24*18, 24*24))
    game = tetge()