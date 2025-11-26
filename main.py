import pygame, os, sys, random, time
from settings import *
from scoreboard import save_score
import voice_control 

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Voice Dino Runner")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

bg = pygame.image.load("Assets/BackGround/BG.png").convert()
bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
bg_x = 0

pygame.mixer.init()
jump_sound = pygame.mixer.Sound("Assets/Sounds/jump.mp3")
dead_sound = pygame.mixer.Sound("Assets/Sounds/dead.mp3")
pygame.mixer.music.load("Assets/Sounds/bg_music.mp3")

def load_anim(folder, prefix, size=(PLAYER_W, PLAYER_H)):
    frames = []
    if not os.path.isdir(folder):
        return frames
    for f in sorted(os.listdir(folder)):
        if f.startswith(prefix) and f.endswith(".png"):
            img = pygame.image.load(os.path.join(folder, f)).convert_alpha()
            img = pygame.transform.scale(img, size)
            frames.append(img)
    return frames

dino_folder = "Sprites/Dino"
Run_frames = load_anim(dino_folder, "Run")
jump_frames = load_anim(dino_folder, "Jump")
dead_frames = load_anim(dino_folder, "Dead")
run_frames = Run_frames if Run_frames else load_anim(dino_folder, "Idle")

cactus_img = pygame.image.load("Sprites/Cactus/Cactus.png").convert_alpha()
cactus_img = pygame.transform.scale(cactus_img, (50, 60))

def draw_text(text, pos, color=(0,0,0), size=28):
    font2 = pygame.font.SysFont(None, size)
    screen.blit(font2.render(text, True, color), pos)

def spawn_cactus():
    img_rect = cactus_img.get_rect()
    img_rect.x = WIDTH + random.randint(100, 300)
    img_rect.y = GROUND_Y - img_rect.height
    # collision rect is a shrunk copy to avoid overly-large hitboxes
    col_rect = img_rect.copy()
    try:
        shrink = CACTUS_HITBOX_SHRINK
        col_rect.inflate_ip(-shrink[0], -shrink[1])
    except Exception:
        # fallback to a reasonable default
        col_rect.inflate_ip(-20, -10)
    obstacles.append((img_rect, col_rect))

def reset_game():
    global player, vel_y, on_ground, obstacles, last_spawn, start_time, dead, score, cactus_active, last_jump_time
    player = pygame.Rect(100, GROUND_Y - PLAYER_H, PLAYER_W, PLAYER_H)
    player.inflate_ip(-20, -10)
    vel_y = 0
    on_ground = True
    obstacles = []
    last_spawn = 0
    start_time = time.time()
    dead = False
    score = 0
    cactus_active = False
    # allow immediate voice jump after reset
    last_jump_time = pygame.time.get_ticks() - JUMP_COOLDOWN
    pygame.mixer.music.play(-1)

# last jump time (uses JUMP_COOLDOWN from settings)
last_jump_time = 0

reset_game()
game_speed = 8
spawn_gap = 1500
voice_mode = True

voice_control.start_listening()

running = True
while running:
    dt = clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_v:
            voice_mode = not voice_mode

    bg_x -= game_speed // 2
    if bg_x <= -WIDTH:
        bg_x = 0
    screen.blit(bg, (bg_x, 0))
    screen.blit(bg, (bg_x + WIDTH, 0))

    keys = pygame.key.get_pressed()
    if not dead:
        if keys[pygame.K_SPACE] and on_ground:
            vel_y = -JUMP_STRENGTH
            on_ground = False
            jump_sound.play()

        if voice_mode and voice_control.voice_ready:
            try:
                now = pygame.time.get_ticks()
                print("voice mode", voice_mode, "ready", voice_control.voice_ready, flush=True)
                print("queue size =", voice_control.command_queue.qsize())
                while not voice_control.command_queue.empty():
                    cmd = voice_control.command_queue.get_nowait().lower()
                    print("cmd = ", repr(cmd), 'type =', type(cmd))
                    print(f"[VOICE COMMAND RECEIVED] {cmd}  on_ground={on_ground} cooldown={now-last_jump_time}ms")

                    if "jump" in cmd or "jump-dino" in cmd or "porcupine" in cmd:
                        if on_ground and now - last_jump_time > JUMP_COOLDOWN:
                            print("[VOICE JUMP TRIGGERED]")
                            vel_y = -JUMP_STRENGTH
                            on_ground = False
                            jump_sound.play()
                            last_jump_time = now
            except Exception as e:
                print("[VOICE LOOP ERROR]", e)

    vel_y += GRAVITY
    player.y += vel_y
    if player.y >= GROUND_Y - player.height:
        player.y = GROUND_Y - player.height
        vel_y = 0
        on_ground = True

    if not cactus_active and time.time() - start_time > 10:
        cactus_active = True
        print("[INFO] Cactus spawning activated.")

    now = pygame.time.get_ticks()
    if cactus_active and now - last_spawn > spawn_gap and not dead:
        spawn_cactus()
        last_spawn = now

    for img_r, col_r in obstacles:
        img_r.x -= game_speed
        col_r.x -= game_speed
        screen.blit(cactus_img, (img_r.x, img_r.y))
    obstacles = [(ir, cr) for (ir, cr) in obstacles if ir.x > -60]

    if not dead:
        for img_r, col_r in obstacles:
            if player.colliderect(col_r):
                dead = True
                dead_sound.play()
                pygame.mixer.music.stop()

    t = pygame.time.get_ticks()
    frame_time = 100
    if dead and dead_frames:
        frames = dead_frames
    elif not on_ground and jump_frames:
        frames = jump_frames
    else:
        frames = run_frames if run_frames else jump_frames

    if frames:
        frame_index = (t // frame_time) % len(frames)
        current_image = frames[frame_index]
    else:
        current_image = pygame.Surface((PLAYER_W, PLAYER_H))
        current_image.fill((0, 0, 0))

    screen.blit(current_image, (player.x, player.y))

    if not dead:
        score = int(time.time() - start_time)
    draw_text(f"Score: {score}", (10, 10))
    draw_text(f"Voice: {'ON' if voice_mode else 'OFF'}", (10, 40))
    if voice_control.voice_ready:
        draw_text("Listening...", (WIDTH - 150, 10), (0, 255, 0), 20)

    if dead:
        high_scores = save_score(score)
        high = high_scores[0] if high_scores else score

        game_over = True
        while game_over:
            screen.fill((0, 0, 0))
            draw_text("GAME OVER", (WIDTH//2 - 90, HEIGHT//2 - 100), (255, 0, 0), 48)
            draw_text(f"Your Score: {score}", (WIDTH//2 - 80, HEIGHT//2 - 40), (255, 255, 255))
            draw_text(f"High Score: {high}", (WIDTH//2 - 80, HEIGHT//2), (255, 255, 255))

            play_again_text = pygame.font.SysFont(None, 36).render("PLAY AGAIN", True, (0, 0, 0))
            play_again_rect = play_again_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 80))

            mx, my = pygame.mouse.get_pos()
            color = (255,255,255) if play_again_rect.collidepoint(mx,my) else (200,200,200)
            pygame.draw.rect(screen, color, play_again_rect.inflate(20, 10))
            screen.blit(play_again_text, play_again_rect)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = False
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if play_again_rect.collidepoint(mx, my):
                        reset_game()
                        game_over = False
                        dead = False
                        break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        reset_game()
                        game_over = False
                        dead = False
                        break

            clock.tick(30)

    pygame.display.flip()

pygame.quit()
sys.exit()
