
import random
import os.path
import pygame 
from pygame.locals import Rect, QUIT, KEYDOWN, K_RIGHT, K_LEFT, \
    K_SPACE, K_ESCAPE, FULLSCREEN
from Alien import Alien
from Bomb import Bomb
from Explosion import Explosion 
# from GameLevel import GameLevel
from Player import Player
from PlayerLives import PlayerLives
from Score import Score
from Shot import Shot
import Utility
from GameLevel import GameLevel
if not pygame.image.get_extended():



    raise SystemExit("Sorry, extended image module required")


MAX_SHOTS = 2
ALIEN_ODDS = 22
BOMB_ODDS =   60 
ALIEN_RELOAD = 12

SCREENRECT = Rect(0, 0, 1024, 768)


main_directory = os.path.split(os.path.abspath(__file__))[0]


def main(winstyle=0):
    if pygame.get_sdl_version()[0] == 2:
        pygame.mixer.pre_init(44100, 32, 2, 1024)

    pygame.init()

    # set the display mode
    # will go to full screen if uncommented
    winstyle = 0 # |FULLSCREEN

    # checks whether display mode is avaliable
    bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle,32)
    # This function will create a display Surface
    # Initialize a window or screenfor display
    screen = pygame.display.set_mode(SCREENRECT.size, winstyle,bestdepth)

    set_game_obj_images()

    pygame.mouse.set_visible(0)

    background_tile_image = Utility.load_image("background.gif")

    background = pygame.Surface(SCREENRECT.size)
    for x_position in range (0, SCREENRECT.width,
                            background_tile_image.get_width()):
        background.blit(background_tile_image, (x_position,0))
    
    screen.blit(background, (0,0))

    pygame.display.flip()

    set_game_sound()

    aliens = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    bombs = pygame.sprite.Group()

    all_game_rects = pygame.sprite.RenderUpdates()
    last_alien = pygame.sprite.GroupSingle()

    Player.containers = all_game_rects

    Alien.containers = aliens, all_game_rects, last_alien
    Shot.containers = shots, all_game_rects
    Bomb.containers = bombs, all_game_rects
    Explosion.containers = all_game_rects
    Score.containers = all_game_rects

    last_alien
    PlayerLives.containers = all_game_rects
    GameLevel.containers = all_game_rects
    PlayerLives.lives = 1000000

    GameLevel.level = 1

    Score.containers = all_game_rects
    Score.score_points = 0

    Alien(SCREENRECT)

    if (pygame.font is not None):
        all_game_rects.add(Score())
        all_game_rects.add(PlayerLives())
        all_game_rects.add(GameLevel())


    print("starting the game")

    game_loop(all_game_rects, screen, background, shots, last_alien, aliens, bombs, winstyle, bestdepth, FULLSCREEN)


    if (pygame.mixer is not None):

        pygame.mixer.music.fadeout(1000)

    pygame.time.wait(1000)

    pygame.quit()


def set_game_sound():

    if pygame.mixer and not pygame.mixer.get_init():
        pygame.mixer = None
    music = os.path.join(main_directory, "data", "house_lo.wav")

    pygame.mixer.music.load(music)

    pygame.mixer.music.set_volume(.2)


    pygame.mixer.music.play(-1)

def check_game_level(score):
    if(GameLevel.level == 1 and score > 9):
        GameLevel.level = 2
    elif(GameLevel.level == 2 and score > 19):
        GameLevel.level = 3
    elif(GameLevel.level == 3 and score > 29):
        GameLevel.level = 4
    elif(GameLevel.level == 4 and score > 39):
        GameLevel.level = 5
    elif(GameLevel.level == 5 and score >49):
        GameLevel.level = 6
    elif(GameLevel.level == 6 and score > 59):
        GameLevel.level = 7
    elif(GameLevel.level == 7 and score > 69):
        GameLevel.level = 8
    elif(GameLevel.level == 8 and score > 79):
        GameLevel.level = 9
    elif(GameLevel.level == 9 and score > 89):
        GameLevel.level = 10


