# tetge - tetris + dodge
import os
import random
import threading
import time
from random import randint
import pygame
import pygame.mixer


class tetge():
    def reset(self):
        self.max_h = 0  # значение максимальной достигнутой высоты персонажем
        self.field = []  # поле 24 на 18
        self.now_blocks = []  # блоки в падении
        self.now_animation = False  # обозначает, что сейчас не происходит прорисовка падения блоков
        self.isjump = False
        self.play = True

        pygame.font.init()
        # pygame.mixer.init()
        self.setting()

        for i in range(self.field_size[0]//self.size_block):
            self.field.append([0] * (self.field_size[1]//self.size_block+4))  # одновременно видно будет только 24 клетки (вверх) и 18 клеток в ширину
        self.height = [0] * (self.field_size[0]//self.size_block)  # высота каждого столбца

        # jump:
        self.isjump = False   # сейчас игрок не в прыжке
        self.isfall = False
        self.jump_speed = 1
        self.t = 0       # замедление после появления нового падующего блока
        self.max_block = 1  # кол-во одновременно падующих блоков
        pygame.mixer.music.play(-1)

    def __init__(self):
        self.reset()

        while 1:
            if not self.play:
                continue
            # col_pl = self.coor_player[0] // 24  # X персонажа
            # row_pl = len(self.field[0]) - self.coor_player[1] // 24 - 5  # Y персонажа
            pygame.time.delay(self.speed_game)
            self.score()

            win.blit(self.player_img, self.coor_player)
            pygame.display.update()

            for event in pygame.event.get(): # пауза на C
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.music.pause()
                        else:
                            pygame.mixer.music.unpause()
                if event.type == pygame.QUIT:
                    pygame.quit()

            self.move()
            if self.block_drop_time > 0.035:
                self.block_drop_time = self.block_drop_time_start - self.max_h/3000 + self.t
            else:
                self.t += 0.006
                self.block_drop_time += self.t
                self.max_block += 1

            if len(self.now_blocks) < self.max_block:
                self.new_generation_field()

            if not self.now_animation:  # обрабатываем анимацию падения блоков в отдельном потоке
                #print(self.block_drop_time)
                self.now_animation = True
                thr_fall = threading.Thread(target=self.fall_blocks, args=(), name="fall_block")
                thr_fall.start()

    def move(self):
        """передвижение игрока"""
        win.fill((0, 0, 0), (self.coor_player[0], self.coor_player[1], self.size_pl[0], self.size_pl[1]))   # стираем

        right = self.coor_player[0]+self.size_pl[0] # "x" правой части персонажа

        if pygame.key.get_pressed()[pygame.K_RIGHT]:  # ходьба в право
            if self.coor_player[0]+self.size_pl[0]+self.speed >= self.field_size[0]: # стенка справа
                self.coor_player[0] = self.field_size[0]-self.size_pl[0]-1
            elif (self.field[(right+self.speed)//self.size_block][len(self.field[0])-self.coor_player[1]//self.size_block-5] not in self.permeable_blocks) or self.field[(right+self.speed)//self.size_block][len(self.field[0])-(self.coor_player[1]+self.size_pl[1])//self.size_block-5] not in self.permeable_blocks:       # блок справа снизу и справа сверху, если есть, то передвигаемся вплотную к нему
                if pygame.key.get_pressed()[pygame.K_UP]:
                    self.isjump = True
                    self.jump_speed = 2
                while (self.field[(right+1)//self.size_block][len(self.field[0])-self.coor_player[1]//self.size_block-5] in self.permeable_blocks) and self.field[(right+1)//self.size_block][len(self.field[0])-(self.coor_player[1]+self.size_pl[1])//self.size_block-5] in self.permeable_blocks:
                    self.coor_player[0]+=1
            else:       # стенки и блока справа нет
                self.coor_player[0] += self.speed

        if pygame.key.get_pressed()[pygame.K_LEFT]:  # ходьба в лево
            if self.coor_player[0]-self.speed < 0: # стенка слева
                self.coor_player[0] = 0
            elif self.field[(self.coor_player[0]-self.speed)//self.size_block][len(self.field[0])-self.coor_player[1]//self.size_block-5] not in self.permeable_blocks or self.field[(self.coor_player[0]-self.speed)//self.size_block][len(self.field[0])-(self.coor_player[1]+self.size_pl[1])//self.size_block-5] not in self.permeable_blocks:       # блок справа снизу и справа сверху,  если есть, то передвигаемся вплотную к нему
                if pygame.key.get_pressed()[pygame.K_UP]:
                    self.isjump = True
                    self.jump_speed = 2
                while (self.field[(self.coor_player[0]-1)//self.size_block][len(self.field[0])-self.coor_player[1]//self.size_block-5] in self.permeable_blocks) and self.field[(self.coor_player[0]-1)//self.size_block][len(self.field[0])-(self.coor_player[1]+self.size_pl[1])//self.size_block-5] in self.permeable_blocks:
                    self.coor_player[0]-=1
            else:       # стенки и блока справа нет
                self.coor_player[0] -= self.speed

        right = self.coor_player[0]+self.size_pl[0] # "x" правой части персонажа
        bottom = self.coor_player[1]+self.size_pl[1]+int(self.jump_speed**2) # "y" нижней части персонажа + после падения

        if pygame.key.get_pressed()[pygame.K_UP] and not self.isjump and not self.isfall:  # прыжок
            self.isjump = True
            self.jump_speed = 2

        if not self.isjump:     # падение
            if (self.field[self.coor_player[0]//self.size_block][len(self.field[0])-bottom//self.size_block-5] in self.permeable_blocks and self.field[right//self.size_block][len(self.field[0])-bottom//self.size_block-5] in self.permeable_blocks) and bottom < self.field_size[1]:    # если снизу нет блока
                if self.jump_speed < 2:
                    self.jump_speed += 0.03     # 0.03 - ускорение свободного падения
                self.coor_player[1] += int(self.jump_speed ** 2)
            else:
                self.isfall = False
                self.jump_speed = 1
                self.coor_player[1] += self.size_block - ((self.coor_player[1]+self.size_pl[1]-1)%self.size_block) - 2

        if self.isjump:     # прыжок
            if self.jump_speed <= 1 or (self.field[self.coor_player[0]//self.size_block][len(self.field[0])-(self.coor_player[1]-int(self.jump_speed ** 2))//self.size_block-5] not in self.permeable_blocks or self.field[(right)//self.size_block][len(self.field[0])-(self.coor_player[1]-int(self.jump_speed ** 2))//self.size_block-5] not in self.permeable_blocks):
                while self.jump_speed > 1 and self.field[self.coor_player[0]//self.size_block][len(self.field[0])-(self.coor_player[1]-1)//self.size_block-5] in self.permeable_blocks and self.field[(right)//self.size_block][len(self.field[0])-(self.coor_player[1]-1)//self.size_block-5] in self.permeable_blocks:
                    self.coor_player[1] -= 1
                self.isjump = False
                self.isfall = True
                self.jump_speed = 1
                # print('высота прыжка - ', self.height_j)
            else:
                self.jump_speed -= 0.03
                self.coor_player[1] -= int(self.jump_speed**2)
                # self.height_j += int(self.jump_speed**2)

        win.blit(self.player_img, self.coor_player)
        pygame.display.update()


    def setting(self):
        """настройки игры"""
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

        self.speed = 2  # скорость передвижения игрока
        self.size_pl = [17, 20]  # размер персонажа в пикселях
        self.size_block = 24    # размер блока
        self.speed_game = 10   # скорость игры
        self.permeable_blocks = [0]  # блоки, через которые игрок может проходить (воздух и в будущем бонусы)
        self.block_drop_time = 0.045  # время за которое падующий блок преодалевает 1 блок
        self.block_drop_time_start = 0.045


        self.field_size = [24 * 18, 24 * 24]  # размер поля в пикселях
        self.coor_player = [192, self.field_size[1]-self.size_pl[1]-2]   # начальные координаты игрока
        self.player_img = pygame.image.load('img/player.png')      # выведим игрока
        self.player_img = pygame.transform.scale(self.player_img, (self.size_pl[0], self.size_pl[1]))  # подгоняем размеры персонажа

        pygame.mixer.music.load("music/game.mp3")   # музыка при запуске игры

    def score(self):
        my_font = pygame.font.SysFont('Comic Sans MS', 30)
        win.fill((0, 0, 0), (0, 0, 170, 35))
        text_surface = my_font.render('Счёт: ' + str(self.max_h), False, (242, 243, 244))
        win.blit(text_surface, (0, 0))

    def update_win(self):
        """при смене уровня карты, перерисовывает все окно"""
        red_block = pygame.image.load('img/cube1.png')  # блок 24 на 24 пикселя
        blue_block = pygame.image.load('img/cube2.png')  # блок 24 на 24 пикселя
        green_block = pygame.image.load('img/cube3.png')  # блок 24 на 24 пикселя
        pink_block = pygame.image.load('img/cube4.png')  # блок 24 на 24 пикселя
        win.fill((0, 0, 0))
        y_win = 24
        for y in range(len(self.field[0]) - 28, len(self.field[0]) - 4):
            y_win -= 1
            for x in range(len(self.field)):
                if self.field[x][y] == 1:
                    win.blit(red_block, (x * 24, y_win * 24))
                elif self.field[x][y] == 2:
                    win.blit(blue_block, (x * 24, y_win * 24))
                elif self.field[x][y] == 3:
                    win.blit(green_block, (x * 24, y_win * 24))
                elif self.field[x][y] == 4:
                    win.blit(pink_block, (x * 24, y_win * 24))
        pygame.display.update()

        # win.blit(self.player_img, self.coor_player)
        # self.coor_player[1] += 24  # смещаем персонажа на 1 блок вниз
        # win.blit(self.player_img, self.coor_player)
        # pygame.display.update()

    def fall_blocks(self):
        """вызываем перерисовку для всех блоков находящихся в падении"""
        for self.i, n_b in enumerate(self.now_blocks, 0):
            if self.fall(n_b[0], n_b[1], n_b[2], n_b[3], n_b[4], n_b[5]):
                return
        time.sleep(self.block_drop_time)
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
                if now_space < x_info[1] or (now_space == x_info[1] and stop_h < x_info[2]) or (now_space == x_info[1] and stop_h == x_info[2] and randint(0, 1)):
                    x_info[2] = stop_h
                    x_info[1] = now_space
                    x_info[0] = x
                    now_block = block
        for i in range(len(now_block)):
            self.height[x_info[0] + i] = x_info[2] + len(now_block[i])  # пересчитываем высоту после падения блока
        # print(x_info)
        color = randint(1, 4)
        self.now_blocks.append([now_block, x_info[2], x_info[0], len(self.field[0]) - 5, 0, color])

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
        block = self.blocks_old[randint(0, len(self.blocks) - 1)]  # блок, который будет падать
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
        color = randint(1, 4)
        self.now_blocks.append([block, stop_h, place, len(self.field[0]) - 5, 0, color])

    def fall(self, block, stop_h, place, y, y_win, color):
        """анимация падения блока"""
        color_block = pygame.image.load(f'img/cube{color}.png')  # блок 24 на 24 пикселя

        if y > stop_h:
            for x in range(len(block)):
                for i, b in enumerate(block[x]):  # стираем поле, где был блок
                    if b == 1 or b == 2 or b == 3 or b == 4:
                        self.field[place + x][y + i] = 0
                        win.fill((0, 0, 0), ((place + x) * 24, (y_win - i) * 24, 24, 24))
            y -= 1
            y_win += 1
            for x in range(len(block)):  # заполняем поле блоком в текущем y
                for i, b in enumerate(block[x], 0):
                    if b == 1 or b == 2 or b == 3 or b == 4:
                        self.field[place + x][y + i] = color
                        win.blit(color_block, ((place + x) * 24, (y_win - i) * 24))
                        if self.death(place, x, y, i):
                            self.reset()
                            return True

            pygame.display.update()
            self.now_blocks[self.i] = [block, stop_h, place, y, y_win, self.now_blocks[self.i][5]]
        else:
            try:
                self.now_blocks.remove([block, stop_h, place, y, y_win, self.now_blocks[self.i][5]])
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
                for i in range(len(self.now_blocks)):
                    self.now_blocks[i][4] += 1
                self.update_win()
                win.fill((0, 0, 0), (self.coor_player[0], self.coor_player[1], 17, 20))
                self.coor_player[1] += 24
                win.blit(self.player_img, (self.coor_player[0], self.coor_player[1]))
                pygame.display.update()

    def death(self, place, x, y, i):
        if ((self.coor_player[0] + 1) // self.size_block == place + x or (self.coor_player[0] + 15) // 24 == place + x) and len(self.field[0]) - (self.coor_player[1] + 20) // 24 - 5 == y + i:
            print('вы проиграли!')
            self.score()
            w,h = pygame.display.get_surface().get_size()
            pygame.draw.rect(win, (0,0,0), (0,0,w,h))
            pygame.display.update()
            f1 = pygame.font.Font(None, 36)
            text1 = f1.render('Вы проиграли!', True,
                              (180, 50, 50))
            win.blit(text1, (w/3,h/2))
            text1 = f1.render('   Счёт: '+str(self.max_h), True,
                              (180, 50, 50))
            win.blit(text1, (w/3,h/1.7))
            pygame.mixer.music.stop()
            pygame.display.update()
            self.now_animation = True
            self.play = False
            time.sleep(3)
            pygame.draw.rect(win, (0, 0, 0), (0, 0, w, h))
            return True


if __name__ == "__main__":
    pygame.init()
    win = pygame.display.set_mode((24 * 18, 24 * 24))
    game = tetge()
