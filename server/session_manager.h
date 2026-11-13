#pragma once
#define WIN32_LEAN_AND_MEAN
#include <winsock2.h>
#include <cstdint>
#include "client_session.h"

class SessionManager {
public:
    void Init();
    void Destroy();

    int  Add(ClientSession* session);
    void Remove(int playerNum);
    void SendTo(int playerNum, const char* buf, int len);
    void SendToAll(const char* buf, int len);
    void SendAssign(int playerNum);
    void OnCharSelected(int playerNum, uint8_t charNum);

private:
    ClientSession*   m_sessions[2];
    CRITICAL_SECTION m_sessionLock;
    bool             m_initialized  = false;
    bool             m_matchStarted = false;
};
