#pragma once
#define WIN32_LEAN_AND_MEAN
#include <winsock2.h>

class GameServer {
public:
    GameServer();

    bool Init(unsigned short port);
    void Run();
    void AcceptLoop();
    void UdpRecvLoop();
    void Shutdown();

private:
    SOCKET        m_listenSock;
    SOCKET        m_udpSock;
    unsigned short m_port;
};
