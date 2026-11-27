from pico2d import *
import game_framework
import net_client
from character import Character
import game_world
import intro_mode
import common
from map import PalaceMap, Timer, HpBar, WinCount
from ai_controller import AIController
from character_frame import *
from interaction import HitBoxManager
import time
import queue
import packet
import net_state
from net_state import is_connected
from packet import pack_hit_report
from round_sync import *
from remote_controller import RemoteController
import os
font = None
TICK_INTERVAL = 0.05# 1/frame
tick_timer = 0.0

pressed_keys = set()# 현재 누르고 있는 키
pending_packets = []

running = True
debug_hitbox = False
round_over = False

ROUND_OVER_DELAY = 3.0
round_over_timer = 0.0
round_reset_timer = 0.0

def reset_round():
    global round_over, round_reset_timer
    round_over = False

    common.c1, common.c2 = common.characters

    if common.c1.hp <= 0 :
        common.c2.win_count += 1
    elif common.c2.hp <= 0 :
        common.c1.win_count += 1

    common.game_timer.total_time = 0.0
    common.c1.reset(100,120)
    common.c2.reset(700,120)
    common.c1.xPos = common.palace_map.w / 2 - 200
    common.c2.xPos = common.palace_map.w / 2 + 300
    common.palace_map.window_left = int(common.palace_map.w / 2 - common.palace_map.cw / 2)
    if common.c1.win_count >=2 or common.c2.win_count >= 2:
        game_framework.change_mode(intro_mode)

def handle_events():
    event_list = get_events()
    global running, pressed_keys
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                running = False
            elif  event.key == SDLK_r:
                game_framework.change_mode(intro_mode)
            elif event.key == SDLK_F1: #히트박스 그리기
                global debug_hitbox
                debug_hitbox = not debug_hitbox
            elif event.key == SDLK_F2: #플레이어 공격력 최대치로 조절
                common.c1.atk = 100
                common.c2.atk = 100
                pass
            elif event.key == SDLK_F4: #타이머 종료
                common.game_timer.total_time = 117.0
            else:
                # 키 입력 상태 저장
                pressed_keys.add(event.key)
                # 멀티인 경우
                if common.game_mode == 'Network':
                    # 내 캐릭터에만 이벤트 전달
                    my_character = common.characters[net_state.my_player_num]
                    my_character.handle_event(event)
                else:
                # 기존 오프라인 모드
                    for c in common.characters:
                        c.handle_event(event)
        elif event.type == SDL_KEYUP:
            pressed_keys.discard(event.key)

            # 멀티인 경우
            if common.game_mode == 'Network':
                my_character = common.characters[net_state.my_player_num]
                my_character.handle_event(event)

            # 싱글 및 로컬 2인 플레이
            else:
                for c in common.characters:
                    c.handle_event(event)
