import pygame as pg
from random import random, randint, choice


# здесь определяются константы, классы и функции
def draw_grid():    # функция для рисования сетки
    size, x_len, y_len = CELL_SIZE, X_LEN, Y_LEN
    height, width = HEIGHT, WIDTH
    color = GRAY
    for i in range(0, x_len, 16):
        pg.draw.line(disp, color,
                     [i * size, 0],
                     [i * size, height], 1)

    for i in range(0, y_len, 16):
        pg.draw.line(disp, color,
                     [0, i * size],
                     [width, i * size], 1)


def draw_food():    # функция для рисования еды
    gen = FIELD
    size = CELL_SIZE
    food_color = FOOD_COLOR
    for y in range(Y_LEN):
        for x in range(X_LEN):
            if gen[y][x]:
                pg.draw.rect(disp, food_color, (x * size, y * size, size, size))


def create_field():
    x_len, y_len, chance = X_LEN, Y_LEN, FOOD_CHANCE
    return [[1 if random() < chance else 0 for _ in range(x_len)] for _ in range(y_len)]


def create_ants():  # функция для создания муравьев
    neeed = ENERGY_NEED
    ants = []
    while len(ants) != ANTS_AMOUNT:
        x = randint(0, X_LEN-1)
        y = randint(0, Y_LEN-1)
        if FIELD[y][x] != 2:
            ants.append(Ant(x=x, y=y, e=neeed))
            FIELD[y][x] = 2
    return ants


class Ant:
    def __init__(self, x, y, e):
        self.x = x
        self.y = y
        self.e = e

    def move(self, gen):    # функция для движения муравья
        FIELD[self.y][self.x] = 0   # старая позиция на поле свободна
        size = CELL_SIZE
        pg.draw.rect(disp, ENV_COLOR, (self.x * size, self.y * size, size, size))

        if self.e <= 0:     # если нет энергии
            ANTS.remove(self)   # удаление муравья
            return

        move_x, move_y = choice([   # случайный выбор направления
            (1, 0),
            (0, 1),
            (-1, 0),
            (0, -1),
        ])

        x_len = X_LEN - 1
        y_len = Y_LEN - 1

        if move_x:
            self.e -= 1         # чтобы вечно не жили
            self.x += move_x
            if self.x > x_len:  # чтобы не выходил за границу
                self.x = x_len
            elif self.x < 0:    # чтобы не выходил за границу
                self.x = 0
            elif gen[self.y][self.x] == 2:  # чтобы не сталкивался с другими муравьями
                self.x -= move_x
            elif gen[self.y][self.x] == 1:  # чтобы кушал
                self.e += FOOD_EFFICIENCY
        else:
            self.e -= 1         # чтобы вечно не жили
            self.y += move_y
            if self.y > y_len:  # чтобы не выходил за границу
                self.y = y_len
            elif self.y < 0:    # чтобы не выходил за границу
                self.y = 0
            elif gen[self.y][self.x] == 2:  # чтобы не сталкивался с другими муравьями
                self.y -= move_y
            elif gen[self.y][self.x] == 1:  # чтобы кушал
                self.e += FOOD_EFFICIENCY

        FIELD[self.y][self.x] = 2   # новая позиция на поле занята
        # print(FIELD)

        e_need = ENERGY_NEED
        # создание нового муравья
        if self.e > e_need and not x_len < self.x - move_x < 0 and not y_len < self.y - move_y < 0:
            self.e -= e_need
            ANTS.append(Ant(x=self.x, y=self.y, e=e_need))
            FIELD[self.y][self.x] = 2

    def draw(self):     # функция для отрисовки муравья
        current_state_color = ANT_COLOR
        if self.e <= 0:
            current_state_color = ENV_COLOR
        pg.draw.rect(
            disp,
            current_state_color,
            (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        )


# палитра: https://coolors.co/palette/d9ed92-b5e48c-99d98c-76c893-52b69a-34a0a4-168aad-1a759f-1e6091-184e77
GRAY = (200, 200, 200)
GREEN = (41, 191, 18)
LIGHT_GREEN = (171, 255, 79)
BLUE = (8, 189, 189)
RED = (242, 27, 63)
ORANGE = (255, 153, 20)

ENV_COLOR = LIGHT_GREEN
FOOD_COLOR = GREEN
ANT_COLOR = RED


# здесь происходит инициация, создание объектов
pg.init()
pg.event.set_allowed([pg.QUIT])
FPS = 10

CELL_SIZE = 2
ANTS_AMOUNT = 4

ENERGY_NEED = 8
FOOD_EFFICIENCY = 16
FOOD_CHANCE = 0.5

WIDTH, HEIGHT = 1280, 720
X_LEN = WIDTH // CELL_SIZE
Y_LEN = HEIGHT // CELL_SIZE

disp = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()


FIELD = create_field()  # создание поля с клетками


ANTS = create_ants()    # создание муравьев


# отрисовка
disp.fill(ENV_COLOR)
# draw_grid()

draw_food()

for ant in ANTS:
    ant.draw()

pg.display.update()


RUN = True
while RUN:
    pg.display.set_caption(f'{round(clock.get_fps())}')

    # цикл обработки событий
    for event in pg.event.get():
        if event.type == pg.QUIT:
            RUN = False

    # изменение объектов
    # draw_grid()

    for ant in ANTS:
        ant.move(FIELD)
        ant.draw()

    clock.tick(FPS)
    pg.display.update()
