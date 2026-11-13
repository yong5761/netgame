#include "hit_judge.h"
#include <cstdio>

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

    if (m_report.guard > 1)
        return;
    if (m_report.guard == 1)
        return;
    if (m_report.damage == 0)
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
    const PlayerState& defender = m_playerState[m_report.victim];

    int distance = std::abs(static_cast<int>(attacker.x)-static_cast<int>(defender.x))
}

void HitJudge::CheckCooldown() {
    printf("[HitJudge] CheckCooldown 호출\n");
    if (!m_valid)
        return;

    int victim = m_report.victim;

    
}

void HitJudge::SendResult(int defenderNum) {
    printf("[HitJudge] SendResult 호출\n");
}
