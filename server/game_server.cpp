#include "game_server.h"
#include "client_session.h"
#include <cstdio>
#include <cstring>

#pragma comment(lib, "ws2_32.lib")

static DWORD WINAPI AcceptThreadProc(LPVOID param) {
    GameServer* srv = static_cast<GameServer*>(param);
    srv->AcceptLoop();
    return 0;
}

DWORD WINAPI GameServer::UdpThreadProc(LPVOID param) {
    GameServer* srv = static_cast<GameServer*>(param);
    srv->UdpRecvLoop();
    return 0;
}

DWORD WINAPI GameServer::TickSendThreadProc(LPVOID param) {
    GameServer* srv = static_cast<GameServer*>(param);
    srv->TickSendLoop();
    return 0;
}

GameServer::GameServer()
    : m_listenSock(INVALID_SOCKET)
    , m_udpSock(INVALID_SOCKET)
    , m_port(0)
    , m_stopFlag(false)
{
}

bool GameServer::Init(unsigned short port)
{
    m_port = port;

    WSADATA wsa;
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) {
        printf("[Init] WSAStartup 실패: %d\n", WSAGetLastError());
        return false;
    }

    // TCP 소켓
    m_listenSock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (m_listenSock == INVALID_SOCKET) {
        printf("[Init] TCP socket 생성 실패: %d\n", WSAGetLastError());
        WSACleanup();
        return false;
    }

    int opt = 1;
    setsockopt(m_listenSock, SOL_SOCKET, SO_REUSEADDR,
               reinterpret_cast<const char*>(&opt), sizeof(opt));

    sockaddr_in addr{};
    addr.sin_family      = AF_INET;
    addr.sin_port        = htons(m_port);
    addr.sin_addr.s_addr = INADDR_ANY;

    if (bind(m_listenSock, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) == SOCKET_ERROR) {
        printf("[Init] TCP bind 실패 (포트 %u): %d\n", m_port, WSAGetLastError());
        closesocket(m_listenSock); m_listenSock = INVALID_SOCKET;
        WSACleanup(); return false;
    }
    if (listen(m_listenSock, SOMAXCONN) == SOCKET_ERROR) {
        printf("[Init] listen 실패: %d\n", WSAGetLastError());
        closesocket(m_listenSock); m_listenSock = INVALID_SOCKET;
        WSACleanup(); return false;
    }

    // UDP 소켓
    m_udpSock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (m_udpSock == INVALID_SOCKET) {
        printf("[Init] UDP socket 생성 실패: %d\n", WSAGetLastError());
        closesocket(m_listenSock); m_listenSock = INVALID_SOCKET;
        WSACleanup(); return false;
    }
    if (bind(m_udpSock, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) == SOCKET_ERROR) {
        printf("[Init] UDP bind 실패 (포트 %u): %d\n", m_port, WSAGetLastError());
        closesocket(m_udpSock); m_udpSock = INVALID_SOCKET;
        closesocket(m_listenSock); m_listenSock = INVALID_SOCKET;
        WSACleanup(); return false;
    }

    m_sessionMgr.Init();
    g_sessionMgr = &m_sessionMgr;
    printf("[Init] 서버 준비 완료 — TCP/UDP 포트 %u\n", m_port);
    return true;
}

void GameServer::Run()
{
    HANDLE hAccept = CreateThread(nullptr, 0, AcceptThreadProc, this, 0, nullptr);
    if (!hAccept) {
        printf("[Run] AcceptThread 생성 실패: %d\n", GetLastError());
        return;
    }
    HANDLE hUdp = CreateThread(nullptr, 0, UdpThreadProc, this, 0, nullptr);
    if (!hUdp) {
        printf("[Run] UdpThread 생성 실패: %d\n", GetLastError());
        m_stopFlag = true;
        Shutdown();
        WaitForSingleObject(hAccept, 3000);
        CloseHandle(hAccept);
        return;
    }
    HANDLE hTickSend = CreateThread(nullptr, 0, TickSendThreadProc, this, 0, nullptr);
    if (!hTickSend) {
        printf("[Run] TickSendThread 생성 실패: %d\n", GetLastError());
        m_stopFlag = true;
        Shutdown();
        WaitForSingleObject(hAccept, 3000);
        WaitForSingleObject(hUdp, 3000);
        CloseHandle(hAccept);
        CloseHandle(hUdp);
        return;
    }
    printf("서버 실행 중. 종료하려면 Enter 를 누르세요...\n");
    getchar();
    m_stopFlag = true;
    Shutdown();
    WaitForSingleObject(hAccept, 3000);
    WaitForSingleObject(hUdp, 3000);
    WaitForSingleObject(hTickSend, 3000);
    CloseHandle(hAccept);
    CloseHandle(hUdp);
    CloseHandle(hTickSend);
}

