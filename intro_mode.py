import game_framework
import character_select_mode
import common
from pico2d import *

STATE_MENU     = 'menu'
STATE_IP_INPUT = 'ip_input'

image     = None
font      = None
running   = True
state     = STATE_MENU
ip_buffer = ''

def init():
    global image, font, running, state, ip_buffer
    image     = load_image('GameMode_Image/Game_Intro_Image.png')
    font      = load_font('ENCR10B.TTF', 20)
    running   = True
    state     = STATE_MENU
    ip_buffer = ''

def finish():
    global image, font
    del image
    image = None
    font  = None

def update():
    global running
    if running == False:
        game_framework.change_mode(character_select_mode)

def draw():
    clear_canvas()
    image.draw(400, 300, 800, 600)
    if state == STATE_IP_INPUT:
        font.draw(130, 340, 'SERVER IP  (Enter: confirm  ESC: back)', (255, 220, 0))
        display = ip_buffer if ip_buffer else '127.0.0.1'
        font.draw(280, 300, '> ' + display, (255, 255, 255))
    update_canvas()

def handle_events():
    global running, state, ip_buffer
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        if event.type == SDL_KEYDOWN:
            if state == STATE_MENU:
                if event.key == SDLK_1:
                    common.game_mode = 'Single Player'
                    running = False
                elif event.key == SDLK_2:
                    common.game_mode = 'Two Player'
                    running = False
                elif event.key == SDLK_3:
                    state     = STATE_IP_INPUT
                    ip_buffer = ''
            elif state == STATE_IP_INPUT:
                if event.key == SDLK_ESCAPE:
                    state = STATE_MENU
                elif event.key == SDLK_BACKSPACE:
                    ip_buffer = ip_buffer[:-1]
                elif event.key in (SDLK_RETURN, SDLK_KP_ENTER):
                    common.server_ip = ip_buffer.strip() if ip_buffer.strip() else '127.0.0.1'
                    common.game_mode = 'Network'
                    running = False
                elif event.key == SDLK_PERIOD:
                    ip_buffer += '.'
                elif SDLK_0 <= event.key <= SDLK_9:
                    ip_buffer += chr(event.key)
