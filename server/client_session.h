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

    static DWORD WINAPI RecvThreadProc(LPVOID param);

private:
    SOCKET          m_sock;
    sockaddr_in     m_addr;
    int             m_playerNum;
    bool            m_alive;
    SessionManager* m_mgr;
};
