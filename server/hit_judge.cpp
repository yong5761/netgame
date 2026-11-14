#include "hit_judge.h"
#include <cstdio>
#include <stdlib.h>
#include <string.h>

void HitJudge::HandleReport(int attackerNum, int defenderNum) {
    printf("[HitJudge] HandleReport 호출\n");

    m_valid = false;

    if (!m_ready)
        return;
    m_ready = false;

    if (m_report.attacker != attackerNum ||
        m_report.victim != defenderNum)
        return;

    m_now = GetTickCount();

    Verify();

    if (!m_valid)
        return;
}

void HitJudge::Verify() {
    printf("[HitJudge] Verify 호출\n");
    m_valid = false;

    if (m_report.attacker == m_report.victim)
        return;

    if (m_senderNum < 0 || m_report.victim)
        return;

    if (m_report.guard > 1)
        return;
    if (m_report.guard == 1)
        return;

    if (m_report.damage != 5 && m_report.damage != 10)
        return;

    m_valid = true;

    CheckDistance();

    if (!m_valid)
        return;

    CheckCooldown();
}

void HitJudge::CheckDistance() {
    printf("[HitJudge] CheckDistance 호출\n");
    if (!m_valid)
        return;

    const PlayerState& attacker = m_playerStates[m_report.attacker];
    const PlayerState& defender = m_playerStates[m_report.victim];

    int distance = abs(static_cast<int>(attacker.x) - static_cast<int>(defender.x));
        
    if (distance > m_minDist)
        m_valid = false;   
}

void HitJudge::CheckCooldown() {
    printf("[HitJudge] CheckCooldown 호출\n");
    if (!m_valid)
        return;

    int victim = m_report.victim;

    if (!m_hasLastHit[victim])
        return;

    DWORD elapsed = m_now - m_lastHitTick[victim];

    if (elapsed < m_cooldownMs)
        m_valid = false;
}

void HitJudge::SendResult(int defenderNum) {
    printf("[HitJudge] SendResult 호출\n");

    HitResultBody body = m_result;
    body.Hton();

    PacketHeader header{};
    header.size = htons(static_cast<uint16_t>(sizeof(HitResultBody)));
    header.type = PKT_HIT_RESULT;

    char buffer[sizeof(PacketHeader) + sizeof(HitResultBody)];

    memcpy(buffer, &header, sizeof(header));
    memcpy(buffer + sizeof(header), &body, sizeof(body));
}
