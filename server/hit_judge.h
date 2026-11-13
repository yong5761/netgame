#pragma once
#define WIN32_LEAN_AND_MEAN
#include <winsock2.h>
#include <cstdint>
#include "packet.h"

class HitJudge {
public:
    void HandleReport(int attackerNum, int defenderNum);
    void Verify();

private:
    void CheckDistance();
    void CheckCooldown();
    void SendResult(int defenderNum);

    DWORD m_lastHitTick[2];
    float m_minDist;
    DWORD m_cooldownMs;
    bool m_hasLastHit[2]{};

    HitReportBody m_report{};
    PlayerState m_playerStates[2]{};
    HitResultBody m_result{};

    int m_senderNum{ -1 };
    DWORD m_now{};
    bool m_valid{ false };

    bool m_ready{ false };
};
