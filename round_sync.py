
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

    # 서버에서 전달한 승자 정보
    winner = data["winner"]

    if winner == 0:
        common.p1_win_counter.add_win()
    elif winner == 1:
        common.p2_win_counter.add_win()

    # 라운드 종료 후 처리
    common.round_over_timer = 3.0

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