#pragma once
#define WIN32_LEAN_AND_MEAN
#include <winsock2.h>
#include <cstdint>

// ── 1. 패킷 종류 ─────────────────────────────────────────────
// TCP 1번대, UDP 20번대 — 번호는 프로토콜 규격
enum PacketType {
    PKT_JOIN        = 1,
    PKT_ASSIGN      = 2,
    PKT_SELECT      = 3,
    PKT_MATCH_START = 4,
    PKT_ROUND_START = 5,
    PKT_HIT_REPORT  = 6,
    PKT_HIT_RESULT  = 7,
    PKT_ROUND_END   = 8,
    PKT_LEAVE       = 9,
    PKT_TICK_C2S    = 20, // UDP
    PKT_TICK_S2C    = 21, // UDP
};

// ── 2. 동작 번호 ─────────────────────────────────────────────
enum ActionId {
    IDLE          = 0,
    WALK          = 1,
    JUMP          = 2,
    MOVE_JUMP     = 3,
    RUN           = 4,
    RUN_JUMP      = 5,
    BACK_DASH     = 6,
    SIT_DOWN      = 7,
    SIT_UP        = 8,
    NORMAL_ATTACK = 9,
    AIR_ATTACK    = 10,
    SIT_ATTACK    = 11,
    GUARD         = 12,
    GET_HIT       = 13,
    COMBO_ATTACK  = 14,
    DEAD          = 15,
};

// ── 3. 비트마스크 ────────────────────────────────────────────
// 키 입력 — 한 바이트에 복수 키 동시 표현
enum KeyMask {
    LEFT  = 0x01,
    RIGHT = 0x02,
    UP    = 0x04,
    DOWN  = 0x08,
    LP    = 0x10,
    RP    = 0x20,
    RK    = 0x40,
    LK    = 0x80,
};

// 캐릭터 상태 플래그
enum StateFlag {
    ATTACKING  = 0x01,
    GUARDING   = 0x02,
    HITTED     = 0x04,
    DAMAGEABLE = 0x08,
};

// ── 4. 공통 머리 (3바이트) ───────────────────────────────────
#pragma pack(1)
struct PacketHeader {
    uint16_t size; // 본문 바이트 수 (머리 제외)
    uint8_t  type; // PacketType 값
};
#pragma pack()
