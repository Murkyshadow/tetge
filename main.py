# tetge - tetris + dodge
import datetime
import os
import random
import sys
import threading
import time
from random import randint
import pygame
import pygame.mixer
import sqlite3

def start():    # таймер
    global st
    st = time.time()

def end():
    return float("%.2f"%(time.time()-st))

class tetge():
    def setting(self):
        """настройки игры"""
        pygame.font.init()
        pygame.mixer.init()

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
        self.speed_game = 10  # скорость игры
        self.permeable_blocks = [0]  # блоки, через которые игрок может проходить (воздух и в будущем бонусы)
        self.block_drop_time = 0.041  # время за которое падующий блок преодалевает 1 блок
        self.block_drop_time_start = 0.045

        self.skin_choice = 0
        self.field_size = [24 * 18, 24 * 24]  # размер поля в пикселях
        mypath = './players'
        self.skins = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]

        # self.player_img = pygame.image.load(self.skins[self.skin_choice])      # выведим игрока
        # self.player_img = pygame.transform.scale(self.player_img, (self.size_pl[0], self.size_pl[1]))  # подгоняем размеры персонажа

        self.plane = pygame.transform.scale(pygame.image.load('img/plane.png'), (153, 100))
        self.background = pygame.image.load('img/background.png')
        self.fail = pygame.image.load('img/fail.png')
        self.fail = pygame.transform.scale(self.fail, (150, 163))
        self.arrow = pygame.image.load('img/arrow.png')
        self.arrow = pygame.transform.scale(self.arrow, (70, 35))
        self.crown = pygame.image.load('img/crown.png')
        self.crown = pygame.transform.scale(self.crown, (30, 24))
        self.color_blocks = [pygame.image.load('img/cube1.png'), pygame.image.load('img/cube2.png'), pygame.image.load('img/cube3.png'), pygame.image.load('img/cube4.png'), pygame.image.load('img/cube5.png')]
        icon = pygame.image.load('img/icon.ico')
        icon = pygame.transform.scale(icon, (64, 64))
        pygame.display.set_icon(icon)

        self.background_black = pygame.image.load('img/black.png')
        self.background_black.set_alpha(130)          # полупрозрачный черный

        pygame.mixer.music.load("music/game.mp3")   # музыка при запуске игры

        self.rules_font = pygame.font.SysFont("comicsansms", 24)
        self.add_font2 = pygame.font.SysFont("Times New Roman", 15)
        self.add_font = pygame.font.SysFont("Times New Roman", 30)
        self.gameover_title = pygame.font.Font("./fonts/failed attempt.ttf", 70)
        self.score_title = pygame.font.Font("./fonts/SUBWT___.ttf", 32)
        self.menu_font = pygame.font.Font("./fonts/SUBWT___.ttf", 28)
        self.game_title = pygame.font.Font("./fonts/Blox2.ttf", 98)
        self.creators = pygame.font.Font("./fonts/SUBWT___.ttf", 16)
        self.fifaks_font = pygame.font.Font("./fonts/Fifaks10Dev1.ttf",24)

        self.taunts = [
                        'В следующий раз будьте\nвнимательней!',
                        'Вы были слишком медленным,\nчтобы уклониться от блока',
                        'Теперь вы блинчик',
                        'Вы не выдержали веса\nнескольких кубиков',
                        'Сегодня ожидается дождь из блоков.\nНе забудьте прихватить зонтик',
                        'Вас расплющило :(',

                        'Напомню, что цель игры\nуклоняться от блоков, а не наоборот',
                        'Музыку можно выключить,\nнажав на букву \'с\'',
                        # 'Поздравляем с ещё одним\nпроигрышом ^_^',
                        'Можно добавить свой скин, если\nпоместить фото в папку "players"',
                        # 'Спасибо за игру\nЖдем вас снова :)',
                        'Эту игру можно пройти',

                        'Где скилл, Лебовски?',
                        'Вы проиграли в какой-то раз',       # написать сколько смертей - сделано
                        'Вы проиграли в...\nЯ сбился со счета в какой раз',
                        'Ходит легенда, что\nблоки в меню не бесконечны',
                        # 'Вся боль начинается с 33 очков',

                        'Гравитация штука тяжелая',
                        'Вам пора баиньки',
                        'Еще разок?',
                        'Берегите голову',

                        'Вы любите фурри?',

        ]
        self.special_taunts = [
            'Бугагашеньки',  # если 13 33 66 99 666 999 очков
            'Ты же умер не специально,\nчтобы посмотреть надпись? Верно же?',  # если счёт ноль
            'Поздравляю с победой!\nПравда вы все равно умерли от\nголода под завалами блоков'
        ]

        self.taunts.append(f'Всего здесь {len(self.taunts)+len(self.special_taunts)+1} надпись(ей)')

    def reset(self):
        pygame.mixer.music.load("music/game.mp3")   # музыка при запуске игры

        win.fill((0, 0, 0))
        self.max_h = 0  # значение максимальной достигнутой высоты персонажем
        self.field = []  # поле 24 на 18
        self.now_blocks = []  # блоки в падении
        self.now_animation = False  # обозначает, что сейчас не происходит прорисовка падения блоков
        self.isjump = False
        self.house = False
        self.time_house = 5
        self.coor_player = [192, self.field_size[1]-self.size_pl[1]-2]   # начальные координаты игрока
        self.reflaction_x = 0   # отражение игрока право/лево
        self.reflaction_y = 0
        self.coor_plane = [self.field_size[0], 15]


        for i in range(self.field_size[0]//self.size_block):
            self.field.append([0] * (self.field_size[1]//self.size_block+4))  # одновременно видно будет только 24 клетки (вверх) и 18 клеток в ширину

        self.height = [0] * (self.field_size[0]//self.size_block)  # высота каждого столбца

        # jump:
        self.isjump = False   # сейчас игрок не в прыжке
        self.isfall = False
        self.jump_speed = 1
        self.direction = 0  # направление персонажа

        self.fm_time = 0
        self.t = 0       # замедление после появления нового падующего блока
        self.max_block = 1  # кол-во одновременно падующих блоков
        self.play = True
        if not self.menu:
            pygame.mixer.music.play(-1)
            if not self.play_music:
                pygame.mixer.music.pause()

    def __init__(self):
        self.DataBase()
        self.play_music = True
        self.menu = True

        self.skin_choice = 0
        self.setting()
        self.reset()

        self.main_menu()
        self.reset()

        win.blit(self.background, (0, 0), (0, 2880-24*24, 24*18, 24*24))
        self.score(0)

        text_dodge = self.fifaks_font.render('Уворачивайся от блоков.', False, (255, 255, 255))
        win.blit(text_dodge, (88, 100))
        win.blit(self.player_img, self.coor_player)
        text_dodge = self.fifaks_font.render('Управляй стрелочками.', False, (255, 255, 255))
        win.blit(text_dodge, (96, 140))
        win.blit(self.arrow, (self.field_size[0]//2-35, 190))

        # text_dodge = self.fifaks_font.render('Специальная версия с фурри', False, (255, 255, 255))
        # win.blit(text_dodge, (70, 300))
        # text_dodge = self.fifaks_font.render('для Алексея Владимировича', False, (255, 255, 255))
        # win.blit(text_dodge, (77, 340))

        pygame.display.update()

        wait = 4
        start()
        while end() <= wait:
            for event in pygame.event.get():  # пауза на C
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.music.pause()
                            self.play_music = False
                        else:
                            pygame.mixer.music.unpause()
                            self.play_music = True
                    if event.key == pygame.K_0:
                        global st
                        st += wait

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

        win.blit(self.background, (0, 0), (0, 2304-24*24, 24*18, 24*24))

        while 1:
            if not self.play:
                self.death()
            pygame.time.delay(self.speed_game)

            for event in pygame.event.get(): # пауза на C
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.music.pause()
                            self.play_music = False
                        else:
                            pygame.mixer.music.unpause()
                            self.play_music = True
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.move()
            if self.block_drop_time > 0.035:
                self.block_drop_time = self.block_drop_time_start - self.max_h/2200 + self.t
            else:
                self.t += 0.009
                self.block_drop_time += self.t
                if self.max_block < 7:
                    self.max_block +=1

            if 24 - self.max_h//2 > 4:
                intrv = 24 - self.max_h//2
            else:
                intrv = 4

            if (len(self.now_blocks) < self.max_block or self.now_blocks[-1][4] == intrv) and len(self.now_blocks)<8:
                self.new_generation_field()

            if not self.now_animation:  # обрабатываем анимацию падения блоков в отдельном потоке
                self.now_animation = True
                thr_fall = threading.Thread(target=self.fall_blocks, args=(), name="fall_block")
                thr_fall.start()

    def plane_animation(self):
        if self.max_h >= 26:
            self.coor_plane[1] = 35 + (self.max_h-26)*24
            x, y = self.coor_plane
            win.blit(self.plane, (int(x), y+20))
            self.coor_plane[0] -= 1.5


    def animation(self):
        if len(self.now_blocks) < self.max_block and self.count <= 0 or len(self.now_blocks) == 0:
            self.count = 10
            if len(self.now_blocks) < 8:
                self.new_generation_field()

        self.count -= 1
        c = 0
        for f in self.field:
            if f[22] == 0:
                c+=1

        if c <= 1:
            self.background_black.set_alpha(220)  # полупрозрачный черный
            self.update_win(0)
            self.background_black.set_alpha(0)

        if not self.now_animation:  # обрабатываем анимацию падения блоков в отдельном потоке
            self.now_animation = True
            thr_fall = threading.Thread(target=self.fall_blocks, args=(), name="fall_block")
            thr_fall.start()

    def move(self):
        """передвижение игрока"""
        win.blit(self.background, (0, 0), (0, 2880-(24+max(0, self.max_h-11))*24, 24*18, 24*24))    # отрисовка и  прокрутка заднего фона
        self.plane_animation()
        self.update_win(2)
        self.score(0)

        right = self.coor_player[0]+self.size_pl[0] # "x" правой части персонажа
        bottom = self.coor_player[1]+self.size_pl[1]+23 # "y" нижней части персонажа + после падения

        x_before = self.coor_player[0]  # для отражения игрока
        y_before = self.coor_player[1]

        if pygame.key.get_pressed()[pygame.K_RIGHT]:  # ходьба в право
            if self.direction == 2:
                self.fm_time = 0
            if self.coor_player[0]+self.size_pl[0]+self.speed >= self.field_size[0]: # стенка справа
                self.coor_player[0] = self.field_size[0]-self.size_pl[0]-1
            elif (self.field[(right+self.speed)//self.size_block][len(self.field[0])-self.coor_player[1]//self.size_block-5] not in self.permeable_blocks) or self.field[(right+self.speed)//self.size_block][len(self.field[0])-(self.coor_player[1]+self.size_pl[1])//self.size_block-5] not in self.permeable_blocks:       # блок справа снизу и справа сверху, если есть, то передвигаемся вплотную к нему
                while (self.field[(self.coor_player[0]+self.size_pl[0]+1)//self.size_block][len(self.field[0])-self.coor_player[1]//self.size_block-5] in self.permeable_blocks) and self.field[(self.coor_player[0]+self.size_pl[0]+1)//self.size_block][len(self.field[0])-(self.coor_player[1]+self.size_pl[1])//self.size_block-5] in self.permeable_blocks:
                    self.coor_player[0]+=1

                if pygame.key.get_pressed()[pygame.K_UP] and ((self.field[self.coor_player[0]//self.size_block][len(self.field[0])-bottom//self.size_block-5] in self.permeable_blocks and self.field[right//self.size_block][len(self.field[0])-bottom//self.size_block-5] in self.permeable_blocks) and bottom < self.field_size[1]):  # отскок от правой стены
                    self.isjump = True
                    self.fm_time = 2
                    self.direction = 1
                    self.jump_speed = 2
            else:       # стенки и блока справа нет
                self.coor_player[0] += self.speed

        if pygame.key.get_pressed()[pygame.K_LEFT]:  # ходьба в лево
            if self.direction == 1:
                self.fm_time = 0
            if self.coor_player[0]-self.speed < 0: # стенка слева
                self.coor_player[0] = 0
            elif self.field[(self.coor_player[0]-self.speed)//self.size_block][len(self.field[0])-self.coor_player[1]//self.size_block-5] not in self.permeable_blocks or self.field[(self.coor_player[0]-self.speed)//self.size_block][len(self.field[0])-(self.coor_player[1]+self.size_pl[1])//self.size_block-5] not in self.permeable_blocks:       # блок слева снизу и справа сверху,  если есть, то передвигаемся вплотную к нему
                if pygame.key.get_pressed()[pygame.K_UP] and ((self.field[self.coor_player[0]//self.size_block][len(self.field[0])-bottom//self.size_block-5] in self.permeable_blocks and self.field[right//self.size_block][len(self.field[0])-bottom//self.size_block-5] in self.permeable_blocks) and bottom < self.field_size[1]):
                    self.isjump = True
                    self.fm_time = 2
                    self.direction = 2
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
            if (self.field[self.coor_player[0]//self.size_block][len(self.field[0])-bottom//self.size_block-5] in self.permeable_blocks and\
                self.field[right//self.size_block][len(self.field[0])-bottom//self.size_block-5] in self.permeable_blocks) and\
                    bottom < self.field_size[1]:    # если снизу нет блока
                if self.jump_speed < 2:
                    self.jump_speed += 0.035     # 0.03 - ускорение свободного падения
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
                # print('высота прыжка - ', self.height)
            else:
                self.jump_speed -= 0.03
                self.coor_player[1] -= int(self.jump_speed**2)

        if self.fm_time>0:
            self.speed += 1
            if self.direction == 1 and not (self.coor_player[0]-self.speed < 0) and not (self.field[(self.coor_player[0]-self.speed)//self.size_block][len(self.field[0])-self.coor_player[1]//self.size_block-5] not in self.permeable_blocks or self.field[(self.coor_player[0]-self.speed)//self.size_block][len(self.field[0])-(self.coor_player[1]+self.size_pl[1])//self.size_block-5] not in self.permeable_blocks): # отскок в лево
                self.coor_player[0] -= self.speed
            elif self.direction == 2 and not (self.coor_player[0]+self.size_pl[0]+self.speed >= self.field_size[0]) and not ((self.field[(right+self.speed)//self.size_block][len(self.field[0])-self.coor_player[1]//self.size_block-5] not in self.permeable_blocks) or self.field[(right+self.speed)//self.size_block][len(self.field[0])-(self.coor_player[1]+self.size_pl[1])//self.size_block-5] not in self.permeable_blocks):
                self.coor_player[0] += self.speed
            else:   # если стенка
                self.fm_time = 0
            self.fm_time -= 0.1
            self.speed -= 1

        if x_before > self.coor_player[0]:  # отражение персонажа по горизонтали
            self.reflaction_x = 1
        elif x_before < self.coor_player[0]:
            self.reflaction_x = 0

        # if y_before > self.coor_player[1]:  # отражение персонажа по горизонтали
        #     self.reflaction_y = 0
        # elif y_before < self.coor_player[1]:
        #     self.reflaction_y = 1

        win.blit(pygame.transform.flip(self.player_img, self.reflaction_x, self.reflaction_y), self.coor_player)
        pygame.display.update()

    def draw_start_game_menu(self):
        win.blit(self.background_black, (0, 0))
        w = 25
        h = 50
        y = self.field_size[1] // 5
        text = self.gameover_title.render('START GAME', False, (255, 255, 255))
        win.blit(text, (self.field_size[0] // 9 + w, y))
        if self.choice != 0:
            text = self.menu_font.render('Select skin', False, (255, 255, 255))
            win.blit(text, (self.field_size[0] // 10 + 2 * w, y + 3 * h))
        text = self.menu_font.render('Select mode: Classic', False, (255, 255, 255))
        win.blit(text, (self.field_size[0] // 10 + 2 * w, y + 4 * h))
        text = self.menu_font.render('Start', False, (255, 255, 255))
        win.blit(text, (self.field_size[0] // 10 + 2 * w, y + 5.5 * h))
        text = self.menu_font.render('Back', False, (255, 255, 255))
        win.blit(text, (self.field_size[0] // 10 + 2 * w, y + 7 * h))

        text = self.menu_font.render('>', False, (255, 255, 255))
        if self.choice == 0:    # skin
            text = self.menu_font.render('<      >', False, (255, 255, 255))
            win.blit(text, (self.field_size[0] // 10 + w, y + (3 + self.choice) * h))

            plr = pygame.image.load('./players/'+self.skins[self.skin_choice])
            self.player_img = pygame.transform.scale(plr, (self.size_pl[0], self.size_pl[1]))
            plr = pygame.transform.scale(plr, (int(self.size_pl[0]*1.5), int(self.size_pl[1]*1.5)))
            prec = plr.get_rect(center=(self.field_size[0] // 10 + w + 43, y + (3 + self.choice) * h + 15))
            win.blit(plr, prec)
        else:
            win.blit(text, (self.field_size[0] // 10 + w, y + (3+self.choice) * h))

        pygame.display.update()

    def start_game_menu(self):
        self.draw_start_game_menu()
        w = 25
        h = 50

        while self.menu2:
            if not self.now_animation:
                self.animation()

            for event in pygame.event.get():  # пауза на C
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if (event.button == 1):  # нажата левая кнопка
                        if (event.pos[0] >= self.field_size[0] // 10 + 2 * w - 30 and event.pos[1] >= self.field_size[1] // 5 + 3 * h and event.pos[0] <= self.field_size[0] // 10 + 2 * w + 105 and event.pos[1] <= self.field_size[1] // 5 + 3 * h + 40):  # cтарт
                            if self.choice != 0:
                                self.choice = 0
                            elif event.pos[0] <= self.field_size[0] // 10 + 2 * w - 10 +15:
                                self.skin_choice -= 1
                                if self.skin_choice < 0:
                                    self.skin_choice = len(self.skins) - 1
                            elif event.pos[0] >= self.field_size[0] // 10 + 2 * w + 105 - 65:
                                self.skin_choice += 1
                                if self.skin_choice == len(self.skins):
                                    self.skin_choice = 0
                        elif event.pos[0] >= self.field_size[0] // 10 + 2 * w and event.pos[1] >= self.field_size[1] // 5 + 5.5 * h and event.pos[0] <= self.field_size[0] // 10 + 2 * w + 105 and event.pos[1] <= self.field_size[1] // 5 + 5.5 * h + 40:  # cтарт
                            self.menu2 = False
                            self.reset()
                        elif event.pos[0] >= self.field_size[0] // 10 + 2 * w and event.pos[1] >= self.field_size[1] // 5 + 7 * h and event.pos[0] <= self.field_size[0] // 10 + 2 * w + 105 and event.pos[1] <= self.field_size[1] // 5 + 7 * h + 40:  # cтарт
                            self.menu2 = False
                            self.menu = True

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.music.pause()
                            self.play_music = False
                        else:
                            self.play_music = True
                            pygame.mixer.music.unpause()
                    if event.key == pygame.K_UP:
                        if self.choice == 0:
                            self.choice = 4
                        elif self.choice == 4 or self.choice == 2.5:
                            self.choice -= 1.5
                        else:
                            self.choice -= 1
                    if event.key == pygame.K_DOWN:
                        if self.choice == 4:
                            self.choice = 0
                        elif self.choice == 1 or self.choice == 2.5:
                            self.choice += 1.5
                        else:
                            self.choice += 1

                    if self.choice == 0:    # skin
                        if event.key == pygame.K_RIGHT:
                            self.skin_choice += 1
                            if self.skin_choice == len(self.skins):
                                self.skin_choice = 0
                        if event.key == pygame.K_LEFT:
                            self.skin_choice -= 1
                            if self.skin_choice < 0:
                                self.skin_choice = len(self.skins)-1

                    if event.key == pygame.K_RETURN:
                        if self.choice == 1:  # мод
                            pass
                        elif self.choice == 2.5:  # cтарт
                            self.menu2 = False
                            self.reset()
                        elif self.choice == 4:  # back
                            self.menu2 = False
                            self.menu = True
                            self.choice = 0
                    elif event.key == pygame.K_ESCAPE:
                        self.menu2 = False
                        self.menu = True
                        self.choice = 0

    def draw_main_menu(self):
        win.blit(self.background_black, (0, 0))
        s = 52
        w = 20
        y = self.field_size[1] // 5

        text = self.game_title.render('T', False, (80, 41, 255))
        win.blit(text, (self.field_size[0] // 2 - 2 * s - w, y))
        win.blit(text, (self.field_size[0] // 2 - w, y))
        text = self.game_title.render('E', False, (255, 30, 0))
        win.blit(text, (self.field_size[0] // 2 - s - w, y))
        text = self.game_title.render('G', False, (59, 255, 0))
        win.blit(text, (self.field_size[0] // 2 + s * 1 - w, y))
        text = self.game_title.render('E', False, (196, 0, 255))
        win.blit(text, (self.field_size[0] // 2 + s * 2 - w, y))

        w = 20
        h = 50
        y = self.field_size[1] // 2

        text = self.menu_font.render('Start', False, (255, 255, 255))
        win.blit(text, (self.field_size[0] // 5 + w, y))
        text = self.menu_font.render('Scores', False, (255, 255, 255))
        win.blit(text, (self.field_size[0] // 5 + w, y + h))
        text = self.menu_font.render('Exit', False, (255, 255, 255))
        win.blit(text, (self.field_size[0] // 5 + w, y + h * 2))

        text = self.creators.render('© MurkyShadow, ToPzSpAy, dogganovich68', False, (255, 255, 255))
        win.blit(text, (self.field_size[0] // 5 - 55, self.field_size[1] - 30))

        w -= 30
        text = self.menu_font.render('>', False, (255, 255, 255))
        win.blit(text, (self.field_size[0] // 5 + w, y+h*self.choice))
        pygame.display.update()

    def main_menu(self):
        self.play = False
        self.scoreboard = False
        self.menu2 = False
        self.menu = True

        self.count = 0      # для двух падующих блоков в self.animation()
        self.max_block = 2  # 2 падующих блока
        self.block_drop_time = 0.07
        self.coor_player = [self.field_size[0]+100, self.field_size[1]+100]     # чтобы персонажа не убило на заднем фоне

        # self.skin_choice = 0
        self.choice = 0
        self.draw_main_menu()

        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load("music/menu.mp3")
            pygame.mixer.music.play(-1)
            if not self.play_music:
                pygame.mixer.music.pause()

        while self.menu:
            if not self.now_animation:
                self.animation()

            for event in pygame.event.get(): # пауза на C
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if (event.button == 1):   # нажата левая кнопка
                        if (event.pos[0]>=self.field_size[0] // 5 + 20 and event.pos[1]>=self.field_size[1] // 2 and event.pos[0]<=self.field_size[0] // 5 + 20+105 and event.pos[1]<=self.field_size[1] // 2 + 40):     # cтарт
                            self.choice = 0
                            self.menu = False
                            self.menu2 = True
                            self.start_game_menu()
                        elif (event.pos[0]>=self.field_size[0] // 5 + 20 and event.pos[1]>=self.field_size[1] // 2+50 and event.pos[0]<=self.field_size[0] // 5 + 20+105 and event.pos[1]<=self.field_size[1] // 2 + 40+50):  # scoreboard
                            self.choice = 0
                            self.menu = False
                            self.scoreboard = True
                            self.start_scoreboard()
                        elif (event.pos[0]>=self.field_size[0] // 5 + 20 and event.pos[1]>=self.field_size[1] // 2+100 and event.pos[0]<=self.field_size[0] // 5 + 20+105 and event.pos[1]<=self.field_size[1] // 2 + 40+100):  # scoreboard:
                            pygame.quit()
                            sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.music.pause()
                            self.play_music = False
                        else:
                            pygame.mixer.music.unpause()
                            self.play_music = True
                    if event.key == pygame.K_UP:
                        if self.choice == 0:
                            self.choice = 2
                        else:
                            self.choice -= 1
                    if event.key == pygame.K_DOWN:
                        if self.choice == 2:
                            self.choice = 0
                        else:
                            self.choice += 1
                    if event.key == pygame.K_RETURN:   # нажата левая кнопка
                        if self.choice == 0:     # cтарт
                            self.menu = False
                            self.menu2 = True
                            self.start_game_menu()
                        elif self.choice == 1:  # scoreboard
                            self.menu = False
                            self.scoreboard = True
                            self.start_scoreboard()
                        else:           # exit
                            pygame.quit()
                            sys.exit()
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

    def start_scoreboard(self):
        self.cur = self.con.cursor()
        self.data = self.cur.execute(f"""SELECT * FROM scoreboard ORDER BY score DESC""")
        self.score_data = []
        for score in self.data:
            self.score_data.append(score)

        self.draw_scoreboard()
        while self.scoreboard:
            if not self.now_animation:
                self.animation()

            for event in pygame.event.get(): # пауза на C
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if (event.button == 1):   # нажата левая кнопка
                        if (self.field_size[0] // 10+25 and event.pos[1]>=self.field_size[1] // 7+ 8.5 * 50 and event.pos[0]<=self.field_size[0] // 10+25+105 and event.pos[1]<=self.field_size[1] // 7 + 8.5 * 50 + 40):     # cтарт
                            self.scoreboard = False
                            self.menu = True

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.music.pause()
                            self.play_music = False
                        else:
                            pygame.mixer.music.unpause()
                            self.play_music = True
                    if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:        # back
                        self.scoreboard = False
                        self.menu = True

    def draw_scoreboard(self):
        win.blit(self.background_black, (0, 0))
        w = 25
        h = 50
        y = self.field_size[1] // 7
        text = self.gameover_title.render('SCOREBOARD', False, (255, 255, 255))
        win.blit(text, (self.field_size[0] // 10, y))

        win.blit(self.crown, (self.field_size[0] // 10, y))

        text = self.menu_font.render('Back', False, (255, 255, 255))
        win.blit(text, (self.field_size[0] // 10+w, y + 8.5 * h))

        text = self.menu_font.render('>', False, (255, 255, 255))
        win.blit(text, (self.field_size[0] // 10, y + 8.5 * h))

        text = self.menu_font.render('Score', False, (255, 255, 255))
        win.blit(text, (self.field_size[0] // 10+w, y+2*h))
        text = self.menu_font.render('Time', False, (255, 255, 255))
        win.blit(text, (self.field_size[0] // 2-w-w, y + 2*h))

        m = 5   # число рекордов
        for i in range(1, m+1):
            text = self.menu_font.render(str(i)+'.', False, (255, 255, 255))
            win.blit(text, (self.field_size[0] // 10, y + (2+i) * h))

        for i, s in enumerate(self.score_data):
            i+=1
            text = self.menu_font.render(str(s[0]), False, (255, 255, 255))
            win.blit(text, (self.field_size[0] // 10+w+10, y + (2+i) * h))

            text = self.menu_font.render(str(s[1]), False, (255, 255, 255))
            win.blit(text, (self.field_size[0] // 2-w-w, y + (2 + i) * h))
            if i == m:
                break

        pygame.display.update()

    def score(self, fill=1):
        if fill == 1:    # не заполняем при перерисовке с падением блока
            win.fill((0, 0, 0), (0, 0, 170, 35))
        text_surface = self.score_title.render('Score: ' + str(self.max_h), False, (242, 243, 244))
        win.blit(text_surface, (0, 0))

    def update_win(self, update=1):
        """при смене уровня карты, перерисовывает все окно"""
        # win.fill((0, 0, 0))
        y_win = 24
        for y in range(len(self.field[0]) - 28, len(self.field[0]) - 4):
            y_win -= 1
            for x in range(len(self.field)):
                if self.field[x][y] == 1:
                    win.blit(self.color_blocks[0], (x * 24, y_win * 24))
                elif self.field[x][y] == 2:
                    win.blit(self.color_blocks[1], (x * 24, y_win * 24))
                elif self.field[x][y] == 3:
                    win.blit(self.color_blocks[2], (x * 24, y_win * 24))
                elif self.field[x][y] == 4:
                    win.blit(self.color_blocks[3], (x * 24, y_win * 24))
                elif self.field[x][y] == 5:
                    win.blit(self.color_blocks[4], (x*24, y_win*24))

        if not update:
            win.blit(self.background_black, (0, 0))
        elif update == 2:
            pass
        else:
            # self.score()
            pygame.display.update()

    def fall_blocks(self):
        """вызываем перерисовку для всех блоков находящихся в падении"""
        for self.i, n_b in enumerate(self.now_blocks, 0):
            if self.fall(n_b[0], n_b[1], n_b[2], n_b[3], n_b[4], n_b[5]):
                return
        if self.menu:
            self.draw_main_menu()
        elif self.menu2:
            self.draw_start_game_menu()
        elif self.scoreboard:
            self.draw_scoreboard()
        else:
            pygame.display.update()

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
                if now_space < x_info[1] or (now_space == x_info[1] and stop_h < x_info[2]) or \
                        (now_space == x_info[1] and stop_h == x_info[2] and randint(0, 1) and block!=[[1, 1, 1, 1]]):    # палку ставим вплотную
                    x_info[2] = stop_h
                    x_info[1] = now_space
                    x_info[0] = x
                    now_block = block
        for i in range(len(now_block)):
            self.height[x_info[0] + i] = x_info[2] + len(now_block[i])  # пересчитываем высоту после падения блока

        print(self.skin_choice)
        if self.skins[self.skin_choice] == 'я_mario.png':     # если скин марио, то генерируется блок с вопросом
            color = randint(1, 5)
        else:
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

    # def generation_field(self):
    #     """генерирует блок и место, где остановится блок"""
    #     block = self.blocks_old[randint(0, len(self.blocks) - 1)]  # блок, который будет падать
    #     y = 23
    #     place = self.place_fall(block)  # координата, где будет падать блок
    #     maximum_h = self.height[place] + y
    #     before = maximum_h + 1
    #     for i, b in enumerate(block):
    #         if maximum_h + b.count(0) - self.height[place + i] <= before:
    #             before = maximum_h + b.count(0) - self.height[place + i]
    #             stop_h = self.height[place + i] - b.count(0)  # высота, на которой остановиться блок после падении
    #     for i in range(len(block)):
    #         self.height[place + i] = stop_h + len(block[i])  # пересчитываем высоту после падения блока
    #     color = randint(1, 4)
    #     self.now_blocks.append([block, stop_h, place, len(self.field[0]) - 5, 0, color])

    def fall(self, block, stop_h, place, y, y_win, color):
        """анимация падения блока"""
        if y > stop_h:
            for x in range(len(block)):
                for i, b in enumerate(block[x]):  # стираем поле, где был блок
                    if b == 1 or b == 2 or b == 3 or b == 4:
                        self.field[place + x][y + i] = 0
                        # if self.play:   # для следа в меню
                        #     win.fill((0, 0, 0), ((place + x) * 24, (y_win - i) * 24, 24, 24))
            y -= 1
            y_win += 1
            for x in range(len(block)):  # заполняем поле блоком в текущем y
                for i, b in enumerate(block[x], 0):
                    if b == 1 or b == 2 or b == 3 or b == 4:
                        self.field[place + x][y + i] = color
                        if not self.play:
                            win.blit(self.color_blocks[color-1], ((place + x) * 24, (y_win - i) * 24))
                        # if (place + x >= 7 or y_win - i >= 2) and self.play:  # перерисовываем score если его задел блок
                        #     self.score(0)
                        if ((self.coor_player[0] + 1) // self.size_block == place + x or (self.coor_player[0] + 15) // 24 == place + x) and len(self.field[0]) - (self.coor_player[1] + 20) // 24 - 5 == y + i:
                            self.play = False
                            self.now_animation = True
                            self.house = False
                            return True
                        elif self.play == True and self.field[self.coor_player[0]//24][len(self.field[0])-5+1-self.coor_player[1]//24]>=1 and (self.coor_player[0]//24-1==-1 or self.field[self.coor_player[0]//24-1][len(self.field[0])-5-self.coor_player[1]//24]>=1) and (self.coor_player[0]//24+1==18 or self.field[self.coor_player[0]//24+1][len(self.field[0])-5-self.coor_player[1]//24]):
                            if self.house and int(end()) >= self.time_house:
                                self.play = False
                                self.now_animation = True
                                return True
                            elif not self.house:
                                self.house = True
                                start()

            self.now_blocks[self.i] = [block, stop_h, place, y, y_win, self.now_blocks[self.i][5]]
        else:
            try:
                self.now_blocks.remove([block, stop_h, place, y, y_win, self.now_blocks[self.i][5]])
            except ValueError:
                pass

        row_pl = len(self.field[0]) - self.coor_player[1] // 24 - 5  # Y персонажа
        before = self.max_h
        self.max_h = max(self.max_h, row_pl)
        if self.max_h != before:
            # self.score()
            pass

        elif row_pl - (len(self.field[0]) - 28) > 10:
            self.max_h += 1
            # self.score()
        if self.play:
            pass
            # self.score(0)

        if self.max_h >= 12 and len(self.field[0]) - self.max_h <= 16:
            up = len(self.field[0]) - self.max_h - 15

            for k in range(up):
                for i in range(18):
                    self.field[i].append([0])
                for i in range(len(self.now_blocks)):
                    self.now_blocks[i][4] += 1
                # self.update_win()
                # win.fill((0, 0, 0), (self.coor_player[0], self.coor_player[1], 17, 20))
                self.coor_player[1] += 24
                # win.blit(self.player_img, (self.coor_player[0], self.coor_player[1]))
                # pygame.display.update()

    def death(self):
        self.insert_in_scoreboard()
        print('вы проиграли!')
        self.score()
        w, h = pygame.display.get_surface().get_size()
        pygame.draw.rect(win, (0, 0, 0), (0, 0, w, h))
        text1 = self.gameover_title.render('GAME OVER!', True, (255, 255, 255))
        text_rect = text1.get_rect(center=(w/2, h/2-190))
        win.blit(text1, text_rect)
        text1 = self.menu_font.render('Score: ' + str(self.max_h), True, (255, 255, 255))
        win.blit(text1, (w / 3+10, h / 2 - 130))

        win.blit(self.fail, (w / 3+10, h / 2 + 80))

        if self.house:
            funny_text = self.special_taunts[2] # в домике
        elif self.max_h == 13 or self.max_h == 33 or self.max_h == 66 or self.max_h == 99 or self.max_h == 666 or self.max_h == 999:
            funny_text = self.special_taunts[0]     # бугагашеньки
        elif self.max_h == 0:
            funny_text = self.special_taunts[1]     # специально умер??
        else:
            funny_text = self.taunts[randint(0, len(self.taunts) - 1)]
            if funny_text == 'Вы проиграли в какой-то раз':
                self.cur = self.con.cursor()
                count = self.cur.execute(f"""SELECT count(*) FROM scoreboard""")
                for deaths in count:
                    pass
                funny_text = f'Вы проиграли в {deaths[0]} раз'


        lines = funny_text.splitlines()
        for i, l in enumerate(lines):
            text1 = self.fifaks_font.render(l, True, (255, 255, 255))
            if len(lines) == 1:
                text_rect = text1.get_rect(center=(w / 2, h / 2 - 50 + (i*20) - ((len(lines)-1)*20)-5))
            else:
                text_rect = text1.get_rect(center=(w / 2, h / 2 - 50 + (i*20) - ((len(lines)-1)*20)+7))
            win.blit(text1, text_rect)

        pygame.mixer.music.stop()

        w = 20
        h = 50
        y = self.field_size[1] // 2

        text = self.menu_font.render('Retry', False, (255, 255, 255))
        win.blit(text, (self.field_size[0] // 5 + w, y))
        text = self.menu_font.render('Menu', False, (255, 255, 255))
        win.blit(text, (self.field_size[0] // 5 + w, y + h))

        w -= 30
        text = self.menu_font.render('>', False, (255, 255, 255))
        win.blit(text, (self.field_size[0] // 5 + w, y))

        pygame.display.update()

        choice = 0
        while 1:
            events = list(pygame.event.get())
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if (event.button == 1):  # нажата левая кнопка
                        if (event.pos[0] >= self.field_size[0] // 5 + w and event.pos[1] >= self.field_size[1] // 2 and event.pos[0] <= self.field_size[0] // 5 + w + 105 and event.pos[1] <= self.field_size[1] // 2 + 40):  # cтарт
                            self.reset()
                            return True
                        elif (event.pos[0] >= self.field_size[0] // 5 + w and event.pos[1] >= self.field_size[1] // 2 + 50 and event.pos[0] <= self.field_size[0] // 5 + w + 105 and event.pos[1] <= self.field_size[1] // 2 + 40 + 50):  # cтарт
                            self.menu = True
                            self.reset()
                            self.main_menu()
                            return True

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        win.fill((0, 0, 0), (self.field_size[0] // 5 + w, y + h * choice, 16, 32))  # стираем
                        if choice == 1:
                            choice = 0
                        win.blit(text, (self.field_size[0] // 5 + w, y + h * choice))
                        pygame.display.update()
                    if event.key == pygame.K_DOWN:
                        win.fill((0, 0, 0), (self.field_size[0] // 5 + w, y + h * choice, 16, 32))  # стираем
                        if choice == 0:
                            choice = 1
                        win.blit(text, (self.field_size[0] // 5 + w, y + h * choice))
                        pygame.display.update()
                    if event.key == pygame.K_RETURN:
                        if choice == 0:  # cтарт
                            self.reset()
                        else:
                            self.menu = True
                            self.reset()
                            self.main_menu()
                        return True
                    elif event.key == pygame.K_ESCAPE:
                        self.menu = True
                        self.reset()
                        self.main_menu()
                        return True

    def insert_in_scoreboard(self):
        self.cur = self.con.cursor()
        now = datetime.datetime.now()
        if now.minute < 10:
            time = f"{now.hour}:0{now.minute} {now.day}.{now.month}.{now.year}"
        else:
            time = f"{now.hour}:{now.minute} {now.day}.{now.month}.{now.year}"
        self.cur.execute(f"""INSERT INTO scoreboard (score, time) VALUES ({self.max_h}, "{time}") """)
        self.con.commit()
        self.cur.close()

    def DataBase(self):
        self.con = sqlite3.connect('tetge.db')
        self.cur = self.con.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS scoreboard (
            score INT,
            time STRING  
        ) """)
        self.cur.close()

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption('Tetge')
    icon = pygame.image.load('img/icon.ico')
    pygame.display.set_icon(icon)

    win = pygame.display.set_mode((24 * 18, 24 * 24))
    game = tetge()

    # тута красота :)  :
    # win = pygame.display.set_mode((512, 512))
    # for y in range(24*24):
    #     for x in range(255):
    #         win.fill((255-x, 0, x), ((x, y), (1, 1)))
    #
    #
    #     for x in range(255, 511):
    #         color = randint(x-255, x)
    #         if color > 255:
    #             win.fill((color-255, 0, 255), ((x, y), (1, 1)))
    #         else:
    #             win.fill((255, 0, color), ((x, y), (1, 1)))
    # pygame.display.update()
    #
    # type = 1
    # while 1:
    #     for event in pygame.event.get():  # пауза на C
    #         if event.type == pygame.QUIT:
    #             pygame.quit()
    #             sys.exit()
    #         if event.type == pygame.KEYDOWN:
    #             if event.key == pygame.K_1:
    #                 type = 1
    #             if event.key == pygame.K_2:
    #                 type = 2
    #
    #     if pygame.key.get_pressed()[pygame.K_UP] and y >= 0:
    #         win.fill((0, 0, 0), ((0, int(y)), (512, 1)))
    #         y -= 0.1
    #         pygame.display.update()
    #
    #     if type == 1:
    #         if pygame.key.get_pressed()[pygame.K_DOWN] and y <= 512:
    #             for x in range(255):
    #                 win.fill((255 - x, 0, x), ((x, int(y)), (1, 1)))
    #                 win.fill((0, x, 255 - x), ((x+255, int(y)), (1, 1)))
    #             y += 0.1
    #             pygame.display.update()
    #
    #     if type == 2:
    #         if pygame.key.get_pressed()[pygame.K_DOWN] and y <= 512:
    #             for x in range(255):
    #                 win.fill((255 - x, 0, x), ((x, int(y)), (1, 1)))
    #                 win.fill((0, x, 255 - x), ((x+255, int(y)), (1, 1)))
    #                 y += 0.1
    #                 pygame.display.update()