# 초기 설정
def init():
    global font

    if font is None:
        font_path = os.path.join(os.path.dirname(__file__), 'ENCR10B.TTF')
        font = load_font(font_path, 30)

    common.palace_map = PalaceMap()
    common.game_timer = Timer()
    common.hitbox_manager = HitBoxManager()
    common.round_over = False
    common.round_over_timer = 0.0
    common.match_over = False

    game_world.add_object(common.palace_map)
    game_world.add_object(common.game_timer, 1)
    # p1의 캐릭터 생성
    if common.game_mode == 'Single Player':
        if common.p1_character_num == 0:
            common.c1 = Character(ShingoFrameInfo(), keymap=common.KEYMAP_P1, x=100, y=120)
        elif common.p1_character_num == 1:
            common.c1 = Character(KimFrameInfo(), keymap=common.KEYMAP_P1, x=100, y=120)
        elif common.p1_character_num == 2:
            common.c1 = Character(YuriFrameInfo(), keymap=common.KEYMAP_P1, x=100, y=120)
        if common.stage_num == 0:
            common.c2 = Character(KimFrameInfo(), keymap=common.KEYMAP_P2, x=700, y=120)
            common.ai_player = AIController(common.c2, common.c1)

    # p2의 캐릭터 생성/멀티용 캐릭터 생성
    if common.game_mode == 'Two Player':
        if common.p1_character_num == 0:
            common.c1 = Character(ShingoFrameInfo(), keymap=common.KEYMAP_P1, x=100, y=120)
        elif common.p1_character_num == 1:
            common.c1 = Character(KimFrameInfo(), keymap=common.KEYMAP_P1, x=100, y=120)
        elif common.p1_character_num == 2:
            common.c1 = Character(YuriFrameInfo(), keymap=common.KEYMAP_P1, x=100, y=120)
        if common.p2_character_num == 0:
            common.c2 = Character(ShingoFrameInfo(), keymap=common.KEYMAP_P2, x=700, y=120)
        elif common.p2_character_num == 1:
            common.c2 = Character(KimFrameInfo(), keymap=common.KEYMAP_P2, x=700, y=120)
        elif common.p2_character_num == 2:
            common.c2 = Character(YuriFrameInfo(), keymap=common.KEYMAP_P2, x=700, y=120)

    if common.game_mode == 'Network':
        if common.p1_character_num == 0:
            common.c1 = Character(ShingoFrameInfo(), keymap=common.KEYMAP_P1, x=100, y=120)
        elif common.p1_character_num == 1:
            common.c1 = Character(KimFrameInfo(), keymap=common.KEYMAP_P1, x=100, y=120)
        elif common.p1_character_num == 2:
            common.c1 = Character(YuriFrameInfo(), keymap=common.KEYMAP_P1, x=100, y=120)
        if common.p2_character_num == 0:
            common.c2 = Character(ShingoFrameInfo(), keymap=common.KEYMAP_P1, x=700, y=120)
        elif common.p2_character_num == 1:
            common.c2 = Character(KimFrameInfo(), keymap=common.KEYMAP_P1, x=700, y=120)
        elif common.p2_character_num == 2:
            common.c2 = Character(YuriFrameInfo(), keymap=common.KEYMAP_P1, x=700, y=120)
        if net_state.my_player_num == 0:
            common.ai_player = RemoteController(common.c2)
        else:
            common.ai_player = RemoteController(common.c1)




    common.characters = [common.c1, common.c2]
    common.p1_HpBar = HpBar(common.c1, 175, 550)
    common.p2_HpBar = HpBar(common.c2, 625, 550)
    common.p1_win_counter = WinCount(common.c1, 280, 500)
    common.p2_win_counter = WinCount(common.c2, 487, 500)
    game_world.add_object(common.p1_HpBar, 1)
    game_world.add_object(common.p2_HpBar, 1)
    game_world.add_object(common.p1_win_counter, 1)
    game_world.add_object(common.p2_win_counter, 1)
    common.c1.xPos = common.palace_map.w/2 - 200
    common.c2.xPos = common.palace_map.w/2 + 300
    common.palace_map.window_left = int(common.palace_map.w/2 - common.palace_map.cw/2)
    if common.c1.xPos < common.c2.xPos:
        common.c1.face_dir = 1
        common.c2.face_dir = -1
    else:
        common.c1.face_dir = -1
        common.c2.face_dir = 1

    for c in common.characters:
        game_world.add_object(c)

    net_state.last_udp_recv_time = time.monotonic()
    net_state.is_udp_timeout = False

def update():
    global round_over, round_over_timer,round_reset_timer

    # 네트워크 게임 데이터 수신
    if common.game_mode == 'Network':
        recv_tick_packet()
        if not net_state.is_connected:
            game_framework.change_mode(intro_mode)
        # 매치 종료는 서버가 보낸 값으로만 판단
        if common.match_over:
            common.match_over = False
            game_framework.change_mode(intro_mode)
            return
        # 매치 종료는 서버가 보낸 값으로만 판단
        if common.match_over:
            common.match_over = False
            game_framework.change_mode(intro_mode)
            return
    # 기존 게임 업데이트
    game_world.update()


    common.c1, common.c2 = common.characters
    # 히트박스
    if common.hitbox_manager == None:
        common.hitbox_manager = HitBoxManager()

    if common.game_mode != 'Network':
        if common.game_mode == 'Single Player':
            common.ai_player.update()
            common.ai_player.run()
        if common.c1.hp <= 0 or common.c2.hp <= 0:
            if not round_over:
                round_over = True
                round_over_timer = ROUND_OVER_DELAY
            else:
                round_over_timer -= game_framework.frame_time
                if round_over_timer <= 0.0:
                    if common.c1.win_count >= 2 or common.c2.win_count >= 2:
                        game_framework.change_mode(intro_mode)
                    else:
                        reset_round()
        elif common.game_timer.total_time >= 60.0:
            if not round_over:
                round_over = True
                round_over_timer = ROUND_OVER_DELAY
            else:
                round_over_timer -= game_framework.frame_time
                if round_over_timer <= 0.0:
                    if common.c1.hp > common.c2.hp:
                        common.c1.win_count += 1
                    elif common.c2.hp > common.c1.hp:
                        common.c2.win_count += 1
                    if common.c1.win_count >= 2 or common.c2.win_count >= 2:
                        game_framework.change_mode(intro_mode)
                    else:
                        reset_round()

        if common.hitbox_manager:
            common.hitbox_manager.detect_body_overlaps()# 신체 겹침 해결
            common.hitbox_manager.detect_is_opponent_attacking()# 공격판정 확인
            common.hitbox_manager.update_face_dir(common.characters[0], common.characters[1])#  마주보게 하고
            common.hitbox_manager.detect_attack_hits()# 양측 피격판정
    elif common.game_mode == 'Network':
        # 서버에서 받은 네트워크 정보로 업데이트
        common.ai_player.update()

        if common.hitbox_manager:
            common.hitbox_manager.detect_body_overlaps()
            common.hitbox_manager.detect_is_opponent_attacking()
            common.hitbox_manager.update_face_dir(common.characters[0], common.characters[1])
            common.hitbox_manager.detect_online_hit(common.characters, net_state.my_player_num)# 내 공격판정




    # 네트워크 입력 전송
    if common.game_mode == 'Network':
        send_tick_packet()