void GameServer::AcceptLoop()
{
    printf("[AcceptLoop] 대기 시작\n");
    while (!m_stopFlag) {
        sockaddr_in clientAddr{};
        int addrLen = sizeof(clientAddr);
        SOCKET clientSock = accept(m_listenSock, reinterpret_cast<sockaddr*>(&clientAddr), &addrLen);
        if (clientSock == INVALID_SOCKET) {
            if (m_stopFlag) break;
            printf("[AcceptLoop] accept 오류: %d\n", WSAGetLastError());
            continue;
        }

        ClientSession* session = new ClientSession(clientSock, clientAddr, -1, &m_sessionMgr);
        int slot = m_sessionMgr.Add(session);
        if (slot < 0) {
            printf("[AcceptLoop] 접속자 초과 — 연결 거부\n");
            session->Close();
            delete session;
            continue;
        }
        session->SetPlayerNum(slot);
        printf("[AcceptLoop] Player %d 접속\n", slot);
        m_sessionMgr.SendAssign(slot);

        HANDLE hRecv = CreateThread(nullptr, 0, ClientSession::RecvThreadProc, session, 0, nullptr);
        if (!hRecv) {
            printf("[AcceptLoop] RecvThread 생성 실패: %d\n", GetLastError());
            m_sessionMgr.Remove(slot);
            session->Close();
            delete session;
            continue;
        }
        CloseHandle(hRecv);
    }
    printf("[AcceptLoop] 종료\n");
}

void GameServer::TickSendLoop()
{
    while (!m_stopFlag) {
        Sleep(50);
        m_sessionMgr.BroadcastTick(m_udpSock);
    }
    printf("[TickSendLoop] 종료\n");
}

void GameServer::UdpRecvLoop()
{
    char buf[1024];
    sockaddr_in from{};
    int fromLen = sizeof(from);
    while (!m_stopFlag) {
        fromLen = sizeof(from);
        int received = recvfrom(m_udpSock, buf, sizeof(buf), 0,
                                reinterpret_cast<sockaddr*>(&from), &fromLen);
        if (received == SOCKET_ERROR) {
            if (m_stopFlag) break;
            printf("[UdpRecvLoop] recvfrom 오류: %d\n", WSAGetLastError());
            continue;
        }
        if (received < (int)sizeof(PacketHeader)) continue;
        PacketHeader hdr;
        memcpy(&hdr, buf, sizeof(PacketHeader));
        uint16_t size = ntohs(hdr.size);
        uint8_t  type = hdr.type;
        if (type != PKT_TICK_C2S) continue;
        if (size != (uint16_t)sizeof(TickC2SBody)) continue;
        if (received < (int)(sizeof(PacketHeader) + size)) continue;
        TickC2SBody body;
        memcpy(&body, buf + sizeof(PacketHeader), sizeof(TickC2SBody));
        body.Ntoh();
        int playerNum = static_cast<int>(body.player);
        if (playerNum < 0 || playerNum >= 2) continue;
        m_sessionMgr.OnTickReceived(playerNum, body, from);
    }
    printf("[UdpRecvLoop] 종료\n");
}

void GameServer::Shutdown()
{
    printf("[Shutdown] 서버 종료 중...\n");
    g_sessionMgr = nullptr;
    m_sessionMgr.Destroy();
    if (m_listenSock != INVALID_SOCKET) {
        closesocket(m_listenSock);
        m_listenSock = INVALID_SOCKET;
    }
    if (m_udpSock != INVALID_SOCKET) {
        closesocket(m_udpSock);
        m_udpSock = INVALID_SOCKET;
    }
    WSACleanup();
    printf("[Shutdown] 완료\n");
}
