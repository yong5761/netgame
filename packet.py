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

# 상태 플래그 비트
FLAG_ATTACKING  =0x01   # 공격 중
FLAG_GUARDING   =0x02   # 가드 중
FLAG_HITTED     =0x04   # 맞은 상태
FLAG_DAMAGEABLE =0x08   # 데미지를 받을 수 있는 상태


# UDP 패킷 헤더 (size, pkt_type) <-> buf
HEADER_FORMAT = "!HB"   # 빅 앤디언, 부호없는 2바이트Unsigned Short , 부호없는 1바이트Unsigned Char
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

# 직렬화
def pack_header(size, pkt_type):
    return struct.pack(size, pkt_type)
# 역직렬화
def unpack_header(buf):
    # 
    if len(buf) < HEADER_SIZE:# 검사
        return None
    size, pkt_type = struct.unpack(HEADER_FORMAT,buf[:HEADER_SIZE])
    return size, pkt_type

def pack_tick_c2s(seq, keys, x, y, face, state, frame, flag):
    pass

def unpack_tick_s2c(body):
    pass