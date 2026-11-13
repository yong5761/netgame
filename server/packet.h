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
// ── 5. 본문 구조체 ───────────────────────────────────────────
// PKT_JOIN  : 본문 0바이트 — 구조체 없음
// PKT_LEAVE : 본문 0바이트 — 구조체 없음

struct AssignBody {
    uint8_t player;   // 플레이어 번호
    void Hton() {}
    void Ntoh() {}
};

struct SelectBody {
    uint8_t charNum;  // 선택 캐릭터 번호
    void Hton() {}
    void Ntoh() {}
};

struct MatchStartBody {
    uint8_t charNum[2]; // 양 플레이어 캐릭터 번호
    void Hton() {}
    void Ntoh() {}
};

struct RoundStartBody {
    int16_t startX[2]; // 초기 X 좌표
    uint8_t hp[2];     // 초기 HP
    uint8_t round;     // 라운드 번호
    void Hton() {
        startX[0] = (int16_t)htons((uint16_t)startX[0]);
        startX[1] = (int16_t)htons((uint16_t)startX[1]);
    }
    void Ntoh() {
        startX[0] = (int16_t)ntohs((uint16_t)startX[0]);
        startX[1] = (int16_t)ntohs((uint16_t)startX[1]);
    }
};

struct HitReportBody {
    uint8_t victim;   // 맞은 플레이어
    uint8_t attacker; // 때린 플레이어
    uint8_t damage;   // 데미지
    uint8_t guard;    // 가드 여부
    void Hton() {}
    void Ntoh() {}
};

struct HitResultBody {
    uint8_t victim;   // 맞은 플레이어
    uint8_t attacker; // 때린 플레이어
    uint8_t damage;   // 확정 데미지
    uint8_t hp;       // 맞은 쪽 남은 HP
    int16_t knockX;   // 넉백 X
    void Hton() {
        knockX = (int16_t)htons((uint16_t)knockX);
    }
    void Ntoh() {
        knockX = (int16_t)ntohs((uint16_t)knockX);
    }
};

struct RoundEndBody {
    uint8_t winner;      // 승자 플레이어 번호
    uint8_t winCount[2]; // 각 플레이어 누적 승수
    uint8_t matchOver;   // 매치 종료 여부
    void Hton() {}
    void Ntoh() {}
};

struct TickC2SBody {
    uint16_t seq;    // 시퀀스 번호
    uint8_t  player; // 플레이어 번호
    uint8_t  keys;   // KeyMask 비트 조합
    int16_t  x;      // X 좌표
    int16_t  y;      // Y 좌표
    int8_t   face;   // 방향
    uint8_t  state;  // ActionId 값
    uint8_t  frame;  // 프레임 번호
    uint8_t  flag;   // StateFlag 비트 조합
    void Hton() {
        seq = htons(seq);
        x   = (int16_t)htons((uint16_t)x);
        y   = (int16_t)htons((uint16_t)y);
    }
    void Ntoh() {
        seq = ntohs(seq);
        x   = (int16_t)ntohs((uint16_t)x);
        y   = (int16_t)ntohs((uint16_t)y);
    }
};

struct PlayerState {        // TickS2CBody 에서만 사용
    int16_t x;      // X 좌표
    int16_t y;      // Y 좌표
    int8_t  face;   // 방향
    uint8_t state;  // ActionId 값
    uint8_t frame;  // 프레임 번호
    uint8_t flag;   // StateFlag 비트 조합
    void Hton() {
        x = (int16_t)htons((uint16_t)x);
        y = (int16_t)htons((uint16_t)y);
    }
    void Ntoh() {
        x = (int16_t)ntohs((uint16_t)x);
        y = (int16_t)ntohs((uint16_t)y);
    }
};

struct TickS2CBody {
    uint16_t    seq;      // 시퀀스 번호
    PlayerState p[2];     // 양 플레이어 상태
    uint8_t     hp[2];    // 양 플레이어 HP
    uint16_t    timeLeft; // 남은 시간
    void Hton() {
        seq = htons(seq);
        p[0].Hton();
        p[1].Hton();
        timeLeft = htons(timeLeft);
    }
    void Ntoh() {
        seq = ntohs(seq);
        p[0].Ntoh();
        p[1].Ntoh();
        timeLeft = ntohs(timeLeft);
    }
};

#pragma pack()

// ── 6. 크기 검증 ─────────────────────────────────────────────
static_assert(sizeof(PacketHeader)   == 3,  "PacketHeader size mismatch");
static_assert(sizeof(AssignBody)     == 1,  "AssignBody size mismatch");
static_assert(sizeof(SelectBody)     == 1,  "SelectBody size mismatch");
static_assert(sizeof(MatchStartBody) == 2,  "MatchStartBody size mismatch");
static_assert(sizeof(RoundStartBody) == 7,  "RoundStartBody size mismatch");
static_assert(sizeof(HitReportBody)  == 4,  "HitReportBody size mismatch");
static_assert(sizeof(HitResultBody)  == 6,  "HitResultBody size mismatch");
static_assert(sizeof(RoundEndBody)   == 4,  "RoundEndBody size mismatch");
static_assert(sizeof(TickC2SBody)    == 12, "TickC2SBody size mismatch");
static_assert(sizeof(PlayerState)    == 8,  "PlayerState size mismatch");
static_assert(sizeof(TickS2CBody)    == 22, "TickS2CBody size mismatch");
