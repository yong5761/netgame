#pragma once
#define WIN32_LEAN_AND_MEAN
#include <winsock2.h>
#include <cstdint>

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
};
