# tetge - tetris + dodge
import datetime
import os
import sys
import threading
import time
from random import randint

import pyautogui

import pygame
import pygame.mixer
import sqlite3

from pygame import RESIZABLE

class Timer():
    def __init__(self):  # таймер
        self.st = time.time()

    def end(self):
        return float("%.2f" % (time.time() - self.st))

class Character():
    def set_player(self, coor_player, control={'left':pygame.K_LEFT, 'up':pygame.K_UP, 'right':pygame.K_RIGHT}, img = 1):
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

# class FallingBlock():
#     def __init__(self, block_shape, stop_height, x, y, interval, color):
#         self.block_shape = block_shape
#         self.stop_height = stop_height # высота, на которой остановится блок после падения
#         self.x = x  # координаты верхнего
#         self.y = y  # левого блока
#         self.timer = interval   # интервал перед появлением нового блока
#         self.color = color

class Test():
    def start_tests(self):
        def open_main_menu(self):
            time.sleep(1)
            print('test open_main_menu', self.main_menu_open)

        def open_scoreboard(self):
            pyautogui.press('down', interval = 0.5)
            pyautogui.click(x=910,y=610, interval = 1)
            print('test open_scoreboard', not self.main_menu_open and self.scoreboard_open)

        def back_main_menu_from_scoreboard(self):
            pyautogui.click(x=848,y=770, interval=1)
            print('test back_main_menu_from_scoreboard', self.main_menu_open and not self.scoreboard_open)

        def open_start_menu(self):
            pyautogui.click(x=890,y=560, interval = 1.5)
            print('test open_start_menu', not self.main_menu_open and self.start_game_menu_open)

        def change_skin_for_2_player(self):
            before_skin = self.player_two.player_img
            pyautogui.press('right', interval = 0.5)
            pyautogui.click(x=900, y=540, interval = 1)
            pyautogui.press('left', interval = 0.5)
            print('test change_skin_for_2_player', before_skin != self.player_two.player_img)

        def change_mode(self):
            before_mode = self.now_players
            pyautogui.press('down', interval = 0.5)
            pyautogui.press('right', interval = 0.5)
            status = False
            if before_mode != self.now_players:
                status = True
            pyautogui.press('left', interval = 0.5)
            print('test change_mode', status and before_mode == self.now_players)

        def test_music(self):
            self.play_stop_music()
            time.sleep(1)
            status = not pygame.mixer.music.get_busy()
            self.play_stop_music()
            print('test test_music', status and pygame.mixer.music.get_busy())

        def start_game(self):
            pyautogui.press('down', interval=0.5)
            pyautogui.click(x=880, y=660, interval = 1)
            print('test start_game', not self.start_game_menu_open and self.play)

        def open_game_rules(self):
            print('test open_game_rules', self.open_game_rules)

        def close_game_rules(self):
            while self.open_game_rules:
                pass
            print('test close_game_rules', not self.open_game_rules)

        def open_game_over(self):
            while self.play:
                pass
            print('test open_game_over', self.open_death_menu)

        def back_main_menu_from_death_menu(self):
            pyautogui.press('down', interval=1.5)
            pyautogui.click(x=890, y=610, interval = 1)
            print('test back_main_menu_from_death_menu', not self.open_death_menu and self.main_menu_open)

        def close_app():
            pyautogui.press('down', interval=0.5)
            pyautogui.press('down', interval=0.5)
            pyautogui.click(x=880, y=650, interval = 1)
            print('test close_app', True)

        tetge_self = B.game
        open_main_menu(tetge_self)
        open_scoreboard(tetge_self)
        back_main_menu_from_scoreboard(tetge_self)
        open_start_menu(tetge_self)
        change_skin_for_2_player(tetge_self)
        change_mode(tetge_self)
        test_music(tetge_self)
        start_game(tetge_self)
        open_game_rules(tetge_self)
        close_game_rules(tetge_self)
        open_game_over(tetge_self)
        back_main_menu_from_death_menu(tetge_self)
        close_app()

