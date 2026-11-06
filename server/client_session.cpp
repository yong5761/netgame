#include "client_session.h"
#include <cstdio>
#include <cstring>

ClientSession::ClientSession(SOCKET sock, sockaddr_in addr, int playerNum, SessionManager* mgr)
    : m_sock(sock), m_addr(addr), m_playerNum(playerNum), m_alive(true), m_mgr(mgr)
{
}

void ClientSession::Send(const char* buf, int len) {
    if (!m_alive || m_sock == INVALID_SOCKET) return;
    int sent = 0;
    while (sent < len) {
        int result = send(m_sock, buf + sent, len - sent, 0);
        if (result <= 0) {
            m_alive = false;
            break;
        }
        sent += result;
    }
}

void ClientSession::Close() {
    if (m_sock != INVALID_SOCKET) {
        closesocket(m_sock);
        m_sock = INVALID_SOCKET;
    }
    m_alive = false;
}

void ClientSession::RecvLoop() {
    // TODO: 메시지 경계 처리 — 2차 커밋에서 구현
}

// 스레드 프로시저. RecvLoop 반환 후 session 메모리를 소유해 해제
DWORD WINAPI ClientSession::RecvThreadProc(LPVOID param) {
    ClientSession* session = static_cast<ClientSession*>(param);
    session->RecvLoop();
    delete session;
    return 0;
}
