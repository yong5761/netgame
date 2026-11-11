#include "session_manager.h"
#include "packet.h"
#include <cstdio>
#include <cstring>

static void BuildAndSend(SOCKET sock, uint8_t pktType, const void* body, uint16_t bodyLen) {
    char buf[256];
    uint16_t netSize = htons(bodyLen);
    memcpy(buf, &netSize, 2);
    buf[2] = static_cast<char>(pktType);
    if (body && bodyLen > 0)
        memcpy(buf + 3, body, bodyLen);
    if (send(sock, buf, 3 + static_cast<int>(bodyLen), 0) == SOCKET_ERROR)
        printf("[BuildAndSend] type=%u send 실패: %d\n",
               static_cast<unsigned>(pktType), WSAGetLastError());
}

void SessionManager::Init() {
    m_sessions[0]  = nullptr;
    m_sessions[1]  = nullptr;
    m_matchStarted = false;
    InitializeCriticalSection(&m_sessionLock);
    m_initialized = true;
}

void SessionManager::Destroy() {
    if (!m_initialized) return;

    // 모든 세션 소켓을 닫아 recv 스레드를 깨운다
    EnterCriticalSection(&m_sessionLock);
    for (int i = 0; i < 2; i++) {
        if (m_sessions[i]) {
            m_sessions[i]->Close();
            m_sessions[i] = nullptr;
        }
    }
    LeaveCriticalSection(&m_sessionLock);

    Sleep(200); // recv 스레드 정리 대기
    DeleteCriticalSection(&m_sessionLock);
    m_initialized = false;
}

int SessionManager::Add(ClientSession* session) {
    EnterCriticalSection(&m_sessionLock);
    int slot = -1;
    for (int i = 0; i < 2; i++) {
        if (!m_sessions[i]) {
            m_sessions[i] = session;
            slot = i;
            break;
        }
    }
    LeaveCriticalSection(&m_sessionLock);
    return slot;
}

void SessionManager::Remove(int playerNum) {
    if (playerNum < 0 || playerNum >= 2) return;
    EnterCriticalSection(&m_sessionLock);
    m_sessions[playerNum] = nullptr; // 메모리 해제는 RecvThreadProc 에서
    LeaveCriticalSection(&m_sessionLock);
    printf("[SessionManager] Player %d 접속 종료\n", playerNum);
}

void SessionManager::SendAssign(int playerNum) {
    SOCKET sock = INVALID_SOCKET;
    EnterCriticalSection(&m_sessionLock);
    if (m_sessions[playerNum] && m_sessions[playerNum]->IsAlive())
        sock = m_sessions[playerNum]->GetSock();
    LeaveCriticalSection(&m_sessionLock);

    if (sock != INVALID_SOCKET) {
        AssignBody body;
        body.player = static_cast<uint8_t>(playerNum);
        BuildAndSend(sock, PKT_ASSIGN, &body, static_cast<uint16_t>(sizeof(body)));
        printf("[Assign] Player %d 번호 통보\n", playerNum);
    }
}

void SessionManager::OnCharSelected(int playerNum, uint8_t charNum) {
    printf("[SessionManager] Player %d 캐릭터 %u 선택 완료\n", playerNum, charNum);

    SOCKET      socks[2]  = { INVALID_SOCKET, INVALID_SOCKET };
    uint8_t     chars[2]  = { 0, 0 };
    bool        doSend    = false;

    EnterCriticalSection(&m_sessionLock);
    if (!m_matchStarted) {
        bool bothReady = true;
        for (int i = 0; i < 2; i++) {
            if (!m_sessions[i] || !m_sessions[i]->IsAlive() || m_sessions[i]->GetCharNum() < 0) {
                bothReady = false;
                break;
            }
            socks[i] = m_sessions[i]->GetSock();
            chars[i] = static_cast<uint8_t>(m_sessions[i]->GetCharNum());
        }
        if (bothReady) {
            m_matchStarted = true;
            doSend = true;
        }
    }
    LeaveCriticalSection(&m_sessionLock);

    if (doSend) {
        MatchStartBody body;
        body.charNum[0] = chars[0];
        body.charNum[1] = chars[1];
        BuildAndSend(socks[0], PKT_MATCH_START, &body, static_cast<uint16_t>(sizeof(body)));
        BuildAndSend(socks[1], PKT_MATCH_START, &body, static_cast<uint16_t>(sizeof(body)));
        printf("[SessionManager] MATCH_START 전송 (1P=%u, 2P=%u)\n", chars[0], chars[1]);
    }
}

void SessionManager::SendTo(int playerNum, const char* buf, int len) {
    if (playerNum < 0 || playerNum >= 2) return;

    // 잠금 안에서 소켓 핸들만 복사
    SOCKET sock = INVALID_SOCKET;
    EnterCriticalSection(&m_sessionLock);
    if (m_sessions[playerNum] && m_sessions[playerNum]->IsAlive())
        sock = m_sessions[playerNum]->GetSock();
    LeaveCriticalSection(&m_sessionLock);

    // 잠금 밖에서 send
    if (sock != INVALID_SOCKET) {
        if (send(sock, buf, len, 0) == SOCKET_ERROR)
            printf("[SendTo] Player %d send 실패: %d\n", playerNum, WSAGetLastError());
    }
}

void SessionManager::SendToAll(const char* buf, int len) {
    // 잠금 안에서 소켓 핸들만 복사
    SOCKET socks[2] = { INVALID_SOCKET, INVALID_SOCKET };
    EnterCriticalSection(&m_sessionLock);
    for (int i = 0; i < 2; i++) {
        if (m_sessions[i] && m_sessions[i]->IsAlive())
            socks[i] = m_sessions[i]->GetSock();
    }
    LeaveCriticalSection(&m_sessionLock);

    // 잠금 밖에서 send
    for (int i = 0; i < 2; i++) {
        if (socks[i] != INVALID_SOCKET) {
            if (send(socks[i], buf, len, 0) == SOCKET_ERROR)
                printf("[SendToAll] Player %d send 실패: %d\n", i, WSAGetLastError());
        }
    }
}
