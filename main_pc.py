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


def start():  # таймер
    global st
    st = time.time()


def end():
    return float("%.2f" % (time.time() - st))


class character():
    def set_player(self, coor_player, control={'left':pygame.K_LEFT, 'up':pygame.K_UP, 'right':pygame.K_RIGHT}, img = 1):
        # self.max_h = max_h  # значение максимальной достигнутой высоты персонажем, но пока оставим максимальную

        # jump:
        self.isjump = False  # сейчас игрок не в прыжке
        self.isfall = False
        self.jump_speed = 1
        self.direction = 0  # направление персонажа
        self.rebound_speed = 1
        self.actual_x = 123

        self.coor_player = coor_player  # начальные координаты игрока
        self.control = control

        self.reflaction_x = False  # отражение игрока право/лево
        self.reflaction_y = False
        self.player_img = img
        self.helmet = 231

        self.speed = 2
        self.fm_time = 0
        self.img = '123'

class tetge():
    def setting(self):
        """настройки игры"""
        pygame.font.init()
        try:
            pygame.mixer.init()
        except Exception:
            print('подключите наушники')

        # self.blocks_old = [[[1, 1], [1, 1]], [[1, 1], [1], [1]], [[1], [1, 1, 1]], [[1, 1, 1], [0, 0, 1]],
        #                    [[0, 1], [0, 1], [1, 1]], [[1, 1, 1], [0, 1]], [[1], [1, 1], [1]], [[0, 1], [1, 1, 1]],
        #                    [[0, 1], [1, 1], [0, 1]], [[1], [1], [1], [1]], [[1, 1, 1, 1]], [[1, 1], [0, 1], [0, 1]],
        #                    [[0, 0, 1], [1, 1, 1]], [[1, 1, 1], [1]],
        #                    [[1], [1], [1, 1]]]  # записаны столбики каждого блока

        self.blocks = [[[1, 1], [1, 1]],  # квадрат
                       [[1, 1], [1, 0], [1, 0]],  # Г фигура
                       [[1, 1], [0, 1], [0, 1]],  # Г фигура отраженная
                       [[1, 1, 1], [0, 1, 0]],  # т
                       [[1, 1, 1, 1]],          # палка
                       [[0, 1, 1], [1, 1, 0]],  # зигзаг
                       [[1, 1, 0], [0, 1, 1]]]  # зигзаг отраженный

        # self.speed = 2  # скорость передвижения игроков
        self.size_pl = [17, 20]  # размер персонажа в пикселях
        self.size_block = 24  # размер блока
        self.speed_game = 10  # скорость игры
        self.permeable_blocks = [0]  # блоки, через которые игрок может проходить (воздух и в будущем бонусы)
        self.block_drop_time = 0.041  # время за которое падующий блок преодалевает 1 блок
        self.block_drop_time_start = 0.045

        self.skin_choice = 0
        self.field_size = [24 * 18, 24 * 24]  # размер поля в пикселях
        mypath = './players'
        self.skins = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]

        self.helmet_one = pygame.image.load('img/helmet_one.png')   # шлем для космоса (с 42)
        self.helmet_two = pygame.image.load('img/helmet_two.png')   # шлем для космоса (с 42)

        self.plane = pygame.image.load('img/plane.png')     # самолет
        self.background = pygame.image.load('img/background.png')
        self.fail = pygame.image.load('img/fail.png')
        self.fail = pygame.transform.scale(self.fail, (150, 163))
        self.arrow = pygame.image.load('img/arrow.png')
        self.arrow = pygame.transform.scale(self.arrow, (70, 35))
        self.crown = pygame.image.load('img/crown.png')
        self.crown = pygame.transform.scale(self.crown, (30, 24))
        self.color_blocks = [pygame.image.load('img/cube1.png'), pygame.image.load('img/cube2.png'),
                             pygame.image.load('img/cube3.png'), pygame.image.load('img/cube4.png'),
                             pygame.image.load('img/cube5.png')]

        try:
            pygame.mixer.music.load("music/game.mp3")  # музыка при запуске игры
        except Exception:
            print('наушники')

        self.rules_font = pygame.font.SysFont("comicsansms", 24)
        self.add_font2 = pygame.font.SysFont("Times New Roman", 15)
        self.add_font = pygame.font.SysFont("Times New Roman", 30)
        self.gameover_title = pygame.font.Font("./fonts/failed attempt.ttf", 70)
        self.score_title = pygame.font.Font("./fonts/SUBWT___.ttf", 32)
        self.menu_font = pygame.font.Font("./fonts/SUBWT___.ttf", 28)
        self.game_title = pygame.font.Font("./fonts/Blox2.ttf", 98)
        self.creators = pygame.font.Font("./fonts/SUBWT___.ttf", 16)
        self.fifaks_font = pygame.font.Font("./fonts/Fifaks10Dev1.ttf", 24)

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
            'Вы проиграли в какой-то раз',  # написать сколько смертей - сделано
            'Вы проиграли в...\nЯ сбился со счета в какой раз',
            'Ходит легенда, что\nблоки в меню не бесконечны',
            # 'Вся боль начинается с 33 очков',

            'Гравитация штука тяжелая',
            'Вам пора баиньки',
            'Еще разок?',
            'Берегите голову',

            'Вы любите фурри?',

            "Чтобы поставить игру\nна паузу, нажмите на 'ecp'",
            "Tetge от слов tetris + dodge"

        ]
        self.special_taunts = [
            'Бугагашеньки',  # если 13 33 66 99 666 999 очков
            'Ты же умер не специально,\nчтобы посмотреть надпись? Верно же?',  # если счёт ноль
            'Поздравляю с победой!\nПравда вы все равно умерли от\nголода под завалами блоков'
        ]

        self.taunts.append(f'Всего здесь {len(self.taunts) + len(self.special_taunts) + 1} надпись(ей)')
        self.height_fly_plane = 15
        self.height_helmet = 42

        self.now_players = 1

        plr = pygame.image.load('./players/' + self.skins[0])
        player_img = pygame.transform.scale(plr, (self.size_pl[0], self.size_pl[1]))

        # игроки
        self.player_one = character()
        self.player_one.set_player(coor_player=[192 - 10, self.field_size[1] - self.size_pl[1] - 2], img=player_img)
        self.player_two = character()
        self.player_two.set_player(coor_player=[192 + 10, self.field_size[1] - self.size_pl[1] - 2],
                                control={'left': pygame.K_a, 'up': pygame.K_w, 'right': pygame.K_d}, img=player_img)
        self.players = []
        self.players.append(self.player_one)
        self.players.append(self.player_two)

        # self.player_three = character()
        # self.player_three.set_player(coor_player=[192 + 40, self.field_size[1] - self.size_pl[1] - 2],
        #                         control={'left': pygame.K_KP1, 'up': pygame.K_KP5, 'right': pygame.K_KP3}, img=player_img)
        # self.players.append(self.player_three)

        # скин (временно):
        # plr = pygame.image.load('./players/' + self.skins[1])
        # player_img = pygame.transform.scale(plr, (self.size_pl[0], self.size_pl[1]))
        self.player_one.player_img = pygame.transform.scale(player_img, (self.size_pl[0], self.size_pl[1]))
        self.player_two.player_img = pygame.transform.scale(pygame.image.load('./players/' + self.skins[-2]),
                                                            (self.size_pl[0], self.size_pl[1]))
        self.player_one.helmet = self.helmet_one
        self.player_two.helmet = self.helmet_two

    def play_music(self, music):
        try:
            pygame.mixer.music.load(f"music/{mus}")  # музыка при запуске игры
        except Exception:
            print('наушники')

    def reset(self):
        try:
            pygame.mixer.music.load("music/game.mp3")  # музыка при запуске игры
        except Exception:
            print('наушники')

        win.fill((0, 0, 0))
        self.max_h = 0  # значение максимальной достигнутой высоты персонажем

        self.field = []  # поле 24 на 18
        self.now_blocks = []  # блоки в падении
        self.now_animation = False  # обозначает, что сейчас не происходит прорисовка падения блоков
        self.house = False
        self.time_house = 5
        self.coor_plane = [self.field_size[0], 15]

        for i in range(self.field_size[0] // self.size_block):
            self.field.append([0] * (self.field_size[1] // self.size_block + 4))  # одновременно видно будет только 24 клетки (вверх) и 18 клеток в ширину

        self.height = [0] * (self.field_size[0] // self.size_block)  # высота каждого столбца
        # self.coor_player = [192, self.field_size[1]-self.size_pl[1]-2]   # начальные координаты игрока

        self.t = 0  # замедление после появления нового падующего блока
        self.max_block = 1  # кол-во одновременно падующих блоков
        self.play = True

        self.background_black = pygame.image.load('img/black.png')
        self.background_black.set_alpha(130)  # полупрозрачный черный

        x = self.field_size[0]//2 + 10
        for player in self.players:
            player.coor_player = [x, self.field_size[1] - self.size_pl[1] - 2]
            x-=20

        if not self.menu and self.play_music:
            pygame.mixer.music.play(-1)
            if not self.play_music:
                pygame.mixer.music.pause()

    def __init__(self):
        self.DataBase()
        try:
            pygame.mixer.init()
            self.play_music = True
        except Exception:
            print('подключите наушники')
            self.play_music = False

        self.menu = True

        self.player_choice = 0
        self.choice_pl = True
        self.skin_choice = 0
        # self.mode_choice = 1    # по факту число игроков
        self.mods = ['тут выбираем режим игры', 'Classic', '2 players', '3 players']
        self.pause_play = False

        self.setting()
        self.reset()

        self.main_menu()
        self.reset()

        win.blit(self.background, (0, 0), (0, 2880 - 24 * 24, 24 * 18, 24 * 24))
        self.score()
        for player in self.players[:self.now_players]:
            win.blit(player.player_img, player.coor_player)

        self.game_rules()   # правила игры (5 секунд)
        win.blit(self.background, (0, 0), (0, 2304 - 24 * 24, 24 * 18, 24 * 24))

        while 1:
            if not self.play:
                self.death_menu()
            pygame.time.delay(self.speed_game)

            for event in pygame.event.get():  # пауза на C
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.music.pause()
                            self.play_music = False
                        else:
                            pygame.mixer.music.unpause()
                            self.play_music = True
                    if event.key == pygame.K_ESCAPE:
                        self.pause_play = True

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if self.pause_play:
                self.pause_menu()
            else:
                self.draw_background()
                self.plane_animation()
                self.update_win(2)
                self.score()

                for player in self.players[:self.now_players]:
                    self.move(player)
                pygame.display.update()

                if self.block_drop_time > 0.035:
                    self.block_drop_time = self.block_drop_time_start - self.max_h / 2200 + self.t
                else:
                    self.t += 0.009
                    self.block_drop_time += self.t
                    if self.max_block < 7:
                        self.max_block += 1

                if 24 - self.max_h // 2 > 4:
                    intrv = 24 - self.max_h // 2
                else:
                    intrv = 4

                if (len(self.now_blocks) < self.max_block or self.now_blocks[-1][4] == intrv) and len(self.now_blocks) < 8:
                    self.new_generation_field()

                if not self.now_animation:  # обрабатываем анимацию падения блоков в отдельном потоке
                    self.now_animation = True
                    thr_fall = threading.Thread(target=self.fall_blocks, args=(), name="fall_block")
                    thr_fall.start()

    def draw_background(self):
        win.blit(self.background, (0, 0), (0, 2880 - (24 + max(0, self.max_h - 11)) * 24, 24 * 18, 24 * 24))  # отрисовка и  прокрутка заднего фона

    def draw_pause_menu(self):
        y = self.field_size[1] // 3
        w = 25
        h = 50

        self.draw_background()
        self.update_win(2)

        for player in self.players[:self.now_players]:
            win.blit(pygame.transform.flip(player.player_img, player.reflaction_x, player.reflaction_y), player.coor_player)

        if self.max_h >= self.height_helmet and player.img != 'w_amogus.png':    # появляется шлем (тк в космосе нет воздуха)
            win.blit(pygame.transform.flip(player.helmet, player.reflaction_x, player.reflaction_y), player.coor_player)

        self.score()

        if not self.screenshot:
            win.blit(self.background_black, (0, 0))

            text1 = self.gameover_title.render('PAUSE!', True, (255, 255, 255))
            win.blit(text1, (self.field_size[0] // 4 + w, y-2*h))

            text = self.menu_font.render('Resume', False, (255, 255, 255))
            win.blit(text, (self.field_size[0] // 5 + w, y+h))
            text = self.menu_font.render('Menu', False, (255, 255, 255))
            win.blit(text, (self.field_size[0] // 5 + w, y + 2*h))

            w -= 30
            text = self.menu_font.render('>', False, (255, 255, 255))
            win.blit(text, (self.field_size[0] // 5 + w, y+(h*self.choice)))

        pygame.display.update()

    def pause_menu(self):
        self.screenshot = False
        self.choice = 1
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.play_music = False
        while 1:
            self.draw_pause_menu()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:     # пауза на C
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.music.pause()
                            self.play_music = False
                        else:
                            pygame.mixer.music.unpause()
                            self.play_music = True

                    if event.key == pygame.K_UP:
                        if self.choice == 1:
                            self.choice = 2
                        else:
                            self.choice -= 1

                    if event.key == pygame.K_DOWN:
                        if self.choice == 2:
                            self.choice = 1
                        else:
                            self.choice += 1

                    if event.key == pygame.K_RETURN:
                        self.pause_play = False
                        try:
                            print(pygame.mixer.music.get_busy())
                            if not pygame.mixer.music.get_busy():
                                pygame.mixer.music.unpause()
                                self.play_music = True
                        except Exception:
                            print('подключите наушники')
                            self.play_music = False

                        if self.choice == 1:  # продолжить
                            return
                        elif self.choice == 2:  # меню
                            self.menu = True
                            self.play = False
                            self.now_animation = False
                            self.house = False
                            self.reset()
                            return self.main_menu()

                    elif event.key == pygame.K_ESCAPE:
                        try:
                            print(pygame.mixer.music.get_busy())
                            if not pygame.mixer.music.get_busy():
                                pygame.mixer.music.unpause()
                                self.play_music = True
                        except Exception:
                            print('подключите наушники')
                            self.play_music = False
                        self.pause_play = False
                        return

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if pygame.key.get_pressed()[pygame.K_SPACE]:
                self.screenshot = True
            else:
                self.screenshot = False

    def game_rules(self):
        text_dodge = self.fifaks_font.render('Уворачивайся от блоков.', False, (255, 255, 255))
        win.blit(text_dodge, (88, 100))

        text_dodge = self.fifaks_font.render('Управляй стрелочками.', False, (255, 255, 255))
        win.blit(text_dodge, (96, 140))
        win.blit(self.arrow, (self.field_size[0] // 2 - 35, 190))

        pygame.display.update()

        wait = 4
        start()
        skip = False
        while end() <= wait and not skip:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:     # пауза на C
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.music.pause()
                            self.play_music = False
                        else:
                            pygame.mixer.music.unpause()
                            self.play_music = True

                    if event.key == pygame.K_RETURN:
                        skip = True

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

    def plane_animation(self):
        if self.max_h >= self.height_fly_plane:
            self.coor_plane[1] = 35 + (self.max_h - self.height_fly_plane) * 24
            x, y = self.coor_plane
            win.blit(self.plane, (int(x), y + 20))
            self.coor_plane[0] -= 1.2

    def animation(self):
        if len(self.now_blocks) < self.max_block and self.count <= 0 or len(self.now_blocks) == 0:
            self.count = 10
            if len(self.now_blocks) < 8:
                self.new_generation_field()

        self.count -= 1
        c = 0
        for f in self.field:
            if f[22] == 0:
                c += 1

        if c <= 1:
            self.background_black.set_alpha(220)  # полупрозрачный черный
            self.update_win(0)
            self.background_black.set_alpha(0)

        if not self.now_animation:  # обрабатываем анимацию падения блоков в отдельном потоке
            self.now_animation = True
            thr_fall = threading.Thread(target=self.fall_blocks, args=(), name="fall_block")
            thr_fall.start()

    def move(self, player):
        """передвижение игрока"""
        right = player.coor_player[0] + self.size_pl[0]  # "x" правой части персонажа
        bottom = player.coor_player[1] + self.size_pl[1] + 23  # "y" нижней части персонажа + после падения

        x_before = player.coor_player[0]  # для отражения игрока
        y_before = player.coor_player[1]

        if pygame.key.get_pressed()[player.control['right']]:  # ходьба в право
            if player.direction == 2:
                player.fm_time = 0
            if player.coor_player[0] + self.size_pl[0] + player.speed >= self.field_size[0]:  # стенка справа
                player.coor_player[0] = self.field_size[0] - self.size_pl[0] - 1

            elif (self.field[(right + player.speed) // self.size_block][
                      len(self.field[0]) - player.coor_player[1] // self.size_block - 5] not in self.permeable_blocks) or \
                    self.field[(right + player.speed) // self.size_block][len(self.field[0]) - (
                            player.coor_player[1] + self.size_pl[1]) // self.size_block - 5] not in self.permeable_blocks:  # блок справа снизу и справа сверху, если есть, то передвигаемся вплотную к нему
                while (self.field[(player.coor_player[0] + self.size_pl[0] + 1) // self.size_block][
                           len(self.field[0]) - player.coor_player[
                               1] // self.size_block - 5] in self.permeable_blocks) and \
                        self.field[(player.coor_player[0] + self.size_pl[0] + 1) // self.size_block][
                            len(self.field[0]) - (player.coor_player[1] + self.size_pl[
                                1]) // self.size_block - 5] in self.permeable_blocks:
                    player.coor_player[0] += 1

                if pygame.key.get_pressed()[player.control['up']] and ((self.field[player.coor_player[0] // self.size_block][len(
                        self.field[0]) - bottom // self.size_block - 5] in self.permeable_blocks and
                 self.field[right // self.size_block][len(self.field[0]) - bottom // self.size_block - 5] in self.permeable_blocks) and bottom <self.field_size[1]):  # отскок от правой стены
                    player.isjump = True
                    player.fm_time = 2
                    player.direction = 1
                    player.jump_speed = 2
                    player.rebound_speed = 2.5
                    player.actual_x = player.coor_player[0]
            else:  # стенки и блока справа нет
                player.coor_player[0] += player.speed

        if pygame.key.get_pressed()[player.control['left']]:  # ходьба в лево
            if player.direction == 1:
                player.fm_time = 0
            if player.coor_player[0] - player.speed < 0:  # стенка слева
                player.coor_player[0] = 0
            elif self.field[(player.coor_player[0] - player.speed) // self.size_block][
                len(self.field[0]) - player.coor_player[1] // self.size_block - 5] not in self.permeable_blocks or \
                    self.field[(player.coor_player[0] - player.speed) // self.size_block][len(self.field[0]) - (
                    player.coor_player[1] + self.size_pl[1]) // self.size_block - 5] not in self.permeable_blocks:  # блок слева снизу и справа сверху,  если есть, то передвигаемся вплотную к нему
                if pygame.key.get_pressed()[player.control['up']] and ((self.field[player.coor_player[0] // self.size_block][len(
                        self.field[0]) - bottom // self.size_block - 5] in self.permeable_blocks and self.field[right // self.size_block][len(self.field[0]) - bottom // self.size_block - 5] in self.permeable_blocks) and bottom < self.field_size[1]):
                    player.isjump = True
                    player.fm_time = 2
                    player.direction = 2
                    player.jump_speed = 2
                    player.rebound_speed = 2.5
                    player.actual_x = player.coor_player[0]
                while (self.field[(player.coor_player[0] - 1) // self.size_block][len(self.field[0]) - player.coor_player[
                    1] // self.size_block - 5] in self.permeable_blocks) and \
                        self.field[(player.coor_player[0] - 1) // self.size_block][len(self.field[0]) - (
                                player.coor_player[1] + self.size_pl[1]) // self.size_block - 5] in self.permeable_blocks:
                    player.coor_player[0] -= 1
            else:  # стенки и блока справа нет
                player.coor_player[0] -= player.speed

        right = player.coor_player[0] + self.size_pl[0]  # "x" правой части персонажа
        bottom = player.coor_player[1] + self.size_pl[1] + int(
            player.jump_speed ** 2)  # "y" нижней части персонажа + после падения

        if pygame.key.get_pressed()[player.control['up']] and not player.isjump and not player.isfall:  # прыжок
            player.isjump = True
            player.jump_speed = 2

        if not player.isjump:  # падение
            if (self.field[player.coor_player[0] // self.size_block][
                    len(self.field[0]) - bottom // self.size_block - 5] in self.permeable_blocks and \
                self.field[right // self.size_block][
                    len(self.field[0]) - bottom // self.size_block - 5] in self.permeable_blocks) and \
                    bottom < self.field_size[1]:  # если снизу нет блока
                if player.jump_speed < 2:
                    player.jump_speed += 0.035  # 0.03 - ускорение свободного падения
                player.coor_player[1] += int(player.jump_speed ** 2)
            else:
                player.isfall = False
                player.jump_speed = 1
                player.coor_player[1] += self.size_block - ( (player.coor_player[1] + self.size_pl[1] - 1) % self.size_block) - 2

        if player.isjump:  # прыжок
            if player.jump_speed <= 1 or (self.field[player.coor_player[0] // self.size_block][len(self.field[0]) - (
                    player.coor_player[1] - int(
                    player.jump_speed ** 2)) // self.size_block - 5] not in self.permeable_blocks or
                                        self.field[(right) // self.size_block][len(self.field[0]) - (
                                                player.coor_player[1] - int(
                                                player.jump_speed ** 2)) // self.size_block - 5] not in self.permeable_blocks):
                while player.jump_speed > 1 and self.field[player.coor_player[0] // self.size_block][
                    len(self.field[0]) - (player.coor_player[1] - 1) // self.size_block - 5] in self.permeable_blocks and \
                        self.field[(right) // self.size_block][len(self.field[0]) - (
                                player.coor_player[1] - 1) // self.size_block - 5] in self.permeable_blocks:
                    player.coor_player[1] -= 1
                player.isjump = False
                player.isfall = True
                player.jump_speed = 1
            else:
                player.jump_speed -= 0.03
                player.coor_player[1] -= int(player.jump_speed ** 2)


        if player.fm_time > 0:  # отскокок
            player.rebound_speed -= 0.15
            if player.direction == 1 and not (int(player.actual_x - player.rebound_speed) < 0) and not (
                    self.field[(int(player.actual_x - player.rebound_speed)) // self.size_block][ len(self.field[0]) - player.coor_player[1] // self.size_block - 5] not in self.permeable_blocks or
                    self.field[(int(player.actual_x - player.rebound_speed)) // self.size_block][len(self.field[0]) - (player.coor_player[1] + self.size_pl[1]) // self.size_block - 5] not in self.permeable_blocks):  # отскок в лево
                player.actual_x -= player.rebound_speed
                player.coor_player[0] = int(player.actual_x)

            elif player.direction == 2 and not (int(player.actual_x + player.rebound_speed) + self.size_pl[0] >= self.field_size[0]) and not ((self.field[(int(player.actual_x + player.rebound_speed) + self.size_pl[0]) // self.size_block][len(self.field[0]) - player.coor_player[1] // self.size_block - 5] not in self.permeable_blocks) or self.field[(int(player.actual_x + player.rebound_speed) + self.size_pl[0]) // self.size_block][len(self.field[0]) - (player.coor_player[1] +self.size_pl[1]) // self.size_block - 5] not in self.permeable_blocks):
                player.actual_x += player.rebound_speed
                player.coor_player[0] = int(player.actual_x)

            else:  # если стенка
                player.fm_time = 0
            player.fm_time -= 0.1
            # player.speed -= 1

        if x_before > player.coor_player[0]:  # отражение персонажа по горизонтали
            player.reflaction_x = 1
        elif x_before < player.coor_player[0]:
            player.reflaction_x = 0

        # if y_before > player.coor_player[1]:  # отражение персонажа по горизонтали
        #     player.reflaction_y = 0
        # elif y_before < player.coor_player[1]:
        #     player.reflaction_y = 1

        win.blit(pygame.transform.flip(player.player_img, player.reflaction_x, player.reflaction_y), player.coor_player)
        if self.max_h >= self.height_helmet and player.img != 'w_amogus.png':    # появляется шлем (тк в космосе нет воздуха)
            win.blit(pygame.transform.flip(player.helmet, player.reflaction_x, player.reflaction_y), player.coor_player)

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
        if self.choice != 1:
            text = self.menu_font.render(f'Select mode: {self.mods[self.now_players]}', False, (255, 255, 255))
            win.blit(text, (self.field_size[0] // 10 + 2 * w, y + 4 * h))
        text = self.menu_font.render('Start', False, (255, 255, 255))
        win.blit(text, (self.field_size[0] // 10 + 2 * w, y + 5.5 * h))
        text = self.menu_font.render('Back', False, (255, 255, 255))
        win.blit(text, (self.field_size[0] // 10 + 2 * w, y + 7 * h))


        text = self.menu_font.render('>', False, (255, 255, 255))
        if self.choice == 0:  # skin
            if self.choice_pl == False:  # выбор скина
                text = self.menu_font.render('<      >', False, (255, 255, 255))
                win.blit(text, (self.field_size[0] // 10 + w, y + (3 + self.choice) * h))

                plr = pygame.image.load('./players/' + self.skins[self.skin_choice])
                self.players[self.player_choice].player_img = pygame.transform.scale(plr, (self.size_pl[0], self.size_pl[1]))
                self.players[self.player_choice].img = self.skins[self.skin_choice]

                plr = pygame.transform.scale(plr, (int(self.size_pl[0] * 1.5), int(self.size_pl[1] * 1.5)))
                prec = plr.get_rect(center=(self.field_size[0] // 10 + w + 43, y + (3 + self.choice) * h + 15))

                win.blit(plr, prec)
            else:   # выбор игрока
                text = self.menu_font.render(f'< Player {self.player_choice+1} >', False, (255, 255, 255))
                win.blit(text, (self.field_size[0] // 10 + w, y + (3 + self.choice) * h))

        elif self.choice == 1:  # режим
            text = self.menu_font.render(f'< {self.mods[self.now_players]} >', False, (255, 255, 255))
            win.blit(text, (self.field_size[0] // 10 + w, y + 4 * h))


        else:
            win.blit(text, (self.field_size[0] // 10 + w, y + (3 + self.choice) * h))
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
                            elif event.pos[0] <= self.field_size[0] // 10 + 2 * w - 10 + 15:
                                self.skin_choice -= 1
                                if self.skin_choice < 0:
                                    self.skin_choice = len(self.skins) - 1
                            elif event.pos[0] >= self.field_size[0] // 10 + 2 * w + 105 - 65:
                                self.skin_choice += 1
                                if self.skin_choice == len(self.skins):
                                    self.skin_choice = 0
                        elif event.pos[0] >= self.field_size[0] // 10 + 2 * w and event.pos[1] >= self.field_size[
                            1] // 5 + 5.5 * h and event.pos[0] <= self.field_size[0] // 10 + 2 * w + 105 and event.pos[
                            1] <= self.field_size[1] // 5 + 5.5 * h + 40:  # cтарт
                            self.menu2 = False
                            self.reset()
                        elif event.pos[0] >= self.field_size[0] // 10 + 2 * w and event.pos[1] >= self.field_size[
                            1] // 5 + 7 * h and event.pos[0] <= self.field_size[0] // 10 + 2 * w + 105 and event.pos[
                            1] <= self.field_size[1] // 5 + 7 * h + 40:  # cтарт
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

                    if self.choice == 0:  # skin
                        if self.choice_pl == False:     # выбор скина
                            if event.key == pygame.K_RIGHT:
                                self.skin_choice += 1
                                if self.skin_choice == len(self.skins):
                                    self.skin_choice = 0

                            if event.key == pygame.K_LEFT:
                                self.skin_choice -= 1
                                if self.skin_choice < 0:
                                    self.skin_choice = len(self.skins) - 1

                        else:   # выбор игрока
                            if event.key == pygame.K_RIGHT:
                                self.player_choice += 1
                                if self.player_choice == len(self.players):
                                    self.player_choice = 0

                            if event.key == pygame.K_LEFT:
                                self.player_choice -= 1
                                if self.player_choice < 0:
                                    self.player_choice = len(self.players) - 1

                    elif self.choice == 1:
                        if event.key == pygame.K_RIGHT:
                            self.now_players += 1
                            if self.now_players == len(self.players)+1:
                                self.now_players = 1

                        if event.key == pygame.K_LEFT:
                            self.now_players -= 1
                            if self.now_players < 1:
                                self.now_players = len(self.players)

                    if event.key == pygame.K_RETURN:
                        if self.choice == 0:
                            if self.choice_pl == False: # номер игрока
                                self.choice_pl = True
                            else:   # скин

                                self.choice_pl = False
                        elif self.choice == 1:  # режим
                            pass

                        elif self.choice == 2.5:  # cтарт
                            # if self.skins[self.skin_choice] == 'player5.png':
                            #     icon = pygame.image.load('img/brawl.png')
                            #     icon = pygame.transform.scale(icon, (64, 64))
                            #     pygame.display.set_icon(icon)
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
        win.blit(text, (self.field_size[0] // 5 + w, y + h * self.choice))
        pygame.display.update()

    def main_menu(self):
        self.play = False
        self.scoreboard = False
        self.menu2 = False
        self.menu = True

        self.count = 0  # для двух падующих блоков в self.animation()
        self.max_block = 2  # 2 падующих блока
        self.block_drop_time = 0.07

        self.choice = 0

        try:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load("music/menu.mp3")
                pygame.mixer.music.play(-1)
                if not self.play_music:
                    pygame.mixer.music.pause()
        except Exception:
            print('наушники')
            self.play_music = False

        while self.menu:
            if not self.now_animation:
                self.animation()

            for event in pygame.event.get():  # пауза на C
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if (event.button == 1):  # нажата левая кнопка
                        if (event.pos[0] >= self.field_size[0] // 5 + 20 and event.pos[1] >= self.field_size[1] // 2 and
                                event.pos[0] <= self.field_size[0] // 5 + 20 + 105 and event.pos[1] <= self.field_size[
                                    1] // 2 + 40):  # cтарт
                            self.choice = 0
                            self.menu = False
                            self.menu2 = True
                            self.start_game_menu()
                        elif (event.pos[0] >= self.field_size[0] // 5 + 20 and event.pos[1] >= self.field_size[
                            1] // 2 + 50 and event.pos[0] <= self.field_size[0] // 5 + 20 + 105 and event.pos[1] <=
                              self.field_size[1] // 2 + 40 + 50):  # scoreboard
                            self.choice = 0
                            self.menu = False
                            self.scoreboard = True
                            self.start_scoreboard()
                        elif (event.pos[0] >= self.field_size[0] // 5 + 20 and event.pos[1] >= self.field_size[
                            1] // 2 + 100 and event.pos[0] <= self.field_size[0] // 5 + 20 + 105 and event.pos[1] <=
                              self.field_size[1] // 2 + 40 + 100):  # scoreboard:
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
                    if event.key == pygame.K_RETURN:  # нажата левая кнопка
                        if self.choice == 0:  # cтарт
                            self.menu = False
                            self.menu2 = True
                            self.start_game_menu()
                        elif self.choice == 1:  # scoreboard
                            self.menu = False
                            self.scoreboard = True
                            self.start_scoreboard()
                        else:  # exit
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

            for event in pygame.event.get():  # пауза на C
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if (event.button == 1):  # нажата левая кнопка
                        if (self.field_size[0] // 10 + 25 and event.pos[1] >= self.field_size[1] // 7 + 8.5 * 50 and
                                event.pos[0] <= self.field_size[0] // 10 + 25 + 105 and event.pos[1] <= self.field_size[
                                    1] // 7 + 8.5 * 50 + 40):  # cтарт
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
                    if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:  # back
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
        win.blit(text, (self.field_size[0] // 10 + w, y + 8.5 * h))

        text = self.menu_font.render('>', False, (255, 255, 255))
        win.blit(text, (self.field_size[0] // 10, y + 8.5 * h))

        text = self.menu_font.render('Score', False, (255, 255, 255))
        win.blit(text, (self.field_size[0] // 10 + w, y + 2 * h))
        text = self.menu_font.render('Time', False, (255, 255, 255))
        win.blit(text, (self.field_size[0] // 2 - w - w, y + 2 * h))

        m = 5  # число рекордов
        for i in range(1, m + 1):
            text = self.menu_font.render(str(i) + '.', False, (255, 255, 255))
            win.blit(text, (self.field_size[0] // 10, y + (2 + i) * h))

        for i, s in enumerate(self.score_data):
            i += 1
            text = self.menu_font.render(str(s[0]), False, (255, 255, 255))
            win.blit(text, (self.field_size[0] // 10 + w + 10, y + (2 + i) * h))

            text = self.menu_font.render(str(s[1]), False, (255, 255, 255))
            win.blit(text, (self.field_size[0] // 2 - w - w, y + (2 + i) * h))
            if i == m:
                break

        pygame.display.update()

    def score(self):
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
                    win.blit(self.color_blocks[4], (x * 24, y_win * 24))

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
                        (now_space == x_info[1] and stop_h == x_info[2] and randint(0, 1) and block != [
                            [1, 1, 1, 1]]):  # палку ставим вплотную
                    x_info[2] = stop_h
                    x_info[1] = now_space
                    x_info[0] = x
                    now_block = block
        for i in range(len(now_block)):
            self.height[x_info[0] + i] = x_info[2] + len(now_block[i])  # пересчитываем высоту после падения блока

        for player in self.players[:self.now_players]:
            if player.img == 'mario.png' or player.img == 'luigi.png':  # если скин марио, то генерируется блок с вопросом
                color = randint(1, 5)
                break
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

    def check_death(self, player, place, x, y, i):
        if ((player.coor_player[0] + 1) // self.size_block == place + x or (player.coor_player[0] + 15) // 24 == place + x) and len(self.field[0]) - (player.coor_player[1] + 20) // 24 - 5 == y + i:
            self.play = False
            self.now_animation = True
            self.house = False
            return True

        elif self.play == True and self.field[player.coor_player[0] // 24][len(self.field[0]) - 5 + 1 - player.coor_player[1] // 24] >= 1 \
            and (player.coor_player[0] // 24 - 1 == -1 or self.field[player.coor_player[0] // 24 - 1][ len(self.field[0]) - 5 - player.coor_player[1] // 24] >= 1) \
            and (player.coor_player[0] // 24 + 1 == 18 or self.field[player.coor_player[0] // 24 + 1][len(self.field[0]) - 5 - player.coor_player[1] // 24]):
            if self.house and int(end()) >= self.time_house:
                self.play = False
                self.now_animation = True
                return True
            elif not self.house:
                self.house = True
                start()
        return False

    def fall(self, block, stop_h, place, y, y_win, color):
        """анимация падения блока"""
        if y > stop_h:
            for x in range(len(block)):
                for i, b in enumerate(block[x]):  # стираем поле, где был блок
                    if b == 1 or b == 2 or b == 3 or b == 4:
                        self.field[place + x][y + i] = 0
            y -= 1
            y_win += 1
            for x in range(len(block)):  # заполняем поле блоком в текущем y
                for i, b in enumerate(block[x], 0):
                    if b == 1 or b == 2 or b == 3 or b == 4:
                        self.field[place + x][y + i] = color
                        if not self.play:
                            win.blit(self.color_blocks[color - 1], ((place + x) * 24, (y_win - i) * 24))
                        else:
                            for player in self.players[:self.now_players]:
                                try:
                                    if self.check_death(player, place, x, y, i):
                                        return True
                                except TypeError:
                                    print("ОШИБКА")
                                    print(self.field[player.coor_player[0] // 24][len(self.field[0]) - 5 + 1 - player.coor_player[1] // 24])
                                    print(self.field[player.coor_player[0] // 24 - 1][ len(self.field[0]) - 5 - player.coor_player[1] // 24])

            self.now_blocks[self.i] = [block, stop_h, place, y, y_win, self.now_blocks[self.i][5]]
        else:
            try:
                self.now_blocks.remove([block, stop_h, place, y, y_win, self.now_blocks[self.i][5]])
            except ValueError:
                pass

        row_pl = max([len(self.field[0]) - pl.coor_player[1]//24-5 for pl in self.players])  # Y персонажа
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
                for pl in self.players[:self.now_players]:
                    pl.coor_player[1] += 24

    def death_menu(self):
        self.insert_in_scoreboard()
        print('вы проиграли!')
        self.score()
        w, h = pygame.display.get_surface().get_size()
        pygame.draw.rect(win, (0, 0, 0), (0, 0, w, h))
        text1 = self.gameover_title.render('GAME OVER!', True, (255, 255, 255))
        text_rect = text1.get_rect(center=(w / 2, h / 2 - 190))
        win.blit(text1, text_rect)
        text1 = self.menu_font.render('Score: ' + str(self.max_h), True, (255, 255, 255))
        win.blit(text1, (w / 3 + 10, h / 2 - 130))

        win.blit(self.fail, (w / 3 + 10, h / 2 + 80))

        if self.house:
            funny_text = self.special_taunts[2]  # в домике
        elif self.max_h == 13 or self.max_h == 33 or self.max_h == 66 or self.max_h == 99 or self.max_h == 666 or self.max_h == 999:
            funny_text = self.special_taunts[0]  # бугагашеньки
        elif self.max_h == 0:
            funny_text = self.special_taunts[1]  # специально умер??
        else:
            funny_text = self.taunts[randint(0, len(self.taunts) - 1)]
            if funny_text == 'Вы проиграли в какой-то раз':
                self.cur = self.con.cursor()
                count = self.cur.execute(f"""SELECT count(*) FROM scoreboard""")
                for deaths in count:
                    pass
                funny_text = f'Вы проиграли в {deaths[0]} раз'

            for player in self.players[:self.now_players]:
                if funny_text == 'Вы любите фурри?' and player.img != 'medw_fur.png':
                    funny_text = self.taunts[4]

        lines = funny_text.splitlines()
        for i, l in enumerate(lines):
            text1 = self.fifaks_font.render(l, True, (255, 255, 255))
            if len(lines) == 1:
                text_rect = text1.get_rect(center=(w / 2, h / 2 - 50 + (i * 20) - ((len(lines) - 1) * 20) - 5))
            else:
                text_rect = text1.get_rect(center=(w / 2, h / 2 - 50 + (i * 20) - ((len(lines) - 1) * 20) + 7))
            win.blit(text1, text_rect)

        if self.play_music:
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
                        if (event.pos[0] >= self.field_size[0] // 5 + w and event.pos[1] >= self.field_size[1] // 2 and
                                event.pos[0] <= self.field_size[0] // 5 + w + 105 and event.pos[1] <= self.field_size[1] // 2 + 40):  # cтарт
                            self.reset()
                            return True
                        elif (event.pos[0] >= self.field_size[0] // 5 + w and event.pos[1] >= self.field_size[
                            1] // 2 + 50 and event.pos[0] <= self.field_size[0] // 5 + w + 105 and event.pos[1] <=
                              self.field_size[1] // 2 + 40 + 50):  # cтарт
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

