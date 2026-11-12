from pico2d import *
import struct

# ---------------패킷 종류 상수 대응표---------------
# TCP 패킷 (접속 및 게임 진행 제어)
PKT_JOIN        = 1   # 접속 요청
PKT_ASSIGN      = 2   # 플레이어 번호 통보
PKT_SELECT      = 3   # 캐릭터 선택
PKT_MATCH_START = 4   # 경기 시작
PKT_ROUND_START = 5   # 라운드 시작
PKT_HIT_REPORT  = 6   # 피격 보고 (클라이언트 -> 서버)
PKT_HIT_RESULT  = 7   # 피격 결과 (서버 -> 클라이언트)
PKT_ROUND_END   = 8   # 라운드 결과
PKT_LEAVE       = 9   # 접속 종료
# UDP 패킷 (실시간 게임 상태 동기화)
PKT_TICK_C2S    = 20  # 클라이언트 -> 서버
PKT_TICK_S2C    = 21  # 서버 -> 클라이언트

# -----캐릭터 동작 상태 상수 (C++ / Python 동일)-----
STATE_IDLE          = 0   # 대기
STATE_WALK          = 1   # 걷기
STATE_JUMP          = 2   # 점프
STATE_MOVE_JUMP     = 3   # 이동 점프
STATE_RUN           = 4   # 달리기
STATE_RUN_JUMP      = 5   # 달리며 점프
STATE_BACK_DASH     = 6   # 백 대시
STATE_SIT_DOWN      = 7   # 앉기

STATE_SIT_UP        = 8   # 일어서기
STATE_NORMAL_ATTACK = 9   # 일반 공격
STATE_AIR_ATTACK    = 10  # 공중 공격
STATE_SIT_ATTACK    = 11  # 앉아서 공격
STATE_GUARD         = 12  # 방어
STATE_GET_HIT       = 13  # 피격
STATE_COMBO_ATTACK  = 14  # 연속 공격
STATE_DEAD          = 15  # 사망

# 상태 플래그 비트 (common.py KEYMAP)
KEY_LEFT    = 0x01
KEY_LP      = 0x10
KEY_RIGHT   = 0x02
KEY_RP      = 0x20
KEY_UP      = 0x04
KEY_RK      = 0x40
KEY_DOWN    = 0x08
KEY_LK      = 0x80
#
KEY_TO_MASK = {
# P1
    SDLK_a: KEY_LEFT,
    SDLK_d: KEY_RIGHT,
    SDLK_w: KEY_UP,
    SDLK_s: KEY_DOWN,
    SDLK_f: KEY_LP,
    SDLK_g: KEY_RP,
    SDLK_b: KEY_RK,
    SDLK_c: KEY_LK,
# P2
    SDLK_LEFT: KEY_LEFT,    
    SDLK_RIGHT: KEY_RIGHT,
    SDLK_UP: KEY_UP,
    SDLK_DOWN: KEY_DOWN,
    SDLK_KP_4: KEY_LP,
    SDLK_KP_5: KEY_RP,
    SDLK_KP_2: KEY_RK,
    SDLK_KP_1: KEY_LK
}
# 상태 플래그 비트
FLAG_ATTACKING  =0x01   # 공격 중
FLAG_GUARDING   =0x02   # 가드 중
FLAG_HITTED     =0x04   # 맞은 상태
FLAG_DAMAGEABLE =0x08   # 데미지를 받을 수 있는 상태


# 패킷 헤더 (size, pkt_type) <-> buf
HEADER_FORMAT = "!HB"   # 빅 앤디언, 부호없는 2바이트Unsigned Short , 부호없는 1바이트Unsigned Char
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

# 직렬화
def pack_header(size, pkt_type):
    return struct.pack(HEADER_FORMAT, size, pkt_type)
# 역직렬화
def unpack_header(buf):
    if len(buf) < HEADER_SIZE:# 검사
        return None
    size, pkt_type = struct.unpack(HEADER_FORMAT,buf[:HEADER_SIZE])
    return size, pkt_type

TICK_C2S_FORMAT = "!HBBIBBBB"
TICK_C2S_SIZE = struct.calcsize(TICK_C2S_FORMAT)

def pack_tick_c2s(seq, keys, x, y, face, state, frame, flag):
    return struct.pack(TICK_C2S_FORMAT, seq, keys, x, y, face, state, frame, flag)


TICK_S2C_FORMAT = "!H4hBBBB4hBBH"
TICK_S2C_SIZE = struct.calcsize(TICK_S2C_FORMAT)