class Tetge():
    def setting(self):
        """настройки игры"""
        pygame.font.init()

        try:
            pygame.mixer.init()
        except Exception:
            print('подключите наушники')

        self.blocks = [[[1, 1], [1, 1]],  # квадрат
                       [[1, 1], [1, 0], [1, 0]],  # Г фигура
                       [[1, 1], [0, 1], [0, 1]],  # Г фигура отраженная
                       [[1, 1, 1], [0, 1, 0]],  # т
                       [[1, 1, 1, 1]],          # палка
                       [[0, 1, 1], [1, 1, 0]],  # зигзаг
                       [[1, 1, 0], [0, 1, 1]]]  # зигзаг отраженный

        self.size_pl = [17, 20]  # размер персонажа в пикселях
        self.size_block = 24  # размер блока
        self.speed_game = 6 # скорость игры
        self.permeable_blocks = [0]  # блоки, через которые игрок может проходить (воздух и в будущем бонусы)
        self.block_drop_time = 0.041  # время за которое падующий блок преодалевает 1 блок
        self.block_drop_time_start = 0.045
        self.jump_speed_const = 2

        self.skin_choice = 0
        self.field_size = [24 * 18, 24 * 24]  # размер поля в пикселях
        mypath = './players'
        self.skins = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]

        self.helmet_one = pygame.image.load(self.android_path + 'img/helmet_one.png').convert_alpha()   # шлем для космоса (с 42)
        self.helmet_two = pygame.image.load(self.android_path + 'img/helmet_two.png').convert_alpha()   # шлем для космоса (с 42)

        self.plane = pygame.image.load(self.android_path + 'img/plane.png').convert_alpha()     # самолет
        self.background = pygame.image.load(self.android_path + 'img/background.png').convert_alpha()
        self.fail = pygame.image.load(self.android_path + 'img/fail.png').convert_alpha()
        self.fail = pygame.transform.scale(self.fail, (150, 163))
        self.arrow = pygame.image.load(self.android_path + 'img/arrow.png').convert_alpha()
        self.arrow = pygame.transform.scale(self.arrow, (70, 35))
        self.crown = pygame.image.load(self.android_path + 'img/crown.png').convert_alpha()
        self.crown = pygame.transform.scale(self.crown, (30, 24))
        self.color_blocks = [pygame.image.load(self.android_path + 'img/cube1.png').convert_alpha(),
                             pygame.image.load(self.android_path + 'img/cube2.png').convert_alpha(),
                             pygame.image.load(self.android_path + 'img/cube3.png').convert_alpha(),
                             pygame.image.load(self.android_path + 'img/cube4.png').convert_alpha(),
                             pygame.image.load(self.android_path + 'img/cube5.png').convert_alpha()]
        self.left = pygame.image.load(self.android_path + 'img/left.png').convert_alpha()
        self.left = pygame.transform.scale(self.left, (70, 70))
        self.right = pygame.image.load(self.android_path + 'img/right.png').convert_alpha()
        self.right = pygame.transform.scale(self.right, (70, 70))
        self.up = pygame.image.load(self.android_path + 'img/up.png').convert_alpha()
        self.up = pygame.transform.scale(self.up, (70, 70))


        try:
            pygame.mixer.music.load(self.android_path + "music/game.mp3")  # музыка при запуске игры
        except Exception:
            print('наушники')

        self.rules_font = pygame.font.SysFont("comicsansms", 24)
        self.add_font2 = pygame.font.SysFont("Times New Roman", 15)
        self.add_font = pygame.font.SysFont("Times New Roman", 30)
        self.gameover_title = pygame.font.Font(self.android_path + "fonts/failed attempt.ttf", 70)
        self.score_title = pygame.font.Font(self.android_path + "fonts/SUBWT___.ttf", 32)
        self.menu_font = pygame.font.Font(self.android_path + "fonts/SUBWT___.ttf", 28)
        self.game_title = pygame.font.Font(self.android_path + "fonts/Blox2.ttf", 98)
        self.creators = pygame.font.Font(self.android_path + "fonts/SUBWT___.ttf", 16)
        self.fifaks_font = pygame.font.Font(self.android_path + "fonts/Fifaks10Dev1.ttf", 24)

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
        self.height_fly_plane = 26
        self.height_helmet = 42

        self.now_players = 1

        plr = pygame.image.load(self.android_path + 'players/' + self.skins[0]).convert_alpha()
        player_img = pygame.transform.scale(plr, (self.size_pl[0], self.size_pl[1]))

        # игроки
        self.player_one = Character()
        self.player_one.set_player(coor_player=[192 - 10, self.field_size[1] - self.size_pl[1] - 2], img=player_img)
        self.player_two = Character()
        self.player_two.set_player(coor_player=[192 + 10, self.field_size[1] - self.size_pl[1] - 2],
                                control={'left': pygame.K_a, 'up': pygame.K_w, 'right': pygame.K_d}, img=player_img)
        self.players = []
        self.players.append(self.player_one)
        self.players.append(self.player_two)

        # self.player_three = character()
        # self.player_three.set_player(coor_player=[192 + 40, self.field_size[1] - self.size_pl[1] - 2],
        #                         control={'left': pygame.K_KP1, 'up': pygame.K_KP5, 'right': pygame.K_KP3}, img=player_img)
        # self.players.append(self.player_three)

        self.player_one.player_img = pygame.transform.scale(player_img, (self.size_pl[0], self.size_pl[1]))
        self.player_two.player_img = pygame.transform.scale(pygame.image.load(self.android_path + 'players/' + self.skins[-2]).convert_alpha(), (self.size_pl[0], self.size_pl[1]))
        self.player_one.helmet = self.helmet_one
        self.player_two.helmet = self.helmet_two

        self.timer_animation = Timer()
        self.timer_animation2 = Timer()

    def play_music(self, music):
        try:
            pygame.mixer.music.load(self.android_path + f"music/{music}")  # музыка при запуске игры
        except Exception:
            print('наушники')

    def reset(self):
        try:
            pygame.mixer.music.load(self.android_path + "music/game.mp3")  # музыка при запуске игры
        except Exception:
            print('наушники')

        win.fill((0, 0, 0))
        self.max_h = 11  # значение максимальной достигнутой высоты персонажем

        self.field = []  # поле 24 на 18
        self.falling_blocks = []  # блоки в падении
        self.now_animation = False  # обозначает, что сейчас не происходит прорисовка падения блоков
        self.house = False
        self.time_house = 5
        self.timer_house = Timer()
        self.coor_plane = [self.field_size[0], 15]

        for i in range(self.field_size[0] // self.size_block):
            self.field.append([0] * (self.field_size[1] // self.size_block + 4))  # одновременно видно будет только 24 клетки (вверх) и 18 клеток в ширину

        self.height = [0] * (self.field_size[0] // self.size_block)  # высота каждого столбца
        # self.coor_player = [192, self.field_size[1]-self.size_pl[1]-2]   # начальные координаты игрока

        self.t = 0  # замедление после появления нового падующего блока
        self.max_block = 1  # кол-во одновременно падующих блоков
        self.play = True

        self.background_black = pygame.image.load(self.android_path + 'img/black.png').convert_alpha()
        self.background_black.set_alpha(130)  # полупрозрачный черный

        x = self.field_size[0]//2 + 10
        for player in self.players:
            player.coor_player = [x, self.field_size[1] - self.size_pl[1] - 2]
            x-=20

        if not self.main_menu_open and self.play_music:
            pygame.mixer.music.play(-1)
            if not self.play_music:
                pygame.mixer.music.pause()

    def start_game(self, path = '', test = False):
        self.android_path = path
        self.DataBase()
        try:
            pygame.mixer.init()
            self.play_music = True
        except Exception:
            print('подключите наушники')
            self.play_music = False
        self.main_menu_open = True

        self.player_choice = 0
        self.choice_pl = True
        self.skin_choice = 0
        # self.mode_choice = 1    # по факту число игроков
        self.mods = ['тут выбираем режим игры', 'Classic', '2 players', '3 players']
        self.pause_play = False
        self.setting()
        self.reset()

        if test:
            testing_app = Test()
            thr_testing = threading.Thread(target=testing_app.start_tests, args=(), name="testing")
            thr_testing.start()

        self.main_menu()
        self.reset()

        # self.win_img()
        win.blit(self.background, (0, 0), (0, 2880 - 24 * 24, 24 * 18, 24 * 24))
        self.score()
        for player in self.players[:self.now_players]:
            win.blit(player.player_img, player.coor_player)

        self.game_rules()  # правила игры (5 секунд)

        win.blit(self.background, (0, 0), (0, 2304 - 24 * 24, 24 * 18, 24 * 24))
        while 1:
            if not self.play:
                self.death_menu()
            pygame.time.delay(6)

            for event in pygame.event.get():  # пауза на C
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        self.play_stop_music()
                    if event.key == pygame.K_ESCAPE:
                        self.pause_play = True

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if self.pause_play:
                self.pause_menu()
            else:
                self.win_img()
                for player in self.players[:self.now_players]:
                    self.move(player)
                self.window_resize()
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

                if (len(self.falling_blocks) < self.max_block or self.falling_blocks[-1][4] == intrv) and len(self.falling_blocks) < 8:
                    self.new_generation_field()

                if self.timer_animation.end() >= self.block_drop_time:
                    self.fall_blocks()
                    self.timer_animation = Timer()

    def win_img(self):
        """
        выводим все изображения (задний фон, самолет, блоки, очки)
        :return:
        """
        self.draw_background()
        self.plane_animation()
        self.update_win(2)
        self.score()

    def draw_background(self):
        if self.max_h > 72:
            x = (self.max_h - 72)%24
            win.blit(self.background, (0, 0), (
                0, 2880 - (24 + max(0, 72+x)) * 24, 24 * 18, 24 * 24))  # отрисовка и  прокрутка заднего фона
        else:
            win.blit(self.background, (0, 0), (
            0, 2880 - (24 + max(0, self.max_h - 11)) * 24, 24 * 18, 24 * 24))  # отрисовка и  прокрутка заднего фона

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

            self.text_resume = self.output_text('Resume', self.field_size[0] // 5 + w, y+h)
            self.text_menu = self.output_text('Menu', self.field_size[0] // 5 + w, y + 2*h)

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
            self.window_resize()

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # нажата левая кнопка мыши
                    mouse = pygame.mouse.get_pos()
                    if self.rect_resize(self.text_resume).collidepoint(mouse) or self.rect_resize(self.text_menu).collidepoint(mouse):    # resume
                        self.pause_play = False
                        try:
                            print(pygame.mixer.music.get_busy())
                            if not pygame.mixer.music.get_busy():
                                pygame.mixer.music.unpause()
                                self.play_music = True
                        except Exception:
                            print('подключите наушники')
                            self.play_music = False
                    if self.rect_resize(self.text_resume).collidepoint(mouse):
                        return
                    if self.rect_resize(self.text_menu).collidepoint(mouse):
                        self.main_menu_open = True
                        self.play = False
                        self.now_animation = False
                        self.house = False
                        self.reset()
                        return self.main_menu()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:     # пауза на C
                        self.play_stop_music()

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

                        if self.choice == 1:  # resume
                            return
                        elif self.choice == 2:  # меню
                            self.main_menu_open = True
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
        self.open_game_rules = True
        text_dodge = self.fifaks_font.render('Уворачивайся от блоков.', False, (255, 255, 255))
        win.blit(text_dodge, (88, 100))

        text_dodge = self.fifaks_font.render('Управляй стрелочками.', False, (255, 255, 255))
        win.blit(text_dodge, (96, 140))
        win.blit(self.arrow, (self.field_size[0] // 2 - 35, 190))

        self.window_resize()
        pygame.display.update()

        wait = 4
        rules_time = Timer()
        skip = False
        while rules_time.end() <= wait and not skip:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:     # пауза на C
                        self.play_stop_music()

                    if event.key == pygame.K_RETURN:
                        skip = True

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
        self.open_game_rules = False

    def plane_animation(self):
        if self.max_h >= self.height_fly_plane:
            self.coor_plane[1] = 35 + (self.max_h - self.height_fly_plane) * 24
            x, y = self.coor_plane
            win.blit(self.plane, (int(x), y + 20))
            self.coor_plane[0] -= 1.2

    def animation(self):
        if len(self.falling_blocks) < self.max_block and self.count <= 0 or len(self.falling_blocks) == 0:
            self.count = 10
            if len(self.falling_blocks) < 8:
                self.new_generation_field()

        self.count -= 1
        c = 0
        for f in self.field:
            if f[22] == 0:
                c += 1

        if c <= 1:
            # self.background_black.set_alpha(220)  # полупрозрачный черный
            self.update_win(0)
            # self.background_black.set_alpha(0)

        # if not self.now_animation:  # обрабатываем анимацию падения блоков в отдельном потоке
        #     self.now_animation = True
        #     thr_fall = threading.Thread(target=self.fall_blocks, args=(), name="fall_block")
        #     thr_fall.start()

        if self.timer_animation.end() >= self.block_drop_time:
            self.fall_blocks()
            self.timer_animation = Timer()

    def move(self, player):
        """передвижение игрока"""
        def draw_control():
            y = self.field_size[1] + 20
            x = self.field_size[0]//10
            left_rect = win.blit(self.left, (x, y))
            right_rect = win.blit(self.right, (x+90, y))
            up_rect = win.blit(self.up, (self.field_size[0]-120, y))
            return self.rect_resize(left_rect), self.rect_resize(right_rect), self.rect_resize(up_rect)
        left_rect, right_rect, up_rect = draw_control()

        right = player.coor_player[0] + self.size_pl[0]  # "x" правой части персонажа
        bottom = player.coor_player[1] + self.size_pl[1] + 23  # "y" нижней части персонажа + после падения

        x_before = player.coor_player[0]  # для отражения игрока
        y_before = player.coor_player[1]

        mouse = pygame.mouse.get_pos()
        if pygame.key.get_pressed()[player.control['right']] or right_rect.collidepoint(mouse):  # ходьба в право
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
                    player.jump_speed = self.jump_speed_const
                    player.rebound_speed = 2.5
                    player.actual_x = player.coor_player[0]
            else:  # стенки и блока справа нет
                player.coor_player[0] += player.speed

        if pygame.key.get_pressed()[player.control['left']] or left_rect.collidepoint(mouse):  # ходьба в лево
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
                    player.jump_speed = self.jump_speed_const
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

        if (pygame.key.get_pressed()[player.control['up']] or up_rect.collidepoint(mouse)) and not player.isjump and not player.isfall:  # прыжок
            player.isjump = True
            player.jump_speed = self.jump_speed_const

        if not player.isjump:  # падение
            if (self.field[player.coor_player[0] // self.size_block][
                    len(self.field[0]) - bottom // self.size_block - 5] in self.permeable_blocks and \
                self.field[right // self.size_block][
                    len(self.field[0]) - bottom // self.size_block - 5] in self.permeable_blocks) and \
                    bottom < self.field_size[1]:  # если снизу нет блока
                if player.jump_speed < self.jump_speed_const:
                    player.jump_speed += 0.035  # 0.03 - ускорение свободного падения
                player.coor_player[1] += int(player.jump_speed ** 2)
            else:
                player.isfall = False
                player.jump_speed = 1
                player.coor_player[1] += self.size_block - ((player.coor_player[1] + self.size_pl[1] - 1) % self.size_block) - 2

        if player.isjump:  # прыжок
            if player.jump_speed <= 1 or (self.field[player.coor_player[0] // self.size_block][len(self.field[0]) - (player.coor_player[1] - int(player.jump_speed ** 2)) // self.size_block - 5] not in self.permeable_blocks or
                    self.field[(right) // self.size_block][len(self.field[0]) - (player.coor_player[1] - int(player.jump_speed ** 2)) // self.size_block - 5] not in self.permeable_blocks):
                while player.jump_speed > 1 and self.field[player.coor_player[0] // self.size_block][
                    len(self.field[0]) - (player.coor_player[1] - 1) // self.size_block - 5] in self.permeable_blocks and \
                    self.field[(right) // self.size_block][len(self.field[0]) - (player.coor_player[1] - 1) // self.size_block - 5] in self.permeable_blocks:
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

    def play_stop_music(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.play_music = False
        else:
            self.play_music = True
            pygame.mixer.music.unpause()

    def start_game_menu(self):
        self.draw_start_game_menu()

        while self.start_game_menu_open:
            self.window_resize()
            if self.timer_animation.end() >= self.block_drop_time:
                self.animation()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # нажата левая кнопка мыши
                    mouse = pygame.mouse.get_pos()
                    if self.choice != 0 and self.rect_resize(self.text_skin).collidepoint(mouse): # select skin
                        self.choice = 0
                    elif self.rect_resize(self.text_start_game).collidepoint(mouse):  # cтарт
                        self.start_game_menu_open = False
                        self.reset()
                    elif self.rect_resize(self.text_back_start).collidepoint(mouse):  # back
                        self.start_game_menu_open = False
                        self.main_menu_open = True
                    elif self.rect_resize(self.text_mode).collidepoint(mouse) and self.choice != 1:    # mode
                        self.choice = 1
                    elif self.choice == 1:  # выбор режима
                        if self.rect_resize(self.text_mode_prev).collidepoint(mouse):
                            self.now_players -= 1
                            if self.now_players < 1:
                                self.now_players = len(self.players)
                        elif self.rect_resize(self.text_mode_next).collidepoint(mouse):
                            self.now_players += 1
                            if self.now_players == len(self.players) + 1:
                                self.now_players = 1
                    elif self.choice_pl == True and self.choice == 0:  # выбор игрока
                        if self.rect_resize(self.text_player).collidepoint(mouse):
                            if self.choice_pl == False:  # номер игрока
                                self.choice_pl = True
                            else:  # скин
                                self.choice_pl = False
                        elif self.rect_resize(self.text_player_prev).collidepoint(mouse): # select player <
                            self.player_choice -= 1
                            if self.player_choice < 0:
                                self.player_choice = len(self.players) - 1
                        elif self.rect_resize(self.text_player_next).collidepoint(mouse): # select player >
                            self.player_choice += 1
                            if self.player_choice == len(self.players):
                                self.player_choice = 0
                    elif self.choice_pl == False and self.choice == 0:  # выбор скина
                        if self.rect_resize(self.text_skin_prev).collidepoint(mouse):    # select skin <
                            self.skin_choice -= 1
                            if self.skin_choice < 0:
                                self.skin_choice = len(self.skins) - 1
                        elif self.rect_resize(self.text_skin_next).collidepoint(mouse):   # select skin <
                            self.skin_choice += 1
                            if self.skin_choice == len(self.skins):
                                self.skin_choice = 0
                        elif self.rect_resize(self.skin_coor).collidepoint(mouse):
                            self.choice_pl = True

                if event.type == pygame.KEYDOWN:    # нажатие клавишы
                    if event.key == pygame.K_c: # музыка
                        self.play_stop_music()

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

                    elif self.choice == 1:  # mode
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
                            #     icon = pygame.image.load(self.android_path + 'img/brawl.png').convert_alpha()
                            #     icon = pygame.transform.scale(icon, (64, 64))
                            #     pygame.display.set_icon(icon)
                            self.start_game_menu_open = False
                            self.reset()

                        elif self.choice == 4:  # back
                            self.start_game_menu_open = False
                            self.main_menu_open = True
                            self.choice = 0

                    elif event.key == pygame.K_ESCAPE:
                        self.start_game_menu_open = False
                        self.main_menu_open = True
                        self.choice = 0

    def draw_start_game_menu(self):
        # win.blit(self.background_black, (0, 0))
        w = 25  # x
        h = 50  # y
        y = self.field_size[1] // 5
        x = self.field_size[0] // 10
        text = self.gameover_title.render('START GAME', False, (255, 255, 255))
        win.blit(text, (self.field_size[0] // 9 + w, y))
        if self.choice != 0:
            self.text_skin = self.output_text('Select skin', x + 2 * w, y + 3 * h)
        if self.choice != 1:
            self.text_mode = self.output_text(f'Select mode: {self.mods[self.now_players]}', x + 2 * w, y + 4 * h)

        self.text_start_game = self.output_text('Start', self.field_size[0] // 10 + 2 * w, y + 5.5 * h)
        self.text_back_start = self.output_text('Back', self.field_size[0] // 10 + 2 * w, y + 7 * h)

        text = self.menu_font.render('>', False, (255, 255, 255))
        if self.choice == 0:  # skin
            if self.choice_pl == False:  # выбор скина
                self.text_skin_prev = self.output_text('<', self.field_size[0] // 10 + w, y + (3 + self.choice) * h)

                plr = pygame.image.load(self.android_path + 'players/' + self.skins[self.skin_choice]).convert_alpha()
                self.players[self.player_choice].player_img = pygame.transform.scale(plr, (self.size_pl[0], self.size_pl[1]))
                self.players[self.player_choice].img = self.skins[self.skin_choice]
                self.skin_coor = plr.get_rect(center = self.text_rect_left(plr, self.field_size[0] // 10 + w + 43, y + (3 + self.choice) * h ))

                self.text_skin_next = self.output_text('>', self.skin_coor[0] + 55, self.skin_coor[1])
                plr = pygame.transform.scale(plr, (int(self.size_pl[0] * 1.5), int(self.size_pl[1] * 1.5)))
                win.blit(plr, self.skin_coor)
            else:   # выбор игрока
                self.text_player = self.output_text(f'Player {self.player_choice+1}', self.field_size[0] // 10 + w*2, y + (3 + self.choice) * h)
                self.text_player_prev = self.output_text('<', self.field_size[0] // 10 + w, y + (3 + self.choice) * h)
                self.text_player_next = self.output_text('>', self.text_player[0]+self.text_player[2]+8, y + (3 + self.choice) * h)

        elif self.choice == 1:  # режим
            text_mode = self.output_text(f'{self.mods[self.now_players]}', self.field_size[0] // 10 + w * 2, y + 4 * h)
            self.text_mode_prev = self.output_text('<', self.field_size[0] // 10 + w, y + 4 * h)
            self.text_mode_next = self.output_text('>', text_mode[0] + text_mode[2] + 8, y + (3 + self.choice) * h)

        else:
            win.blit(text, (self.field_size[0] // 10 + w, y + (3 + self.choice) * h))
        pygame.display.update()

    def draw_main_menu(self):
        def title_tetge(string, color, y):
            x = (self.field_size[0] - self.game_title.render(string, False, (0,0,0)).get_size()[0])//2 + 10
            for char in string:
                text = self.game_title.render(char, False, color[char])
                text_coor = text.get_rect(center=(x, y))
                win.blit(text, text_coor)
                x += text_coor[2] + 8

        # win.blit(self.background_black, (0, 0)) # полупрозрачный
        y = self.field_size[1] // 5

        s = 40
        w = 10

        # text = self.game_title.render('T', False, (80, 41, 255))
        # win.blit(text, (self.field_size[0] // 2 - 2 * s - w, y))
        # win.blit(text, (self.field_size[0] // 2 - w, y))
        # text = self.game_title.render('E', False, (255, 30, 0))
        # win.blit(text, (self.field_size[0] // 2 - s - w, y))
        # text = self.game_title.render('G', False, (59, 255, 0))
        # win.blit(text, (self.field_size[0] // 2 + s * 1 - w, y))
        # text = self.game_title.render('E', False, (196, 0, 255))
        # win.blit(text, (self.field_size[0] // 2 + s * 2 - w, y))

        title_tetge('TETGE', {'T':(80, 41, 255), 'E':(255, 30, 0), 'G':(59, 255, 0)}, y)
        w = 20
        h = 50
        y = self.field_size[1] // 2
        x = self.field_size[0] // 5

        self.text_start = self.output_text('Start', x + w, y)
        self.text_score = self.output_text('Scores', x + w, y + h)
        self.text_exit = self.output_text('Exit', x + w, y + h * 2)

        text = self.creators.render('© MurkyShadow, ToPzSpAy, dogganovich68', False, (255, 255, 255))
        win.blit(text, (x - 55, self.field_size[1] - 30))

        w -= 30
        text = self.menu_font.render('>', False, (255, 255, 255))
        win.blit(text, (x + w, y + h * self.choice))

        pygame.display.update()

    def rect_resize(self, rect):
        for i in range(4):
            rect[i] = int(multi*rect[i])
        return rect

    def main_menu(self):
        self.play = False
        self.scoreboard_open = False
        self.start_game_menu_open = False
        self.main_menu_open = True

        self.count = 0  # для двух падующих блоков в self.animation()
        self.max_block = 2  # 2 падующих блока
        self.block_drop_time = 0.07

        self.choice = 0
        try:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(self.android_path + "music/menu.mp3")
                pygame.mixer.music.play(-1)
                if not self.play_music:
                    pygame.mixer.music.pause()
        except Exception:
            print('наушники')
            self.play_music = False

        while self.main_menu_open:
            self.window_resize()
            if self.timer_animation.end() >= self.block_drop_time:
                self.animation()

            for event in pygame.event.get():  # пауза на C
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and (event.button == 1):  # нажата левая кнопка мыши
                    mouse = pygame.mouse.get_pos()
                    # print(self.text_start)
                    # print(self.rect_resize(self.text_start))
                    if self.rect_resize(self.text_start).collidepoint(mouse):  # cтарт
                        self.choice = 0
                        self.main_menu_open = False
                        self.start_game_menu_open = True
                        self.start_game_menu()
                    elif self.rect_resize(self.text_score).collidepoint(mouse):    # scoreboard
                        self.choice = 0
                        self.main_menu_open = False
                        self.scoreboard_open = True
                        self.start_scoreboard()
                    elif self.rect_resize(self.text_exit).collidepoint(mouse):  # exit
                        pygame.quit()
                        sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        self.play_stop_music()
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
                            self.main_menu_open = False
                            self.start_game_menu_open = True
                            self.start_game_menu()
                        elif self.choice == 1:  # scoreboard
                            self.main_menu_open = False
                            self.scoreboard_open = True
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
        while self.scoreboard_open:
            self.window_resize()
            if self.timer_animation.end() >= self.block_drop_time:
                self.animation()

            for event in pygame.event.get():  # пауза на C
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # нажата левая кнопка мыши
                    mouse = pygame.mouse.get_pos()
                    if self.rect_resize(self.text_back_score).collidepoint(mouse):    # назад в главное меню
                        self.scoreboard_open = False
                        self.main_menu_open = True

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        self.play_stop_music()
                    if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:  # back
                        self.scoreboard_open = False
                        self.main_menu_open = True

    def draw_scoreboard(self):
        # win.blit(self.background_black, (0, 0))
        w = 25
        h = 50
        y = self.field_size[1] // 7
        x = self.field_size[0] // 10
        text = self.gameover_title.render('SCOREBOARD', False, (255, 255, 255))
        win.blit(text, (x, y))
        win.blit(self.crown, (x, y))

        self.text_back_score = self.output_text('Back',  x+w, y + 8.5 * h)
        self.output_text('>', x, y + 8.5 * h)

        text = self.menu_font.render('Score', False, (255, 255, 255))
        win.blit(text, (x + w, y + 2 * h))

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

    def text_rect_left(self, text, x, y):   # координаты для левой верхней точки вывода текста
        return (x+text.get_rect()[2]//2, y+text.get_rect()[3]//2)

    def output_text(self, string, x, y):
        text = self.menu_font.render(string, False, (255, 255, 255))
        text_coord = text.get_rect(center = self.text_rect_left(text, x, y))
        win.blit(text, text_coord)
        return text_coord

    def score(self):
        text_surface = self.score_title.render('Score: ' + str(self.max_h), False, (242, 243, 244))
        win.blit(text_surface, (0, 0))

    def update_win(self, update=1):
        """при смене уровня карты, перерисовывает все окно"""
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
        for self.i, n_b in enumerate(self.falling_blocks, 0):
            if self.fall(n_b[0], n_b[1], n_b[2], n_b[3], n_b[4], n_b[5]):
                return
        if self.main_menu_open:
            self.draw_main_menu()
        elif self.start_game_menu_open:
            self.draw_start_game_menu()
        elif self.scoreboard_open:
            self.draw_scoreboard()
        else:
            pygame.display.update()


        # time.sleep(self.block_drop_time)
        self.timer_animation = Timer()
        # self.now_animation = False

    def place_fall(self, block):
        """выбираем место для падения блока"""
        min_height = min(self.height)
        min_now = randint(1, self.height.count(min_height))  # если минимальных чисел несколько, то среди них выбираем рандомно
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
                        (now_space == x_info[1] and stop_h == x_info[2] and randint(0, 1) and block != [[1, 1, 1, 1]]):  # палку ставим вплотную
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
        # print([now_block, x_info[2], x_info[0], len(self.field[0]) - 5, 0, color])
        self.falling_blocks.append([now_block, x_info[2], x_info[0], len(self.field[0]) - 5, 0, color])

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
            if self.house and int(self.timer_house.end()) >= self.time_house:
                self.play = False
                self.now_animation = True
                return True
            elif not self.house:
                self.house = True
                self.timer_house = Timer()
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
                            # win.blit(self.color_blocks[color - 1], ((place + x) * 24, (y_win - i) * 24))
                            # self.update_win(2)
                            pass
                        else:
                            for player in self.players[:self.now_players]:
                                try:
                                    if self.check_death(player, place, x, y, i):
                                        return True
                                except TypeError:
                                    print("ОШИБКА")
                                    print(self.field[player.coor_player[0] // 24][len(self.field[0]) - 5 + 1 - player.coor_player[1] // 24])
                                    print(self.field[player.coor_player[0] // 24 - 1][ len(self.field[0]) - 5 - player.coor_player[1] // 24])
            self.falling_blocks[self.i] = [block, stop_h, place, y, y_win, self.falling_blocks[self.i][5]]

        else:
            try:
                self.falling_blocks.remove([block, stop_h, place, y, y_win, self.falling_blocks[self.i][5]])
            except ValueError:
                pass
        if not self.play:
            self.background_black.set_alpha(115)  # полупрозрачный черный
            self.update_win(0)
            self.background_black.set_alpha(130)  # полупрозрачный черный
        row_pl = max([len(self.field[0]) - pl.coor_player[1]//24-5 for pl in self.players])  # Y персонажа
        self.max_h = max(self.max_h, row_pl)

        if row_pl - (len(self.field[0]) - 28) > 10:
            self.max_h += 1

        if self.max_h >= 12 and len(self.field[0]) - self.max_h <= 16:
            up = len(self.field[0]) - self.max_h - 15

            for k in range(up):
                for i in range(18):
                    self.field[i].append([0])
                for i in range(len(self.falling_blocks)):
                    self.falling_blocks[i][4] += 1
                for pl in self.players[:self.now_players]:
                    pl.coor_player[1] += 24

    def death_menu(self):
        self.open_death_menu = True
        self.insert_in_scoreboard()
        # print('вы проиграли!')
        self.score()
        # w, h = pygame.display.get_surface().get_size()
        w, h = self.field_size[0], self.field_size[1]
        pygame.draw.rect(win, (0, 0, 0), (0, 0, w, h+150))
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


        # text = self.menu_font.render('Retry', False, (255, 255, 255))
        # win.blit(text, (self.field_size[0] // 5 + w, y))
        rect_retry = self.output_text('Retry', self.field_size[0] // 5 + w, y)

        # text = self.menu_font.render('Menu', False, (255, 255, 255))
        # win.blit(text, (self.field_size[0] // 5 + w, y + h))
        rect_menu = self.output_text('Menu', self.field_size[0] // 5 + w, y + h)

        w -= 30
        text = self.menu_font.render('>', False, (255, 255, 255))
        win.blit(text, (self.field_size[0] // 5 + w, y))

        self.window_resize()
        pygame.display.update()

        choice = 0
        while 1:
            self.window_resize()
            events = list(pygame.event.get())
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # нажата левая кнопка мыши
                    mouse = pygame.mouse.get_pos()
                    if self.rect_resize(rect_retry).collidepoint(mouse):    # retry
                        self.reset()
                        self.open_death_menu = False
                        return True
                    if self.rect_resize(rect_menu).collidepoint(mouse):     # main menu
                        self.main_menu_open = True
                        self.open_death_menu = False
                        self.reset()
                        self.main_menu()
                        return True
                        # if (event.pos[0] >= self.field_size[0] // 5 + w and event.pos[1] >= self.field_size[1] // 2 and
                        #         event.pos[0] <= self.field_size[0] // 5 + w + 105 and event.pos[1] <= self.field_size[1] // 2 + 40):  # cтарт
                        #     self.reset()
                        #     return True
                        # elif (event.pos[0] >= self.field_size[0] // 5 + w and event.pos[1] >= self.field_size[
                        #     1] // 2 + 50 and event.pos[0] <= self.field_size[0] // 5 + w + 105 and event.pos[1] <=
                        #       self.field_size[1] // 2 + 40 + 50):  # cтарт
                        #     self.menu = True
                        #     self.reset()
                        #     self.main_menu()
                        #     return True

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        win.fill((0, 0, 0), (self.field_size[0] // 5 + w, y + h * choice, 16, 32))  # стираем
                        if choice == 1:
                            choice = 0
                        win.blit(text, (self.field_size[0] // 5 + w, y + h * choice))
                        self.window_resize()
                        pygame.display.update()
                    if event.key == pygame.K_DOWN:
                        win.fill((0, 0, 0), (self.field_size[0] // 5 + w, y + h * choice, 16, 32))  # стираем
                        if choice == 0:
                            choice = 1
                        win.blit(text, (self.field_size[0] // 5 + w, y + h * choice))
                        self.window_resize()
                        pygame.display.update()
                    if event.key == pygame.K_RETURN:
                        if choice == 0:  # cтарт
                            self.reset()
                        else:
                            self.main_menu_open = True
                            self.reset()
                            self.main_menu()
                        return True
                    elif event.key == pygame.K_ESCAPE:
                        self.main_menu_open = True
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

    def window_resize(self):
        # scaled_surface = pygame.transform.scale(win, (int(18 * 24 * multi), int((24 * 24+150) * multi)))
        # scaled_surface = pygame.transform.scale(win, (int(18 * 24 * multi), int((24 * 24) * multi)))
        # main_win.blit(scaled_surface, (0, 0))
        pygame.display.update()
        pass

class Builder():    # запускает приложение
    multi, win = 1,1
    def __init__(self):
        x = 100
        y = 45
        # os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x, y)
        pygame.init()
        win_size = [18 * 24, 24 * 24]

        pygame.display.set_caption('Tetge')
        # icon = pygame.image.load('/data/data/org.test.myapp/files/app/'+'img/icon.png')
        icon = pygame.image.load('img/icon.png')
        pygame.display.set_icon(icon)

        try:
            global multi
            global win
            multi = pygame.display.Info().current_h / (win_size[1] + 150)  # во сколько  раз растянуть экран
            multi = 1
            if multi * win_size[0] <= pygame.display.Info().current_w + 1:  # подгоняем экран для компа
                # main_win = pygame.display.set_mode((int(18 * 24 * multi), int((24 * 24+150) * multi)), RESIZABLE)
                # win = pygame.Surface((int(18 * 24), int(24 * 24+150)))
                self.win = pygame.display.set_mode((int(18 * 24 * multi), int((24 * 24) * multi)))
                # win = pygame.Surface((int(18 * 24), int(24 * 24)))
                self.path = ''

                multi, win = multi, self.win

                self.game = Tetge()
            else:  # экран для телефона
                multi = pygame.display.Info().current_w / win_size[0]
                main_win = pygame.display.set_mode((int(18 * 24 * multi), int((24 * 24 + 150) * multi)))
                self.win = pygame.Surface((int(18 * 24), int(24 * 24 + 150)))
                self.path = '/data/data/org.test.myapp/files/app/'
                multi, win = multi, self.win
                self.game = Tetge()

        except Exception as er:  # если ошибка, то выводим
            win_size = (pygame.display.Info().current_w, pygame.display.Info().current_h - 50)
            main_win = pygame.display.set_mode(win_size)
            font = pygame.font.SysFont("comicsansms", 55)
            words = str(er).split()
            before_line = ''
            line = 'ERROR'
            y = 10
            for word in words:
                before_line = line
                line += ' ' + word
                text = font.render(line, False, (255, 255, 255))
                # print(text.get_size()[0])
                # print(line)
                if text.get_size()[0] >= win_size[0]:
                    main_win.blit(font.render(before_line, False, (255, 255, 255)), (10, y))
                    y += 40
                    line = word
            main_win.blit(font.render(line, False, (255, 255, 255)), (10, y))

            # text = font.render('ERROR '+str(er), False, (255, 255, 255))
            pygame.display.update()
            while 1:
                pass

        #     game = tetge()
        # except Exception:
        #     font = pygame.font.SysFont("comicsansms", 24)
        #     text = font.render('ERROR', False, (255, 255, 255))
        #     win.blit(text, (10, 10))
        #     pygame.display.update()
        #     while 1:
        #         pass

if __name__ == "__main__":
    B = Builder()
    B.game.start_game(path='', test=True)