def draw():
    clear_canvas()
    game_world.render()
    if debug_hitbox:
        common.hitbox_manager.debug_draw()
    if common.round_over and font is not None and common.stage_winner is not None:
        # 반투명 배경
        #draw_rectangle(0, 0, get_canvas_width(), get_canvas_height())
        # 라운드 종료 문구
        message = f"{common.stage_winner}P WIN!"
        width = get_canvas_width() // 2
        font.draw(width - 50, 300, message, (0, 0, 255))

        message = f"ROUND OVER"
        font.draw(width - 80, 250, message, (255, 0, 0))

    update_canvas()


def finish():
    if common.game_mode == 'Network' and is_connected:
        net_state.send_queue.put((packet.PKT_LEAVE, None))
    game_world.clear()
    pass


# ----------------------------------------------------------------
def get_key_mask():
    keys = 0x00
    if 1 - net_state.my_player_num:
        for key in pressed_keys:
            keys |= packet.KEY_TO_MASK_P1.get(key, 0)
    else:
        for key in pressed_keys:
            keys |= packet.KEY_TO_MASK_P2.get(key, 0)

    return keys

instant_tick_time = 0.016
ATTACK_KEY_MASK = {'lp': packet.KEY_LP, 'rp': packet.KEY_RP, 'rk': packet.KEY_RK, 'lk': packet.KEY_LK}
ATTACK_MASK_ALL = packet.KEY_LP | packet.KEY_RP | packet.KEY_RK | packet.KEY_LK
# 패킷 송신
def send_tick_packet():

    my_character = common.characters[net_state.my_player_num]
    keys = get_key_mask()
    # 네트워크로는 어떤 위치에서든 1P 컨트롤
    flag = 0
    for key in pressed_keys:
        mask = packet.KEY_TO_MASK_P1.get(key, 0)
        flag |= mask
    # 공격 중에는 키를 뗐어도 공격 종류를 계속 실어 보낸다
    attack_key = getattr(my_character.state_machine.cur_state, 'attack_key', None)
    if isinstance(attack_key, str) and attack_key in ATTACK_KEY_MASK:
        flag = (flag & ~ATTACK_MASK_ALL) | ATTACK_KEY_MASK[attack_key]

    seq = net_state.send_seq
    frame = max(0, min(255, int(my_character.frame)))
    body = packet.pack_tick_c2s(
        net_state.send_seq,
        net_state.my_player_num,
        keys,
        int(my_character.xPos),
        int(my_character.yPos),
        my_character.face_dir,
        my_character.get_state_id(),
        frame,
        flag
    )
    net_state.send_queue.put((packet.PKT_TICK_C2S,body))

    net_state.send_seq = (net_state.send_seq + 1) & 0xFFFF
# 패킷 수신
def recv_tick_packet():
    if not net_state.is_connected:
        return
    while True:
        packet_data = common.net_client_obj.pop_packet()

        if packet_data is None:
            break

        packet_type, body = packet_data

        if packet_type == packet.PKT_TICK_S2C and len(body) >= packet.TICK_S2C_SIZE:

            data = packet.unpack_tick_s2c(body)
            # 라운드 공통 정보
            apply_round_sync(data)

            # 상대 플레이어 정보
            if net_state.my_player_num == 0:
                remote_data = data["p2"]
            else:
                remote_data = data["p1"]
            common.ai_player.apply_tick(remote_data)

        elif packet_type == packet.PKT_HIT_RESULT and len(body) >= packet.HIT_RESULT_SIZE:
            data = packet.unpack_hit_result(body)
            common.ai_player.apply_hit(data)
            # 피격 결과 반영
        elif packet_type == packet.PKT_ROUND_END and len(body) >= packet.ROUND_END_SIZE:
            print("packet.PKT_ROUND_END")
            data = packet.unpack_round_end(body)
            common.stage_winner = data["winner"]
            # A가 구현한 경기 종료 반영 함수
            handle_round_end(data)
        elif packet_type == packet.PKT_ROUND_START and len(body) >= packet.ROUND_START_SIZE:
            data = packet.unpack_round_start(body)
            # 서버가 보낸 다음 라운드 시작 반영
            handle_round_start(data)
    # 연결 끊김 확인
    now = time.monotonic()
    elapsed = now - net_state.last_udp_recv_time

    if elapsed >= net_state.UDP_TIMEOUT:
        if net_state.is_connected:
            print("UDP 연결 끊김 감지")
            net_state.is_connected = False

    elif elapsed >= net_state.UDP_WARNING:
        print("UDP 수신 지연")

    else:
        net_state.is_connected = True