#pragma once
#define WIN32_LEAN_AND_MEAN
#include <winsock2.h>
#include <cstdint>
#include "client_session.h"
#include "packet.h"

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
    void OnTickReceived(int playerNum, const TickC2SBody& body, const sockaddr_in& from);

private:
    ClientSession*   m_sessions[2];
    CRITICAL_SECTION m_sessionLock;
    bool             m_initialized  = false;
    bool             m_matchStarted = false;

    PlayerState      m_latest[2];
    uint16_t         m_lastSeq[2];
    bool             m_seqInitialized[2];
    CRITICAL_SECTION m_stateLock;
};
