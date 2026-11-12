#include "hit_judge.h"
#include <cstdio>

void HitJudge::HandleReport(int attackerNum, int defenderNum) {
    printf("[HitJudge] HandleReport 호출\n");
}

void HitJudge::Verify() {
    printf("[HitJudge] Verify 호출\n");
}

void HitJudge::CheckDistance() {
    printf("[HitJudge] CheckDistance 호출\n");
}

void HitJudge::CheckCooldown() {
    printf("[HitJudge] CheckCooldown 호출\n");
}

void HitJudge::SendResult(int defenderNum) {
    printf("[HitJudge] SendResult 호출\n");
}
