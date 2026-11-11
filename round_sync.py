# 4바이트 상태 보고 생성 함수
def build_hit_report(victim, attacker, dmg, guarding):
    return bytes((victim, attacker, dmg, int(guarding)))