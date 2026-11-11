#include "client_session.h"
#include <cstdio>
#include <cstring>
#include "session_manager.h"
#include "packet.h"
#include <cstdint>

ClientSession::ClientSession(SOCKET sock, sockaddr_in addr, int playerNum, SessionManager* mgr)
    : m_sock(sock), m_addr(addr), m_playerNum(playerNum), m_alive(true), m_charNum(-1), m_mgr(mgr)
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
    char recvBuf[1024];
    char accumBuf[4096];
    int  accumLen = 0;

    while (m_alive) {
        int received = recv(m_sock, recvBuf, sizeof(recvBuf), 0);
        if (received == 0) {
            printf("[Session %d] 클라이언트 정상 종료\n", m_playerNum);
            break;
        }
        if (received == SOCKET_ERROR) {
            printf("[Session %d] recv 오류: %d\n", m_playerNum, WSAGetLastError());
            break;
        }
        if (accumLen + received > (int)sizeof(accumBuf)) {
            printf("[Session %d] 버퍼 초과, 연결 종료\n", m_playerNum);
            break;
        }

        // 누적 버퍼에 추가
        memcpy(accumBuf + accumLen, recvBuf, received);
        accumLen += received;

        // 완성된 패킷을 버퍼 앞에서 반복 추출
        while (true) {
            if (accumLen < 3) break;                              // 1. 헤더 미만

            uint16_t bodySize;
            memcpy(&bodySize, accumBuf, 2);
            bodySize        = ntohs(bodySize);                    // 2. 헤더 파싱
            uint8_t pktType = static_cast<uint8_t>(accumBuf[2]);

            int pktTotal = 3 + static_cast<int>(bodySize);
            if (accumLen < pktTotal) break;                       // 3. 본문 미만

            if (pktType == static_cast<uint8_t>(PKT_SELECT)) {    // 4. 종류별 처리
                if (bodySize >= 1) {
                    uint8_t charNum = static_cast<uint8_t>(accumBuf[3]);
                    if (charNum > 2) {
                        printf("[Session %d] PKT_SELECT charNum=%u 범위 초과, 무시\n",
                               m_playerNum, charNum);
                    } else {
                        m_charNum = static_cast<int>(charNum);
                        printf("[Session %d] PKT_SELECT charNum=%u\n", m_playerNum, charNum);
                        m_mgr->OnCharSelected(m_playerNum, charNum);
                    }
                }
            } else {
                printf("[Session %d] pkt type=%u body=%u bytes\n",
                       m_playerNum, pktType, bodySize);
            }

            memmove(accumBuf, accumBuf + pktTotal, accumLen - pktTotal);
            accumLen -= pktTotal;                                  // 5. 버퍼 앞부분 제거
        }
    }

    m_alive = false;
    m_mgr->Remove(m_playerNum); // 세션 목록에서 자신을 제거하고 스레드 종료
}

// 스레드 프로시저. RecvLoop 반환 후 session 메모리를 소유해 해제
DWORD WINAPI ClientSession::RecvThreadProc(LPVOID param) {
    ClientSession* session = static_cast<ClientSession*>(param);
    session->RecvLoop();
    delete session;
    return 0;
}
