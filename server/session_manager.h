#pragma once
#define WIN32_LEAN_AND_MEAN
#include <winsock2.h>
#include <cstdint>
#include "client_session.h"
#include "packet.h"
#include "hit_judge.h"

class SessionManager {
public:
    static const uint8_t  MAX_HP     = 100;
    static const int16_t  KNOCK_GUARD = 12;
    static const int16_t  KNOCK_HIT   = 40;
    void Init();
    void Destroy();

    int  Add(ClientSession* session);
    void Remove(int playerNum);
    void SendTo(int playerNum, const char* buf, int len);
    void SendToAll(const char* buf, int len);
    void SendAssign(int playerNum);
    void OnCharSelected(int playerNum, uint8_t charNum);
    void OnTickReceived(int playerNum, const TickC2SBody& body, const sockaddr_in& from);
    void BroadcastTick(SOCKET udpSock);
    void OnHitReport(int senderNum, const HitReportBody& report);
    bool GetPendingReport(HitReportBody& out);
    bool GetPendingState(int playerNum, PlayerState& out);
    int  GetPendingSender();
    void SendHitResult(int playerNum, const HitResultBody& body);
    void OnHitVerified(int attackerNum, int defenderNum,
                       uint8_t damage, bool guarded);

private:
    ClientSession*   m_sessions[2];
    CRITICAL_SECTION m_sessionLock;
    bool             m_initialized  = false;
    bool             m_matchStarted = false;

    PlayerState      m_latest[2];
    uint16_t         m_lastSeq[2];
    bool             m_seqInitialized[2];
    CRITICAL_SECTION m_stateLock;

    uint16_t         m_sendSeq;
    bool             m_sendStarted;
    uint8_t          m_hp[2];

    HitJudge         m_judge;
    HitReportBody    m_pendingReport;
    PlayerState      m_pendingStates[2];
    int              m_pendingSender;
    bool             m_hitReportLogged;
};

extern SessionManager* g_sessionMgr;
