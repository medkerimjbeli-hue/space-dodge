import pygame
import sys
import random
import pickle
import webbrowser

pygame.init()
pygame.mixer.init()

WIDTH = 700
HEIGHT = 700
fullscreen = False
game_surface = pygame.Surface(
    (WIDTH, HEIGHT)
)

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT),
    pygame.RESIZABLE
)
pygame.display.set_caption("Space Dodge")

clock = pygame.time.Clock()


background = pygame.image.load(
    "assets/bg.jpg"
).convert()

background = pygame.transform.scale(
    background,
    (WIDTH, HEIGHT)
)

player = pygame.image.load(
    "assets/player.png"
).convert_alpha()

player = pygame.transform.scale(
    player,
    (60, 60)
)

pygame.display.set_icon(player)

player_rect = player.get_rect(
    center=(WIDTH // 2, HEIGHT // 2)
)

projectile = pygame.image.load(
    "assets/rock.webp"
).convert_alpha()

projectile = pygame.transform.scale(
    projectile,
    (40, 40)
)


title_font = pygame.font.Font(
    "assets/fonts/TitleFont.ttf",
    80
)

timer_font = pygame.font.Font(
    "assets/fonts/Thin.otf",
    40
)

hud_font = pygame.font.Font(
    "assets/fonts/Thin.otf",
    26
)

restart_font = pygame.font.Font(
    "assets/fonts/Thin_Italic.otf",
    32
)

menu_button_font = pygame.font.Font(
    "assets/fonts/Thin.otf",
    32
)

small_font = pygame.font.Font(
    "assets/fonts/Thin.otf",
    24
)


theme_song = pygame.mixer.Sound(
    "assets/Sounds/theme_song.mp3"
)

collision_sound = pygame.mixer.Sound(
    "assets/Sounds/collision.mp3"
)

game_over_sound = pygame.mixer.Sound(
    "assets/Sounds/game_over.mp3"
)

button_sound = pygame.mixer.Sound(
    "assets/Sounds/button_pressed.mp3"
)

theme_song.set_volume(0.35)
collision_sound.set_volume(0.7)
game_over_sound.set_volume(0.8)
button_sound.set_volume(0.6)

theme_song.play(loops=-1)


HUD_REFERENCE_WIDTH = 700

HUD_SLOTS = [
    {"key": "time", "cx": 87, "cy": 70},
    {"key": "rocks", "cx": 262, "cy": 70},
    {"key": "speed", "cx": 437, "cy": 70},
    {"key": "best", "cx": 612, "cy": 70},
]

hud_strip = pygame.image.load(
    "assets/HUD.png"
).convert_alpha()

_hud_scale = WIDTH / hud_strip.get_width()

hud_strip = pygame.transform.smoothscale(
    hud_strip,
    (
        WIDTH,
        int(hud_strip.get_height() * _hud_scale)
    )
)


def draw_hud(
    elapsed_time,
    best_time,
    projectile_speed,
    max_projectiles
):

    screen.blit(hud_strip, (0, 0))

    values = {
        "time": f"{elapsed_time:.2f}",
        "rocks": f"{max_projectiles}",
        "speed": f"{projectile_speed:.1f}",
        "best": f"{best_time:.2f}",
    }

    for slot in HUD_SLOTS:

        text_surface = hud_font.render(
            values[slot["key"]],
            True,
            (255, 255, 255)
        )

        center = (
            slot["cx"] * _hud_scale,
            slot["cy"] * _hud_scale
        )

        text_rect = text_surface.get_rect(
            center=center
        )

        screen.blit(
            text_surface,
            text_rect
        )



BASE_PROJECTILE_SPEED = 5
PROJECTILE_SPEED_INCREASE = 0.5

BASE_MAX_PROJECTILES = 3
MAX_PROJECTILES_LIMIT = 8


def create_projectile():

    side = random.choice([
        "top",
        "bottom",
        "left",
        "right"
    ])

    if side == "top":

        x = random.randint(20, WIDTH - 20)
        y = 20

    elif side == "bottom":

        x = random.randint(20, WIDTH - 20)
        y = HEIGHT - 20

    elif side == "left":

        x = 20
        y = random.randint(20, HEIGHT - 20)

    else:

        x = WIDTH - 20
        y = random.randint(20, HEIGHT - 20)

    position = pygame.Vector2(x, y)

    target = pygame.Vector2(
        player_rect.centerx,
        player_rect.centery
    )

    direction = target - position

    if direction.length() > 0:
        direction = direction.normalize()

    return {
        "position": position,
        "direction": direction
    }


def get_difficulty(elapsed_time):

    speed = BASE_PROJECTILE_SPEED + (
        int(elapsed_time // 10)
        * PROJECTILE_SPEED_INCREASE
    )

    max_projectiles = BASE_MAX_PROJECTILES + int(
        elapsed_time // 30
    )

    max_projectiles = min(
        max_projectiles,
        MAX_PROJECTILES_LIMIT
    )

    return speed, max_projectiles



projectiles = []

for _ in range(BASE_MAX_PROJECTILES):
    projectiles.append(
        create_projectile()
    )

running = True

game_over = False

start_time = pygame.time.get_ticks()

try:

    with open(
        "best_time.pkl",
        "rb"
    ) as file:

        best_time = pickle.load(file)

except (
    FileNotFoundError,
    EOFError,
    pickle.UnpicklingError
):

    best_time = 0


elapsed_time = 0
projectile_speed = BASE_PROJECTILE_SPEED
max_projectiles = BASE_MAX_PROJECTILES



MENU = "menu"
HOW_TO_PLAY = "how_to_play"
GAME = "game"
GAME_OVER = "game_over"

current_screen = MENU



def draw_button(
    text,
    rect,
    mouse_pos,
    font=menu_button_font
):

    hovered = rect.collidepoint(mouse_pos)

    if hovered:

        pygame.draw.rect(
            screen,
            (255, 255, 255),
            rect,
            border_radius=8
        )

        text_color = (0, 0, 0)

    else:

        pygame.draw.rect(
            screen,
            (0, 0, 0),
            rect,
            border_radius=8
        )

        pygame.draw.rect(
            screen,
            (255, 255, 255),
            rect,
            2,
            border_radius=8
        )

        text_color = (255, 255, 255)

    text_surface = font.render(
        text,
        True,
        text_color
    )

    text_rect = text_surface.get_rect(
        center=rect.center
    )

    screen.blit(
        text_surface,
        text_rect
    )

    return hovered



def create_blurred_background(surface):

    # Downscale heavily
    small_surface = pygame.transform.smoothscale(
        surface,
        (70, 70)
    )

    # Scale it back up
    blurred_surface = pygame.transform.smoothscale(
        small_surface,
        (WIDTH, HEIGHT)
    )

    # Darken it
    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 150)
    )

    blurred_surface.blit(
        overlay,
        (0, 0)
    )

    return blurred_surface



