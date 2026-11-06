#include "game_server.h"
#include <windows.h>
#include <cstdlib>

int main()
{
    SetConsoleOutputCP(CP_UTF8);

    GameServer server;

    if (!server.Init(9000)) {
        server.Shutdown();
        return 1;
    }

    server.Run();
    server.Shutdown();
    return 0;
}
