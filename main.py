import pygame
import sys
import random
import pickle

# Global Constans

pygame.init()
screen_width = 1200
screen_height = 750
screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption("Dino Game")
pygame.display.set_icon(pygame.image.load("assets/images/dino_icon_game.png"))
clock = pygame.time.Clock()

game_font = pygame.font.Font('assets/PressStart2P-Regularr.ttf', 24)

# Sounds
jump_song = pygame.mixer.Sound("assets/audio/jumpp.mp3")
points_song = pygame.mixer.Sound("assets/audio/100points.mp3")
lose_song = pygame.mixer.Sound("assets/audio/lose.mp3")


# Classes


class Dino(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos):
        super(Dino, self).__init__()

        self.running_sprites = [pygame.transform.scale(
            pygame.image.load("assets/images/Dino1.png"), (80, 100)), pygame.transform.scale(
            pygame.image.load("assets/images/Dino2.png"), (80, 100))]

        self.ducking_sprites = [pygame.transform.scale(
            pygame.image.load("assets/images/DinoDucking1.png"), (100, 60)), pygame.transform.scale(
            pygame.image.load("assets/images/DinoDucking2.png"), (100, 60))]

        self.dino_stoping = [pygame.transform.scale(
            pygame.image.load("assets/images/Dino_stop.png"), (100, 100))]

        self.x = x_pos
        self.y = y_pos

        self.current_image = 0
        self.velocity = 60
        self.image = self.running_sprites[self.current_image]
        self.gravity = 4.5
        self.ducking = False
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self):
        global game_speed, timer
        self.animate()
        self.apply_gravity()

    def animate(self):
        global game_speed, timer
        self.current_image += 0.05
        if self.current_image >= 2:
            self.current_image = 0

        if game_speed == 0:
            self.image = self.dino_stoping[0]
        else:
            if self.ducking:
                self.image = self.ducking_sprites[int(self.current_image)]
            else:
                self.image = self.running_sprites[int(self.current_image)]

    def duck(self):
        if game_speed > 0:
            self.ducking = True
            self.rect.centery = 380

    def unduck(self):
        self.ducking = False
        self.rect.centery = 360

    def apply_gravity(self):
        if self.rect.centery <= 360:
            self.rect.centery += self.gravity

    def jump(self):
        jump_song.play()
        if self.rect.centery >= 360 and game_speed > 0:
            while self.rect.centery - self.velocity > 50:
                self.rect.centery -= 0.6


class Clouds:
    def __init__(self):
        self.x = screen_width + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = cloud
        self.width = self.image.get_width()

    def update(self):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = screen_width + random.randint(1000, 1300)
            self.y = random.randint(40, 100)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
        screen.blit(self.image, (self.x + 100, self.y + 50))


class Obstacle:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = screen_width

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacle.pop()
            del self

    def draw(self, screen):
        screen.blit(self.image[self.type], self.rect)


class Big_cactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 300


class Small_cactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 325