def start_game():

    global current_screen
    global game_over
    global start_time
    global elapsed_time
    global projectile_speed
    global max_projectiles

    player_rect.center = (
        WIDTH // 2,
        HEIGHT // 2
    )

    projectiles.clear()

    for _ in range(BASE_MAX_PROJECTILES):

        projectiles.append(
            create_projectile()
        )

    game_over = False

    start_time = pygame.time.get_ticks()

    elapsed_time = 0

    projectile_speed = BASE_PROJECTILE_SPEED

    max_projectiles = BASE_MAX_PROJECTILES

    current_screen = GAME


while running:

    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False


        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:


                if current_screen == MENU:

                    play_button = pygame.Rect(
                        200,
                        270,
                        300,
                        60
                    )

                    how_button = pygame.Rect(
                        200,
                        350,
                        300,
                        60
                    )

                    contact_button = pygame.Rect(
                        200,
                        430,
                        300,
                        60
                    )

                    quit_button = pygame.Rect(
                        200,
                        510,
                        300,
                        60
                    )

                    if play_button.collidepoint(mouse_pos):

                        button_sound.play()

                        start_game()

                    elif how_button.collidepoint(mouse_pos):

                        button_sound.play()

                        current_screen = HOW_TO_PLAY

                    elif contact_button.collidepoint(mouse_pos):

                        button_sound.play()


                        webbrowser.open(
                            "https://www.instagram.com/med_kerim_jbeli/"
                        )

                    elif quit_button.collidepoint(mouse_pos):

                        button_sound.play()

                        running = False


                elif current_screen == HOW_TO_PLAY:

                    back_button = pygame.Rect(
                        200,
                        570,
                        300,
                        60
                    )

                    if back_button.collidepoint(mouse_pos):

                        button_sound.play()

                        current_screen = MENU

            

                elif current_screen == GAME_OVER:

                    menu_button = pygame.Rect(
                        200,
                        500,
                        300,
                        60
                    )

                    if menu_button.collidepoint(mouse_pos):

                        button_sound.play()

                        current_screen = MENU


        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_F11:

                fullscreen = not fullscreen

                if fullscreen:
                    screen = pygame.display.set_mode(
                        (0, 0),
                        pygame.FULLSCREEN
                    )
                else:
                    screen = pygame.display.set_mode(
                        (WIDTH, HEIGHT),
                        pygame.RESIZABLE
                    )
            if (
                event.key == pygame.K_r
                and current_screen == GAME_OVER
            ):

                button_sound.play()

                start_game()

            # Main menu
            if (
                event.key == pygame.K_ESCAPE
                and current_screen in [
                    HOW_TO_PLAY,
                    GAME_OVER
                ]
            ):

                button_sound.play()

                current_screen = MENU

    if current_screen == GAME:

        elapsed_time = (
            pygame.time.get_ticks()
            - start_time
        ) / 1000

        projectile_speed, max_projectiles = get_difficulty(
            elapsed_time
        )

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w] or keys[pygame.K_UP]:

            player_rect.y -= 5

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:

            player_rect.y += 5

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:

            player_rect.x -= 5

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:

            player_rect.x += 5

        player_rect.clamp_ip(
            screen.get_rect()
        )

        for p in projectiles:

            p["position"] += (
                p["direction"]
                * projectile_speed
            )


        for p in projectiles[:]:

            x = p["position"].x
            y = p["position"].y

            if (
                x < -50
                or x > WIDTH + 50
                or y < -50
                or y > HEIGHT + 50
            ):

                projectiles.remove(p)


        while len(projectiles) < max_projectiles:

            projectiles.append(
                create_projectile()
            )


        for p in projectiles:

            projectile_rect = projectile.get_rect(
                center=(
                    int(p["position"].x),
                    int(p["position"].y)
                )
            )

            if player_rect.colliderect(
                projectile_rect
            ):

                collision_sound.play()
                game_over_sound.play()

                game_over = True

                if elapsed_time > best_time:

                    best_time = elapsed_time

                    with open(
                        "best_time.pkl",
                        "wb"
                    ) as file:

                        pickle.dump(
                            best_time,
                            file
                        )

                current_screen = GAME_OVER

                break

    if current_screen == GAME:

        screen.blit(
            background,
            (0, 0)
        )

        screen.blit(
            player,
            player_rect
        )

        for p in projectiles:

            projectile_rect = projectile.get_rect(
                center=(
                    int(p["position"].x),
                    int(p["position"].y)
                )
            )

            screen.blit(
                projectile,
                projectile_rect
            )

        draw_hud(
            elapsed_time,
            best_time,
            projectile_speed,
            max_projectiles
        )


    elif current_screen == MENU:

        screen.blit(
            background,
            (0, 0)
        )

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 100)
        )

        screen.blit(
            overlay,
            (0, 0)
        )

        title = title_font.render(
            "SPACE DODGE",
            True,
            (255, 255, 255)
        )

        title_rect = title.get_rect(
            center=(WIDTH // 2, 150)
        )

        screen.blit(
            title,
            title_rect
        )

        play_button = pygame.Rect(
            200,
            270,
            300,
            60
        )

        how_button = pygame.Rect(
            200,
            350,
            300,
            60
        )

        contact_button = pygame.Rect(
            200,
            430,
            300,
            60
        )

        quit_button = pygame.Rect(
            200,
            510,
            300,
            60
        )

        draw_button(
            "PLAY",
            play_button,
            mouse_pos
        )

        draw_button(
            "HOW TO PLAY",
            how_button,
            mouse_pos
        )

        draw_button(
            "CONTACT DEV",
            contact_button,
            mouse_pos
        )

        draw_button(
            "QUIT GAME",
            quit_button,
            mouse_pos
        )

    elif current_screen == HOW_TO_PLAY:

        screen.blit(
            background,
            (0, 0)
        )

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 150)
        )

        screen.blit(
            overlay,
            (0, 0)
        )

        title = title_font.render(
            "HOW TO PLAY",
            True,
            (255, 255, 255)
        )

        title_rect = title.get_rect(
            center=(WIDTH // 2, 120)
        )

        screen.blit(
            title,
            title_rect
        )

        instructions = [
            "SURVIVE AS LONG AS YOU CAN.",
            "",
            "W / A / S / D",
            "OR ARROW KEYS",
            "",
            "DODGE THE ROCKS.",
            "",
            "THE LONGER YOU SURVIVE,",
            "THE FASTER THEY BECOME.",
            "",
            "GOOD LUCK."
        ]

        y = 210

        for line in instructions:

            text = small_font.render(
                line,
                True,
                (255, 255, 255)
            )

            text_rect = text.get_rect(
                center=(WIDTH // 2, y)
            )

            screen.blit(
                text,
                text_rect
            )

            y += 35

        back_button = pygame.Rect(
            200,
            570,
            300,
            60
        )

        draw_button(
            "BACK TO MENU",
            back_button,
            mouse_pos
        )


    elif current_screen == GAME_OVER:


        screen.blit(
            background,
            (0, 0)
        )

        screen.blit(
            player,
            player_rect
        )

        for p in projectiles:

            projectile_rect = projectile.get_rect(
                center=(
                    int(p["position"].x),
                    int(p["position"].y)
                )
            )

            screen.blit(
                projectile,
                projectile_rect
            )

        draw_hud(
            elapsed_time,
            best_time,
            projectile_speed,
            max_projectiles
        )


        blurred_background = create_blurred_background(
            screen.copy()
        )

        screen.blit(
            blurred_background,
            (0, 0)
        )


        game_over_text = title_font.render(
            "GAME OVER",
            True,
            (255, 255, 255)
        )

        game_over_rect = game_over_text.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2 - 130
            )
        )

        screen.blit(
            game_over_text,
            game_over_rect
        )

        run_text = timer_font.render(
            f"RUN TIME: {elapsed_time:.2f}s",
            True,
            (255, 255, 255)
        )

        run_rect = run_text.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2 - 40
            )
        )

        screen.blit(
            run_text,
            run_rect
        )

        best_text = timer_font.render(
            f"TIME TO BEAT: {best_time:.2f}s",
            True,
            (255, 255, 255)
        )

        best_rect = best_text.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2 + 10
            )
        )

        screen.blit(
            best_text,
            best_rect
        )

        restart_text = restart_font.render(
            "PRESS R TO RESTART",
            True,
            (255, 255, 255)
        )

        restart_rect = restart_text.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2 + 70
            )
        )

        screen.blit(
            restart_text,
            restart_rect
        )

        menu_button = pygame.Rect(
            200,
            500,
            300,
            60
        )

        draw_button(
            "MAIN MENU",
            menu_button,
            mouse_pos
        )


    pygame.display.flip()

    clock.tick(30)


pygame.quit()
sys.exit()