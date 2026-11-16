#pragma once
#define WIN32_LEAN_AND_MEAN
#include <winsock2.h>

class SessionManager; // RecvLoop 에서 Remove 호출

class ClientSession {
public:
    ClientSession(SOCKET sock, sockaddr_in addr, int playerNum, SessionManager* mgr);

    void RecvLoop();
    void Send(const char* buf, int len);
    void Close();

    void   SetPlayerNum(int num) { m_playerNum = num; }
    int    GetPlayerNum() const  { return m_playerNum; }
    SOCKET GetSock()      const  { return m_sock; }
    bool   IsAlive()      const  { return m_alive; }
    int    GetCharNum()   const  { return m_charNum; }

    void        SetUdpAddr(const sockaddr_in& addr) { m_udpAddr = addr; m_udpAddrKnown = true; }
    sockaddr_in GetUdpAddr()  const { return m_udpAddr; }
    bool        HasUdpAddr()  const { return m_udpAddrKnown; }

    static DWORD WINAPI RecvThreadProc(LPVOID param);

private:
    SOCKET          m_sock;
    sockaddr_in     m_addr;
    int             m_playerNum;
    bool            m_alive;
    int             m_charNum;
    sockaddr_in     m_udpAddr;
    bool            m_udpAddrKnown;
    SessionManager* m_mgr;
};
