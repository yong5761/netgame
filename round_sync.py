
import common
import packet
import net_state


def apply_round_sync(data):
    # 플레이어 체력 동기화
    common.c1.hp = data["p1_hp"]
    common.c2.hp = data["p2_hp"]

    # 경기 시간 동기화
    common.game_timer.remaining_time = data["remaining_time"]


def handle_round_end(data):
    # 라운드 종료 상태
    common.round_over = True

    # 서버가 보낸 누적 승수를 캐릭터에 반영
    common.c1.win_count = data['win_count1']
    common.c2.win_count = data['win_count2']

    # 라운드 종료 후 처리
    common.round_over_timer = 3.0

    # 매치 종료 여부는 서버가 정한다
    common.match_over = bool(data['match_over'])


def handle_round_start(data):
    # 서버가 보낸 시작 위치와 체력으로 라운드 초기화
    common.c1, common.c2 = common.characters

    common.c1.reset(data['start_x1'], 120)
    common.c2.reset(data['start_x2'], 120)
    common.c1.hp = data['hp1']
    common.c2.hp = data['hp2']

    common.game_timer.total_time = 0.0
    common.palace_map.window_left = int(common.palace_map.w / 2 - common.palace_map.cw / 2)

    common.round_over = False
    common.round_over_timer = 0.0

# 4바이트 상태 보고 생성 함수
def build_hit_report(victim, attacker, dmg, guarding):
    return bytes((victim, attacker, dmg, int(guarding)))


def report_hit(victim, attacker, dmg, guarding):
    if not net_state.is_connected:
        return False
    if net_state.my_player_num not in (0, 1):
        return False
    if victim != net_state.my_player_num:
        return False

    body = build_hit_report(victim, attacker, dmg, guarding)

    net_state.send_queue.put((packet.PKT_HIT_REPORT, body))

    return True