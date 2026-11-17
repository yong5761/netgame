#pragma once
#define WIN32_LEAN_AND_MEAN
#define MAX_X_DISTANCE      350.f
#define MIN_COOLDOWN_MS     100
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
    float m_minDist{MAX_X_DISTANCE};
    DWORD m_cooldownMs{MIN_COOLDOWN_MS};
    bool m_hasLastHit[2]{};

    HitReportBody m_report{};
    PlayerState m_playerStates[2]{};
    HitResultBody m_result{};

    int m_senderNum{ -1 };
    DWORD m_now{};
    bool m_valid{ false };

    bool m_ready{ false };
};