def unpack_tick_s2c(body):
    if len(body) != TICK_S2C_SIZE:
        raise ValueError("잘못된 TICK_S2C 패킷 크기")
    data = struct.unpack(TICK_S2C_FORMAT, body)
    return {
        "seq": data[0],
        "p1": {
            "x": data[1],
            "y": data[2],
            "face": data[3],
            "state": data[4],
        },
        "p2": {
            "x": data[5],
            "y": data[6],
            "face": data[7],
            "state": data[8],
        },
        "p1_hp": data[9],
        "p2_hp": data[10],
        "remaining_time": data[11]
    }


# =========================================================
# 본문 구조체 포맷 (C++ packet.h와 1:1 대응)
# =========================================================

# 1. AssignBody
ASSIGN_FORMAT = "!B"
ASSIGN_SIZE = struct.calcsize(ASSIGN_FORMAT)

# 2. SelectBody
SELECT_FORMAT = "!B"
SELECT_SIZE = struct.calcsize(SELECT_FORMAT)

# 3. MatchStartBody
MATCH_START_FORMAT = "!2B"
MATCH_START_SIZE = struct.calcsize(MATCH_START_FORMAT)

# 4. RoundStartBody
ROUND_START_FORMAT = "!2h3B"
ROUND_START_SIZE = struct.calcsize(ROUND_START_FORMAT)

# 5. HitReportBody
HIT_REPORT_FORMAT = "!4B"
HIT_REPORT_SIZE = struct.calcsize(HIT_REPORT_FORMAT)

# 6. HitResultBody
HIT_RESULT_FORMAT = "!4Bh"
HIT_RESULT_SIZE = struct.calcsize(HIT_RESULT_FORMAT)

# 7. RoundEndBody
ROUND_END_FORMAT = "!4B"
ROUND_END_SIZE = struct.calcsize(ROUND_END_FORMAT)

# 8. TickC2SBody
TICK_C2S_FORMAT = "!HBBhhbBBB"
TICK_C2S_SIZE = struct.calcsize(TICK_C2S_FORMAT)

# 9. PlayerState
PLAYER_STATE_FORMAT = "!hhbBBB"
PLAYER_STATE_SIZE = struct.calcsize(PLAYER_STATE_FORMAT)

# 10. TickS2CBody
TICK_S2C_FORMAT = "!" + "H" + PLAYER_STATE_FORMAT[1:] * 2 + "BBH"
TICK_S2C_SIZE = struct.calcsize(TICK_S2C_FORMAT)


# =========================================================
# 구조체 크기 검증
# =========================================================

assert ASSIGN_SIZE == 1
assert SELECT_SIZE == 1
assert MATCH_START_SIZE == 2
assert ROUND_START_SIZE == 7
assert HIT_REPORT_SIZE == 4
assert HIT_RESULT_SIZE == 6
assert ROUND_END_SIZE == 4
assert TICK_C2S_SIZE == 12
assert PLAYER_STATE_SIZE == 8
assert TICK_S2C_SIZE == 22

# AssignBody
def pack_assign(player):
    return struct.pack(ASSIGN_FORMAT, player)
# SelectBody
def pack_select(char_num):
    return struct.pack(SELECT_FORMAT, char_num)
# MatchStartBody
def pack_match_start(char_num):
    return struct.pack(MATCH_START_FORMAT, *char_num)
# RoundStartBody
def pack_round_start(start_x, hp, round_num):
    return struct.pack(
        ROUND_START_FORMAT,
        start_x[0], start_x[1],
        hp[0], hp[1],
        round_num
    )
# HitReportBody
def pack_hit_report(victim, attacker, damage, guard):
    return struct.pack(
        HIT_REPORT_FORMAT,
        victim, attacker, damage, guard
    )
# HitResultBody
def pack_hit_result(victim, attacker, damage, hp, knock_x):
    return struct.pack(
        HIT_RESULT_FORMAT,
        victim, attacker, damage, hp, knock_x
    )
# RoundEndBody
def pack_round_end(winner, win_count, match_over):
    return struct.pack(
        ROUND_END_FORMAT,
        winner, win_count[0], win_count[1], match_over
    )
# TickC2SBody
def pack_tick_c2s(seq, player, keys, x, y, face, state, frame, flag):
    return struct.pack(
        TICK_C2S_FORMAT,
        seq, player, keys, x, y, face, state, frame, flag
    )
# PlayerState
def pack_player_state(x, y, face, state, frame, flag):
    return struct.pack(
        PLAYER_STATE_FORMAT,
        x, y, face, state, frame, flag
    )
# TickS2CBody
def pack_tick_s2c(seq, p1, p2, hp, time_left):
    return struct.pack(
        TICK_S2C_FORMAT,
        seq,
        *p1,
        *p2,
        hp[0], hp[1],
        time_left
    )