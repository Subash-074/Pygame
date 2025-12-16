
import pygame
import sys

# ---------------------------
# Screen Settings
# ---------------------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GROUND_HEIGHT = 40

# ---------------------------
# Character Base Class
# ---------------------------
class Character:
    def __init__(self, x, y, width, height, hp=100, speed=5, strength=10):
        self.rect = pygame.Rect(x, y, width, height)
        self.max_hp = hp
        self.hp = hp
        self.speed = speed
        self.strength = strength

        # Jumping / gravity
        self.is_jumping = False
        self.vertical_speed = 0
        self.GRAVITY = 1
        self.JUMP_STRENGTH = 15
        self.ground_y = SCREEN_HEIGHT - GROUND_HEIGHT - height
        self.rect.y = self.ground_y

    # Movement
    def move(self, dx):
        """Only horizontal movement."""
        self.rect.x += dx
        if self.rect.right < 0:
            self.rect.x = SCREEN_WIDTH
        elif self.rect.left > SCREEN_WIDTH:
            self.rect.x = -self.rect.width

    # Damge / Hp 
    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

    def is_alive(self):
        return self.hp > 0

    def apply_gravity(self):
        if self.is_jumping or self.rect.y < self.ground_y:
            self.vertical_speed += self.GRAVITY

        self.rect.y += self.vertical_speed

        # Landing check
        if self.rect.y >= self.ground_y:
            self.rect.y = self.ground_y
            self.is_jumping = False
            self.vertical_speed = 0

    def update(self):
        """Update character each frame."""
        self.apply_gravity()

    def draw(self, screen, color=None):
        screen.blit(self.image, (self.rect.x, self.rect.y))

    #knockback
    def apply_knockback(self, direction, amount=20):
        """Push character left or right."""
        self.rect.x += direction * amount
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - self.rect.width))


# ---------------------------
# Player Class
# ---------------------------
class Player(Character):
    def __init__(self, x, y, image):
        super().__init__(x, y, 80, 120, hp=120, speed=6, strength=20)
        self.image = image
        self.rect.width = image.get_width()
        self.rect.height = image.get_height()
        

    def handle_input(self, keys):
        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -self.speed
        if keys[pygame.K_RIGHT]:
            dx = self.speed

        # Jumping
        if keys[pygame.K_UP] and not self.is_jumping:
            self.is_jumping = True
            self.vertical_speed = -self.JUMP_STRENGTH

        self.move(dx)


# ---------------------------
# Enemy Class
# ---------------------------
class Enemy(Character):
    def __init__(self, x, y, name="Enemy"):
        super().__init__(x, y, 80, 120, hp=100, speed=3, strength=10)
        self.name = name

    # Move horizontally toward the player
    def update_ai(self, player):
        if player.rect.centerx < self.rect.centerx:
            self.move(-self.speed)
        elif player.rect.centerx > self.rect.centerx:
            self.move(self.speed)


