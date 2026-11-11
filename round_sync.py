import packet
import net_state

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
    