def game_loop(all_game_rects, screen, background, shots, last_alien, aliens, bombs, winstyle, bestdepth, FULSCREEN): 
    clock = pygame.time.Clock()
    player = Player(SCREENRECT)


    alienreload = ALIEN_RELOAD

    boom_sound = Utility.load_sound("boom.wav")
    shoot_sound = Utility.load_sound("car_door.wav")


    while (player.alive() is True):

        for event in pygame.event.get():


            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                return
            elif event.type == KEYDOWN:
                if event.key == pygame.K_f:
                    if not FULLSCREEN:
                        print("Changing to FULLSCREEN")
                        screen_backup = screen.copy()
                        screen = pygame.display.set_mode(
                            SCREENRECT.size,
                            winstyle | FULLSCREEN, 
                            bestdepth 
                        )
                        screen.blit(screen_backup, (0, 0))
                    else:
                        print("Changing to windowed mode")
                        screen_backup = screen.copy()
                        screen = pygame.display.set_mode(
                            SCREENRECT.size,
                            winstyle,
                            bestdepth 
                        )
                        screen.blit(screen_backup, (0, 0))
                        pygame.display.flip()
                        FULSCREEN = not FULLSCREEN
        print("in the game loop")
        
        all_game_rects.clear(screen, background)

        all_game_rects.update()

        handle_player_imput(player, shots, shoot_sound)



        if alienreload:
            alienreload = alienreload - 1
        elif not int(random.random() * ALIEN_ODDS):
            alienreload = ALIEN_RELOAD

            # if(GameLevel.level == 3):
            Alien(SCREENRECT)

        if last_alien and not int(random.random() * BOMB_ODDS):
            Bomb(last_alien.sprite)

        detect_collisions(player, aliens, shots, bombs, boom_sound)


        is_dirty = all_game_rects.draw(screen)
        pygame.display.update(is_dirty)
        clock.tick(40)
   
    return clock
def detect_collisions(player, aliens, shots, bombs, boom_sound):
    
    """
    done: pass score to Score object
    """
    
    for alien in pygame.sprite.spritecollide(player, aliens, 1):
        boom_sound.play()
        Explosion(alien)
        Explosion(player)

        Score.score_points = Score.score_points + 1

        check_game_level(Score.score_points)

        PlayerLives.lives = PlayerLives.lives - 1

        check_player_life(player)

    for alien in pygame.sprite.groupcollide(shots, aliens, 1, 1).keys():
        boom_sound.play()
        Explosion(alien)

        Score.score_points = Score.score_points + 1

        check_game_level(Score.score_points)

    for bomb in pygame.sprite.spritecollide(player, bombs, 1):
        Explosion(player)
        boom_sound.play()

        Explosion(bomb)
        boom_sound.play()

        PlayerLives.lives = PlayerLives.lives - 1

        check_player_life(player)

    for bomb in pygame.sprite.groupcollide(shots, bombs, 1, 1).keys():
        boom_sound.play()
        bomb.kill()
        Explosion(bomb)
            
        
def check_player_life(player):
    if (PlayerLives.lives < 1):

        player.kill()
        

def handle_player_imput(player, shots, shoot_sound):  
    keystate = pygame.key.get_pressed()   

    direction = keystate[K_RIGHT] - keystate[K_LEFT]

    player.move(direction)

    firing = keystate[K_SPACE]

    if not player.reloading and firing and len(shots) < MAX_SHOTS:
        Shot(player.get_gun_position())
        shoot_sound.play()

    player.reloading = firing
                        
                        
    
def set_game_obj_images():
    # Load images, assign to sprite classes 
    # (do this before the classes are used, after screen setup)
    player_image = Utility.load_image("player1.gif")

    # 2 images: tank facing left, tank facing right
    Player.images = [player_image, pygame.transform.flip(player_image, 1, 0)]

    explosion_image = Utility.load_image("explosion1.gif")

    Explosion.images = [
        explosion_image,
        pygame.transform.flip(explosion_image, 1, 1)
    ]

    Alien.images = Utility.load_images(
        "alien1.gif",
        "alien2.gif",
        "alien3.gif"
    )

    bomb_image = Utility.load_image("bomb.gif")
    Bomb.images = [bomb_image]

    shot_image = Utility.load_image("shot.gif")
    Shot.images = [shot_image]


    icon = pygame.transform.scale(Alien.images[0], (32, 32))

    pygame.display.set_icon(icon)

    
    
    

if (__name__ == "__main__"):
    main()