# ---------------------------
# Door Class
# ---------------------------
class Door:
    def __init__(self, x, y, width, height, enemy_name, is_unlocked=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.enemy_name = enemy_name
        self.is_unlocked = is_unlocked
        self.is_cleared = False

    def draw(self, screen):
        pass

    def is_player_in_front(self, player):
        return self.rect.colliderect(player.rect)


# ---------------------------
# Game Manager Class
# ---------------------------
class Game:
    def play_music(self, path):
        """Change background music only if it's different."""
        if self.current_music == path:
            return
        
        # Sound
        pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(-1)
        self.current_music = path

    def __init__(self):
        pygame.mixer.init()
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Anime Battle")
        self.clock = pygame.time.Clock()
        self.door_enter_cooldown_until = 0

        #Fonts
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        self.big_font = pygame.font.SysFont(None, 80)

        # Player img
        self.player_image = pygame.image.load("img/player.png").convert_alpha()
        self.player_image = pygame.transform.scale(self.player_image, (80, 120))  

        # Backgrounds img
        self.battle_backgrounds = {
            "Naruto": pygame.transform.scale(pygame.image.load("img/bg_naruto.jpg"), (SCREEN_WIDTH, SCREEN_HEIGHT)),
            "Luffy": pygame.transform.scale(pygame.image.load("img/bg_luffy.jpg"), (SCREEN_WIDTH, SCREEN_HEIGHT)),
        }
        
        self.room_bg = pygame.transform.scale(
        pygame.image.load("img/room_bg.png"),
        (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Enemy img
        self.enemy_images = {
            "Naruto": pygame.transform.scale(pygame.image.load("img/enemy_naruto.png"), (80, 120)),
            "Luffy": pygame.transform.scale(pygame.image.load("img/enemy_luffy.png"), (80, 120)),
        }

        # Game over text
        self.game_over_text = "Game Over - Press R to Restart"

        self.info_message = ""
        self.info_message_until = 0

        self.state = "menu"

        # Player
        self.player = Player(100, SCREEN_HEIGHT - 100, self.player_image)

        # Doors
        self.doors = [
            Door(130, 200, 140, 350, "Naruto"),
            Door(530, 200, 140, 350, "Luffy"),
        ]

        self.current_enemy = None
        self.current_door = None

        self.player_attack_cooldown = 0
        self.enemy_attack_cooldown = 0

        # ---------------------------
        # Sounds
        # ---------------------------

        # Background music
        self.room_bgm = "sound/room_bgm.mp3"
        self.naruto_bgm = "sound/naruto_bgm.mp3"
        self.luffy_bgm = "sound/luffy_bgm.mp3"
        self.current_music = None

        # Sound effects
        self.snd_punch = pygame.mixer.Sound("sound/punch.wav")
        self.snd_fight = pygame.mixer.Sound("sound/fight.wav")

    # ---------------------------
    # Main Loop
    # ---------------------------
    def run(self):
        while True:
            self.clock.tick(FPS)
            self.handle_events()

            if self.state == "menu":
                self.update_menu()
            elif self.state == "room":
                self.update_room()
            elif self.state == "battle":
                self.update_battle()
            elif self.state == "game_over":
                self.update_game_over()

            pygame.display.flip()

    # ---------------------------
    # Event Handling
    # ---------------------------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    # ---------------------------
    # MENU
    # ---------------------------
    def update_menu(self):
        self.play_music(self.room_bgm)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            self.state = "room"

        self.screen.fill((0, 0, 0))
        text = self.font.render("Anime Battle - Press ENTER to Start",
                                True, (255, 255, 255))
        self.screen.blit(text, (60, SCREEN_HEIGHT // 2))


    # ---------------------------
    # ROOM
    # ---------------------------
    def update_room(self):
        keys = pygame.key.get_pressed()
        self.play_music(self.room_bgm)
        self.player.handle_input(keys)
        self.player.update()

        # Room background image
        self.screen.blit(self.room_bg, (0, 0))

        # Ground
        pygame.draw.rect(
            self.screen,
            (120, 70, 20),
            (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
        
        # Title text
        title = self.font.render("Choose a Door", True, (0, 0, 0))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 20))

        # win/lose message 
        now = pygame.time.get_ticks()
        if self.info_message and now < self.info_message_until:
            msg = self.small_font.render(self.info_message, True, (255, 255, 0))
            msg_x = SCREEN_WIDTH // 2 - msg.get_width() // 2
            msg_y = 60  # below "Choose a Door"
            self.screen.blit(msg, (msg_x, msg_y))
        else:
            self.info_message = ""

        for door in self.doors:
            door.draw(self.screen)

        self.player.draw(self.screen, (0, 150, 255))

        # Door interaction
        for door in self.doors:
            if door.is_unlocked and not door.is_cleared and door.is_player_in_front(self.player):
                msg = self.font.render("Press SPACE to enter battle", True, (0, 0, 0))
                self.screen.blit(msg, (240, 70))

                if now >= self.door_enter_cooldown_until and keys[pygame.K_SPACE]:
                    self.start_battle(door)
                    return


    def start_battle(self, door):
        self.current_door = door
        self.current_enemy = Enemy(600, SCREEN_HEIGHT - 100, name=door.enemy_name)
        self.player.hp = self.player.max_hp
        self.current_enemy.hp = self.current_enemy.max_hp

        self.current_enemy.image = self.enemy_images[door.enemy_name]
        self.current_battle_bg = self.battle_backgrounds[door.enemy_name]

        # Battle backmusic
        if door.enemy_name == "Naruto":
            self.play_music(self.naruto_bgm)
        elif door.enemy_name == "Luffy":
            self.play_music(self.luffy_bgm)


        # FIGHT sound
        pygame.mixer.Sound.play(self.snd_fight)

        self.player_attack_cooldown = 0
        self.enemy_attack_cooldown = 0

        self.player.rect.x = 100
        self.player.rect.y = self.player.ground_y

        self.battle_start_time = pygame.time.get_ticks() 
        self.enemy_move_delay = 1000 

        self.show_fight_text = True
        self.fight_text_until = pygame.time.get_ticks() + 1000

        self.state = "battle"


    # ---------------------------
    # BATTLE
    # ---------------------------
    def update_battle(self):
        keys = pygame.key.get_pressed()

        # Cooldowns
        if self.player_attack_cooldown > 0:
            self.player_attack_cooldown -= 1
        if self.enemy_attack_cooldown > 0:
            self.enemy_attack_cooldown -= 1

        now = pygame.time.get_ticks()

        # Delay player and enemy
        can_act = now - self.battle_start_time > self.enemy_move_delay

        # Player movement + gravity
        if can_act:
            self.player.handle_input(keys)
        self.player.update()


        # Enemy logic
        if can_act and self.current_enemy.is_alive():
            self.current_enemy.update_ai(self.player)
            self.current_enemy.update()


        # Player attack
        if can_act and keys[pygame.K_SPACE] and self.player_attack_cooldown == 0:
            pygame.mixer.Sound.play(self.snd_punch)
            if self.player.rect.colliderect(self.current_enemy.rect):
                self.current_enemy.take_damage(self.player.strength)

                if self.player.rect.centerx < self.current_enemy.rect.centerx:
                    self.current_enemy.apply_knockback(3)   # enemy pushed right
                else:
                    self.current_enemy.apply_knockback(-3)

            self.player_attack_cooldown = 20

        # Enemy attack
        if can_act and self.enemy_attack_cooldown == 0 and self.current_enemy.rect.colliderect(self.player.rect):
            self.player.take_damage(self.current_enemy.strength)

            if self.current_enemy.rect.centerx < self.player.rect.centerx:
                self.player.apply_knockback(1)   # player pushed right
            else:
                self.player.apply_knockback(-1)

            self.enemy_attack_cooldown = 30

        # Lose
        if not self.player.is_alive():
            self.game_over_text = "Game Over - Press R to Restart"
            self.state = "game_over"

        # Win
        if not self.current_enemy.is_alive():
            self.current_door.is_cleared = True

            all_cleared = all(door.is_cleared for door in self.doors)

            if all_cleared:
                self.game_over_text = "You won the game! Press R to Restart"
                self.state = "game_over"
            else:
                self.info_message = f"You defeated {self.current_enemy.name}!"
                self.info_message_until = pygame.time.get_ticks() + 2000
                self.state = "room"
                self.player.rect.x = 100
                self.player.rect.y = self.player.ground_y
                self.door_enter_cooldown_until = pygame.time.get_ticks() + 400

            return

        # Background transparent
        self.screen.blit(self.current_battle_bg, (0, 0))
        dark_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        dark_surface.set_alpha(150) 
        dark_surface.fill((0, 0, 0))
        self.screen.blit(dark_surface, (0, 0))
        self.player.draw(self.screen, (0, 150, 255))
        self.current_enemy.draw(self.screen, (255, 100, 100))

        info = self.small_font.render("SPACE to attack | ESC to back", True, (0, 0, 0))
        self.screen.blit(info, (290, 18))

        if can_act and keys[pygame.K_ESCAPE]:
            self.state = "room"
            self.player.rect.x = 100
            self.player.rect.y = self.player.ground_y
            self.door_enter_cooldown_until = pygame.time.get_ticks() + 400

        pygame.draw.rect(
            self.screen,
            (20, 100, 20),
            (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
        
        #FIGHT text
        now = pygame.time.get_ticks()
        if self.show_fight_text and now < self.fight_text_until:
            fight_txt = self.big_font.render("FIGHT!", True, (0, 0, 0))
            fight_x = SCREEN_WIDTH // 2 - fight_txt.get_width() // 2
            fight_y = SCREEN_HEIGHT // 2 - fight_txt.get_height() // 2
            self.screen.blit(fight_txt, (fight_x, fight_y))
        else:
            self.show_fight_text = False


        # HP bars
        player_ratio = self.player.hp / self.player.max_hp
        player_bar_width = 300
        player_bar_height = 20
        player_bar_x = 40
        player_bar_y = 40

        pygame.draw.rect(self.screen,(255, 255, 255),
            (player_bar_x, player_bar_y, player_bar_width, player_bar_height),2)
        
        pygame.draw.rect(self.screen,(0, 200, 255),
            (player_bar_x, player_bar_y, player_bar_width * player_ratio, player_bar_height))

        enemy_ratio = self.current_enemy.hp / self.current_enemy.max_hp
        enemy_bar_width = 300
        enemy_bar_height = 20
        enemy_bar_x = SCREEN_WIDTH - 40 - enemy_bar_width
        enemy_bar_y = 40

        pygame.draw.rect(self.screen,(255, 255, 255),
            (enemy_bar_x, enemy_bar_y, enemy_bar_width, enemy_bar_height),2)
        
        pygame.draw.rect(self.screen,(255, 150, 150),
            (enemy_bar_x, enemy_bar_y, enemy_bar_width * enemy_ratio, enemy_bar_height))


    # ---------------------------
    # GAME OVER
    # ---------------------------
 
    def update_game_over(self):
        self.screen.fill((0, 0, 0))

        text = self.font.render(self.game_over_text, True, (255, 255, 255))
        self.screen.blit(
            text,
            (SCREEN_WIDTH // 2 - text.get_width() // 2,
             SCREEN_HEIGHT // 2 - text.get_height() // 2)
        )

        # Restart text
        hint = self.small_font.render("Press R to restart", True, (180, 180, 180))
        self.screen.blit(
            hint,
            (SCREEN_WIDTH // 2 - hint.get_width() // 2,
             SCREEN_HEIGHT // 2 + 30)
        )

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            self.player = Player(100, SCREEN_HEIGHT - GROUND_HEIGHT - 60, self.player_image)
            for door in self.doors:
                door.is_cleared = False
            self.current_enemy = None
            self.current_door = None
            self.info_message = ""
            self.state = "menu"

# Run Game
if __name__ == "__main__":
    game = Game()
    game.run()
