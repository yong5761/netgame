#include "session_manager.h"
#include <cstdio>

void SessionManager::Init() {
    m_sessions[0] = nullptr;
    m_sessions[1] = nullptr;
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
