import pygame
from math import ceil
import sounddevice as sd
import numpy as np
import sys
import random

# Переменные для установки ширины и высоты окна
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 600
FPS = 30

# Подключение фото для заднего фона
# Здесь лишь создание переменной, вывод заднего фона ниже в коде
bg = pygame.image.load('data/bg.jpg')


def terminate():
    pygame.quit()
    sys.exit()


def end_sound():
    jump.stop()
    go.stop()


def end_screen(text, size_f):
    intro_text = text
    global event

    fon = pygame.transform.scale(pygame.image.load('data/bg.jpg'), (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, size_f)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


# Класс, описывающий поведение главного игрока
class Player(pygame.sprite.Sprite):
    # Изначально игрок смотрит вправо, поэтому эта переменная True
    right = True

    # Методы
    def __init__(self):
        # Стандартный конструктор класса
        # Нужно ещё вызывать конструктор родительского класса
        super().__init__()

        # Создаем изображение для игрока
        # Изображение находится в этой же папке проекта
        self.image = pygame.image.load('data/idle.png')

        # Установите ссылку на изображение прямоугольника
        self.rect = self.image.get_rect()
        self.rect.x = 700
        self.rect.y = 500

        # Задаем вектор скорости игрока
        self.change_x = 0
        self.change_y = 0

    def update(self):
        # В этой функции мы передвигаем игрока
        # Сперва устанавливаем для него гравитацию
        self.calc_grav()

        # Передвигаем его на право/лево
        # change_x будет меняться позже при нажатии на стрелочки клавиатуры
        self.rect.x += self.change_x

        # Следим ударяем ли мы какой-то другой объект, платформы, например
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        if not block_hit_list:
            block_hit_list = pygame.sprite.spritecollide(self, self.level.flag, False)
            if block_hit_list:
                pygame.mixer.music.stop()
                end_sound()
                win.play()
                end_screen(['', '', '', "                                    ПОБЕДА",
                            '                         Вы прекрасно орёте.'], 60)
                terminate()
        if not block_hit_list:
            block_hit_list = pygame.sprite.spritecollide(self, self.level.mplatform_list, False)
        if not block_hit_list:
            block_hit_list = pygame.sprite.spritecollide(self, self.level.ship_list, False)
            if block_hit_list:
                pygame.mixer.music.stop()
                end_sound()
                end.play()
                end_screen(['', '', '', "                                    КОНЕЦ ИГРЫ",
                            '            Для закрытия нажмите любую кнопку.'], 60)
                terminate()
        # Перебираем все возможные объекты, с которыми могли бы столкнуться
        for block in block_hit_list:
            # Если мы идем направо,
            # устанавливает нашу правую сторону на левой стороне предмета, которого мы ударили
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                # В противном случае, если мы движемся влево, то делаем наоборот
                self.rect.left = block.rect.right

        # Передвигаемся вверх/вниз
        self.rect.y += self.change_y

        # То же самое, вот только уже для вверх/вниз
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        if not block_hit_list:
            block_hit_list = pygame.sprite.spritecollide(self, self.level.flag, False)
            if block_hit_list:
                pygame.mixer.music.stop()
                end_sound()
                win.play()
                end_screen(['', '', '', "                                    ПОБЕДА",
                            '                         Вы прекрасно орёте.'], 60)
                terminate()
        if not block_hit_list:
            block_hit_list = pygame.sprite.spritecollide(self, self.level.mplatform_list, False)
        if not block_hit_list:
            block_hit_list = pygame.sprite.spritecollide(self, self.level.ship_list, False)
            if block_hit_list:
                pygame.mixer.music.stop()
                end_sound()
                end.play()
                end_screen(['', '', '', "                                    КОНЕЦ ИГРЫ",
                            '            Для закрытия нажмите любую кнопку.'], 60)
                terminate()
        for block in block_hit_list:
            # Устанавливаем нашу позицию на основе верхней / нижней части объекта, на который мы попали
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom

            # Останавливаем вертикальное движение
            self.change_y = 0

    def calc_grav(self):
        # Здесь мы вычисляем как быстро объект будет
        # падать на землю под действием гравитации
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += .95

        # Если уже на земле, то ставим позицию Y как 0
        if self.rect.y >= SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height

    def jump(self):
        # Обработка прыжка
        # Нам нужно проверять здесь, контактируем ли мы с чем-либо
        # или другими словами, не находимся ли мы в полете.
        # Для этого опускаемся на 10 единиц, проверем соприкосновение и далее поднимаемся обратно
        self.rect.y += 10
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        print(platform_hit_list)
        self.rect.y -= 10
        if not platform_hit_list:
            self.rect.y += 10
            platform_hit_list = pygame.sprite.spritecollide(self, self.level.mplatform_list, False)
            self.rect.y -= 10

        # Если все в порядке, прыгаем вверх
        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            x, y = self.rect.x, self.rect.y
            jump.play()
            create_particles((x + 16, y + 60), 'jump', 10)
            self.change_y = -16

    # Передвижение игрока
    def go_left(self):
        # Сами функции будут вызваны позже из основного цикла
        self.change_x = -9  # Двигаем игрока по Х
        if self.right:  # Проверяем куда он смотрит и если что, то переворачиваем его
            self.flip()
            self.right = False

    def go_right(self):
        # то же самое, но вправо
        self.change_x = 9
        if not self.right:
            self.flip()
            self.right = True

    def stop(self):
        # вызываем этот метод, когда не нажимаем на клавиши
        self.change_x = 0

    def flip(self):
        # переворот игрока (зеркальное отражение)
        self.image = pygame.transform.flip(self.image, True, False)

    def set_coord(self):
        return self.rect.x, self.rect.y


# Класс для описания платформы
class Platform(pygame.sprite.Sprite):
    def __init__(self, width, height, data):
        # Конструктор платформ
        super().__init__()
        # Также указываем фото платформы
        self.image = pygame.image.load(data)

        # Установите ссылку на изображение прямоугольника
        self.rect = self.image.get_rect()


class Ship(pygame.sprite.Sprite):
    def __init__(self, width, height, data):
        super().__init__()
        self.image = pygame.image.load(data)
        self.rect = self.image.get_rect()


class Flag(pygame.sprite.Sprite):
    def __init__(self, width, height, data):
        super().__init__()
        self.image = pygame.image.load(data)
        self.rect = self.image.get_rect()


class M_Platform(pygame.sprite.Sprite):
    # Изначально игрок смотрит вправо, поэтому эта переменная True
    right = True

    # Методы
    def __init__(self, width, height):
        # Стандартный конструктор класса
        # Нужно ещё вызывать конструктор родительского класса
        super().__init__()

        # Создаем изображение для игрока
        # Изображение находится в этой же папке проекта
        self.image = pygame.image.load('data/M_p.png')

        # Установите ссылку на изображение прямоугольника
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 0, 400

        # Задаем вектор скорости игрока
        self.change_x = 0
        self.change_y = 0

    def update(self):
        # В этой функции мы передвигаем платформу
        self.rect.y += self.change_y
        self.rect.x += self.change_x

    def go_left(self):
        # Сами функции будут вызваны позже из основного цикла
        self.change_x = -3  # Двигаем платформу по Х

    def go_right(self):
        # то же самое, но вправо
        self.change_x = 3

    def stop(self):
        # вызываем этот метод, когда не нажимаем на клавиши
        self.change_x = 0

    def up(self, numb):
        self.rect.y = 600 - numb


# Класс для расстановки платформ на сцене
class Level(object):
    def __init__(self, player):
        # Создаем группу спрайтов (поместим платформы различные сюда)
        self.platform_list = pygame.sprite.Group()
        self.mplatform_list = pygame.sprite.Group()
        self.ship_list = pygame.sprite.Group()
        self.flag = pygame.sprite.Group()
        # Ссылка на основного игрока
        self.player = player

    # Чтобы все рисовалось, то нужно обновлять экран
    # При вызове этого метода обновление будет происходить
    def update(self):
        self.flag.update()
        self.platform_list.update()
        self.mplatform_list.update()
        self.ship_list.update()

    # Метод для рисования объектов на сцене
    def draw(self, screen):
        # Рисуем задний фон
        screen.blit(bg, (0, 0))

        # Рисуем все платформы из группы спрайтов
        self.flag.draw(screen)
        self.ship_list.draw(screen)
        self.platform_list.draw(screen)
        self.mplatform_list.draw(screen)


# Класс, что описывает где будут находится все платформы
# на определенном уровне игры
class Level_01(Level):
    def __init__(self, player):
        # Вызываем родительский конструктор
        Level.__init__(self, player)

        # Массив с данными про платформы. Данные в таком формате:
        # ширина, высота, x и y позиция
        level = [(32, 190, 110, 400, 'ws'),
                 (32, 190, 100, 370, 'u'),
                 (32, 190, 270, 370, 'u'),
                 (32, 190, 440, 370, 'u'),
                 (32, 190, 600, 370, 'u'),
                 (190, 32, 100, 180),
                 (32, 60, 600, 400, 's'),
                 (32, 190, -10, 580, 'u'),
                 (32, 190, 180, 580, 'u'),
                 (32, 190, 370, 580, 'u'),
                 (32, 190, 560, 580, 'u'),
                 (32, 190, 750, 580, 'u'),
                 (32, 190, 940, 580, 'u'),
                 (32, 190, 1130, 580, 'u'),
                 (32, 190, 510, 400, 'ws'),
                 (30, 30, 1000, 70, 'f'),
                 (32, 190, 100, 130),
                 (32, 190, 760, 370, 'u'),
                 (190, 32, 935, 180, 'p'),
                 (190, 32, 935, 120, 'p'),
                 (32, 190, 935, 120, 'u'),
                 (32, 190, 100, 133, 'u'),
                 (32, 190, 200, 133, 'u'),
                 (190, 32, 540, -20, 'p'),
                 (32, 60, 900, 550, 'us'),
                 (32, 60, 390, 540, 'us'),
                 (32, 60, 420, 540, 'us'),
                 (32, 60, 360, 540, 'us'),
                 (190, 32, 540, 50, 'p'),
                 (190, 32, 200, 230, 'u'),
                 (190, 32, 350, 230, 'u'),
                 (190, 32, 680, 180, 'p'),
                 (190, 32, 680, 80, 'p'),
                 (190, 32, 800, -20)
                 ]

        # Перебираем массив и добавляем каждую платформу в группу спрайтов - platform_list
        for platform in level:
            if platform[-1] == 'u':
                block = Platform(platform[0], platform[1], 'data/platform.png')
                block.rect.x = platform[2]
                block.rect.y = platform[3]
                block.player = self.player
                self.platform_list.add(block)
            elif platform[-1] == 's':
                block = Ship(platform[0], platform[1], 'data/unship.png')
                block.rect.x = platform[2]
                block.rect.y = platform[3]
                block.player = self.player
                self.ship_list.add(block)
            elif platform[-1] == 'ws':
                block = Ship(platform[0], platform[1], 'data/walls.png')
                block.rect.x = platform[2]
                block.rect.y = platform[3]
                block.player = self.player
                self.ship_list.add(block)
            elif platform[-1] == 'f':
                block = Flag(platform[0], platform[1], 'data/флаг.png')
                block.rect.x = platform[2]
                block.rect.y = platform[3]
                block.player = self.player
                self.flag.add(block)
            elif platform[-1] == 'us':
                block = Ship(platform[0], platform[1], 'data/ship.png')
                block.rect.x = platform[2]
                block.rect.y = platform[3]
                block.player = self.player
                self.ship_list.add(block)
            else:
                if len(platform) == 5:
                    block = Platform(platform[0], platform[1], 'data/pvplat.png')
                else:
                    block = Platform(platform[0], platform[1], 'data/vplat.png')
                block.rect.x = platform[2]
                block.rect.y = platform[3]
                block.player = self.player
                self.platform_list.add(block)

    def ad(self, platform):
        block = platform
        block.player = self.player
        self.mplatform_list.add(block)

    # Основная функция прогарммы


size = [SCREEN_WIDTH, SCREEN_HEIGHT]
screen = pygame.display.set_mode(size)

# Название игры
pygame.display.set_caption("Платформер")
pygame.init()
all_sprites = pygame.sprite.Group()

# для отслеживания улетевших частиц
# удобно использовать пересечение прямоугольников
screen_rect = (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
gravity = 0.25
clock = pygame.time.Clock()

end_screen(['', '', '',
            '', '', '', 'Правила просты - нужно просто дойти до красного',
            ' флага.', 'После нажатия кнопки мыши (мой совет) просто поорите несколько секунд!',
            'ОООЧЕНЬ ГРОМКО)'], 40)

duration = 5
listen = []
b = 0


def play(indata, outdata, frames, time, status):
    v = ceil(np.linalg.norm(indata) * 10) + 200
    if 120 < v < 570:
        listen.append(v)


with sd.Stream(callback=play):
    sd.sleep(duration * 1000)
listen.append(150)
print(listen)
flisten = []
for i in range(len(listen) - 1):
    b += 1
    cv = listen[b]
    flisten.append(listen[i])
    if listen[i] < cv:
        for j in range(abs(cv - listen[i]) // 5):
            listen[i] += 5
            flisten.append(listen[i])
    else:
        for j in range(abs(listen[i] - cv) // 5):
            listen[i] -= 5
            flisten.append(listen[i])

cv = flisten[-1]
if flisten[0] > flisten[-1]:
    for i in range(abs(flisten[0] - flisten[-1]) // 5):
        cv += 5
        flisten.append(cv)
else:
    for i in range(abs(flisten[0] - flisten[-1]) // 5):
        cv -= 5
        flisten.append(cv)
pygame.init()
all_sprites = pygame.sprite.Group()

# для отслеживания улетевших частиц
# удобно использовать пересечение прямоугольников
screen_rect = (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
gravity = 0.25


class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    fire = [pygame.image.load("data/земля.png")]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        # у каждой частицы своя скорость - это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos

        # гравитация будет одинаковой
        self.gravity = gravity

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect(screen_rect):
            self.kill()


def create_particles(position, fort, count):
    # количество создаваемых частиц
    particle_count = count
    # возможные скорости
    if fort == 'run':
        numbers = range(1, 6)
    else:
        numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


# Создаем игрока
player = Player()
platform = M_Platform(60, 32)

# Создаем все уровни
level_list = []
level_list.append(Level_01(player))
level_list[0].ad(platform)

# Устанавливаем текущий уровень
current_level_no = 0
current_level = level_list[current_level_no]

active_sprite_list = pygame.sprite.Group()
plat = pygame.sprite.Group()
player.level = current_level

player.rect.x = 1000
player.rect.y = 500
active_sprite_list.add(player)
plat.add(platform)

# Цикл будет до тех пор, пока пользователь не нажмет кнопку закрытия
done = False

# Основной цикл программы
# Отслеживание действий
paused = False
pygame.mixer.music.load('data/fonm.mp3')
pygame.mixer.music.play(loops=-1)
go = pygame.mixer.Sound('data/Run.mp3')
jump = pygame.mixer.Sound('data/jump.mp3')
end = pygame.mixer.Sound('data/end.mp3')
win = pygame.mixer.Sound('data/win.mp3')
while not done:
    for i in flisten:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Если закрыл программу, то останавливаем цикл
                terminate()
            # Если нажали на стрелки клавиатуры, то двигаем объект
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.go_left()
                    go.play()
                if event.key == pygame.K_RIGHT:
                    player.go_right()
                    go.play()
                if event.key == pygame.K_UP:
                    player.jump()
                if event.key == pygame.K_a:
                    platform.go_left()
                if event.key == pygame.K_d:
                    platform.go_right()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.change_x < 0:
                    player.stop()
                    go.stop()
                if event.key == pygame.K_RIGHT and player.change_x > 0:
                    player.stop()
                    go.stop()
                if event.key == pygame.K_a and platform.change_x < 0:
                    platform.stop()
                if event.key == pygame.K_d and platform.change_x > 0:
                    platform.stop()
        platform.up(i)

        # Обновляем игрока
        active_sprite_list.update()
        plat.update()
        all_sprites.update()

        # Обновляем объекты на сцене
        current_level.update()
        platform.update()

        # Если игрок приблизится к правой стороне, то дальше его не двигаем
        if player.rect.right > SCREEN_WIDTH:
            player.rect.right = SCREEN_WIDTH

        # Если игрок приблизится к левой стороне, то дальше его не двигаем
        if player.rect.left < 0:
            player.rect.left = 0
        # То же самое, но для M_Platform
        if platform.rect.right > SCREEN_WIDTH:
            platform.rect.right = SCREEN_WIDTH

        if platform.rect.left < 0:
            platform.rect.left = 0
        # Рисуем объекты на окне
        current_level.draw(screen)
        active_sprite_list.draw(screen)
        plat.draw(screen)
        all_sprites.draw(screen)

        # Устанавливаем количество фреймов
        clock.tick(30)

        # Обновляем экран после рисования объектов
        pygame.display.flip()