class Angry_dinos(Obstacle):
    def __init__(self, image):
        self.type = 0
        super(Angry_dinos, self).__init__(image, self.type)
        self.rect.y = random.randint(130, 260)
        self.index = 0

    def draw(self, screen):
        if self.index >= 9:
            self.index = 0
        screen.blit(self.image[self.index // 5], self.rect)
        self.index += 1


# Images

small_cactus = [pygame.transform.scale(
    pygame.image.load("assets/cacti_folder/cactus1.png"), (100, 100)),
    pygame.transform.scale(
        pygame.image.load("assets/cacti_folder/cactus2.png"), (100, 100)),
    pygame.transform.scale(
        pygame.image.load("assets/cacti_folder/cactus3.png"), (100, 100))]

big_cactus = [pygame.transform.scale(
    pygame.image.load("assets/cacti_folder/cactus4.png"), (100, 100)),
    pygame.transform.scale(
        pygame.image.load("assets/cacti_folder/cactus4.png"), (100, 100)),
    pygame.transform.scale(
        pygame.image.load("assets/cacti_folder/cactus5.png"), (100, 100))]

angry_dinos = [pygame.transform.scale(
    pygame.image.load("assets/images/Ptero1.png"), (84, 62)),
    pygame.transform.scale(
        pygame.image.load("assets/images/Ptero2.png"), (84, 62))]

restart_games = pygame.transform.scale(
    pygame.image.load("assets/images/restart_game.png"), (84, 62))

# Surfaces

points = 0
three_lives = 3
game_speed = 5
dino_group = pygame.sprite.GroupSingle()
dinosaur = Dino(50, 400)
dino_group.add(dinosaur)

cloud = pygame.image.load("assets/images/cloud.png")
cloud = pygame.transform.scale(cloud, (200, 80))

clouds = Clouds()

death_count = 0

ground = pygame.image.load("assets/images/ground.png")
ground = pygame.transform.scale(ground, (1200, 20))
ground_x = 0
ground_rect = ground.get_rect(center=(640, 400))

state = 'start'
timer = 60
dino_lose = False
record_points = 0
time = 0
timer_lives = 0
obstacle = []


# Functions

def menu():
    global points, state

    run = True
    while run:
        screen.fill("white")

        if death_count == 0:
            text = game_font.render("Press any Key to Start", True, "black")
        else:
            text = game_font.render("Press any Key to Start", True, "black")
            result_points = game_font.render("You points " + str(points), True, "black")
            result_points_rect = result_points.get_rect()
            result_points_rect.center = (screen_width // 2, screen_height + 60)
            screen.blit(result_points, result_points_rect)

        menu_picture = pygame.transform.scale(
            pygame.image.load("assets/images/menu_icon.png"), (430, 380))
        menu_picture_rect = menu_picture.get_rect()
        menu_picture_rect.center = (screen_width // 2, screen_height // 2 - 120)
        text_rect = text.get_rect()
        text_rect.center = (screen_width // 2, screen_height // 2 + 90)
        screen.blit(text, text_rect)
        screen.blit(menu_picture, menu_picture_rect)
        pygame.display.update()

        for event_ in pygame.event.get():
            if event_.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
            if event_.type == pygame.KEYDOWN:
                main()


def score():
    global points, game_speed
    if game_speed > 0:
        points += 1

    if points % 500 == 0:
        game_speed += 0.8
        points_song.play()
    text = game_font.render("Points: " + str(points), True, "#A69498")
    text_rect = text.get_rect()
    text_rect.center = (1000, 40)
    screen.blit(text, text_rect)

    record_text = game_font.render("Record: " + str(record_points), True, "#C8564F")
    record_rect = record_text.get_rect()
    record_rect.center = (150, 50)
    screen.blit(record_text, record_rect)


def end_game():
    global points, game_speed
    text_game_over = game_font.render("GAME OVER!", True, "black")
    game_over_rect = text_game_over.get_rect(center=(screen_height // 2 + 230, screen_height // 2 - 200))
    points_text = game_font.render("Points: " + str(points), True, "black")
    points_rect = points_text.get_rect(center=(screen_width // 2, screen_height // 2 - 150))
    screen.blit(text_game_over, game_over_rect)
    screen.blit(points_text, points_rect)

    restart_rect = restart_games.get_rect(center=(screen_width // 2, screen_height // 2 + 100))
    screen.blit(restart_games, restart_rect)
    pygame.display.update()

    run = True
    while run:
        for event_ in pygame.event.get():
            if event_.type == pygame.QUIT:
                run = False
            if event_.type == pygame.KEYDOWN:
                menu()


def lives():
    global three_lives
    text = game_font.render(f"Lives: {str(three_lives)}", True, "#A69498")
    text_rect = text.get_rect()
    text_rect.center = (980, 90)
    screen.blit(text, text_rect)


def points_save():
    global record_points
    if points > record_points:
        file = open("points.dat", "wb")
        pickle.dump(points, file)
        file.close()
        record_points = points


def points_load():
    global record_points
    try:
        file = open("points.dat", "wb")
        record_points - pickle.load(file)
        file.close()
    except:
        pass


def main():
    global state, three_lives, game_speed, ground_x, death_count, timer_lives, obstacle, points, time

    points_load()

    run = True
    while run:
        game_lost = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_DOWN]:
            dinosaur.duck()
        else:
            if dinosaur.ducking:
                dinosaur.unduck()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    dinosaur.jump()

        click = keys[0] or keys[pygame.K_SPACE]

        if click and game_speed == 0:
            points_save()

            state = "start"
            obstacle = []
            timer_lives = 3
            state = 'start'
            points = 0
            three_lives = 3
            ground_x = 0
            game_speed = 5

        if state == "start":

            if click and game_speed > 0:
                state = "play"
        elif state == "play":
            pass
        elif state == "collectivising":
            state = "start"
            three_lives -= 1
            if three_lives > 0:
                state = "start"
            else:
                state = "game_over"
        else:
            game_speed = 0
            death_count += 1
            end_game()

        time = (time + 0.05) % 512

        colors = abs(time - 256)
        screen.fill((colors, colors * 0.99, colors * 0.99))

        dino_group.update()
        dino_group.draw(screen)

        clouds.draw(screen)
        clouds.update()

        score()
        lives()

        game_speed -= 0.00025

        ground_x -= game_speed

        screen.blit(ground, (ground_x, 370))
        screen.blit(ground, (ground_x + 1200, 370))
        if ground_x <= -1300:
            ground_x = 0

        if game_lost:
            end_game()

        if len(obstacle) == 0 and game_speed > 0:
            if random.randint(0, 7) in [0, 4]:
                obstacle.append(Small_cactus(small_cactus))
            elif random.randint(0, 7) in [4, 6]:
                obstacle.append(Big_cactus(big_cactus))
            else:
                obstacle.append(Angry_dinos(angry_dinos))

        for i in obstacle:
            i.draw(screen)
            i.update()
            if dinosaur.rect.colliderect(i.rect) and game_speed > 0:
                pygame.draw.rect(screen, (255, 0, 0), dinosaur.rect, 2)
                lose_song.play()

                death_count += 1
                timer_lives += 1
                if timer_lives == 30:
                    state = "collectivising"
                    timer_lives = 0

        pygame.display.update()
        clock.tick(120)


points_save()
menu()
