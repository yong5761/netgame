#include "game_server.h"
#include <cstdio>

#pragma comment(lib, "ws2_32.lib")

GameServer::GameServer()
    : m_listenSock(INVALID_SOCKET)
    , m_udpSock(INVALID_SOCKET)
    , m_port(0)
{
}

bool GameServer::Init(unsigned short port)
{
    m_port = port;

    // WSAStartup
    WSADATA wsa;
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) {
        printf("[Init] WSAStartup 실패: %d\n", WSAGetLastError());
        return false;
    }

    // TCP 소켓 생성
    m_listenSock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (m_listenSock == INVALID_SOCKET) {
        printf("[Init] TCP socket 생성 실패: %d\n", WSAGetLastError());
        WSACleanup();
        return false;
    }

    // SO_REUSEADDR 설정
    int opt = 1;
    if (setsockopt(m_listenSock, SOL_SOCKET, SO_REUSEADDR,
                   reinterpret_cast<const char*>(&opt), sizeof(opt)) == SOCKET_ERROR) {
        printf("[Init] setsockopt SO_REUSEADDR 실패: %d\n", WSAGetLastError());
        closesocket(m_listenSock);
        m_listenSock = INVALID_SOCKET;
        WSACleanup();
        return false;
    }

    // TCP bind
    sockaddr_in addr{};
    addr.sin_family      = AF_INET;
    addr.sin_port        = htons(m_port);
    addr.sin_addr.s_addr = INADDR_ANY;

    if (bind(m_listenSock, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) == SOCKET_ERROR) {
        printf("[Init] TCP bind 실패 (포트 %u): %d\n", m_port, WSAGetLastError());
        closesocket(m_listenSock);
        m_listenSock = INVALID_SOCKET;
        WSACleanup();
        return false;
    }

    // listen
    if (listen(m_listenSock, SOMAXCONN) == SOCKET_ERROR) {
        printf("[Init] listen 실패: %d\n", WSAGetLastError());
        closesocket(m_listenSock);
        m_listenSock = INVALID_SOCKET;
        WSACleanup();
        return false;
    }

    // UDP 소켓 생성
    m_udpSock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (m_udpSock == INVALID_SOCKET) {
        printf("[Init] UDP socket 생성 실패: %d\n", WSAGetLastError());
        closesocket(m_listenSock);
        m_listenSock = INVALID_SOCKET;
        WSACleanup();
        return false;
    }

    // UDP bind
    sockaddr_in udpAddr{};
    udpAddr.sin_family      = AF_INET;
    udpAddr.sin_port        = htons(m_port);
    udpAddr.sin_addr.s_addr = INADDR_ANY;

    if (bind(m_udpSock, reinterpret_cast<sockaddr*>(&udpAddr), sizeof(udpAddr)) == SOCKET_ERROR) {
        printf("[Init] UDP bind 실패 (포트 %u): %d\n", m_port, WSAGetLastError());
        closesocket(m_udpSock);
        m_udpSock = INVALID_SOCKET;
        closesocket(m_listenSock);
        m_listenSock = INVALID_SOCKET;
        WSACleanup();
        return false;
    }

    printf("[Init] 서버 준비 완료 — TCP/UDP 포트 %u\n", m_port);
    return true;
}
