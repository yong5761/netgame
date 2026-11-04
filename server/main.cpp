#include "game_server.h"
#include <cstdlib>

int main()
{
    GameServer server;

    if (!server.Init(9000)) {
        server.Shutdown();
        return 1;
    }

    server.Run();
    server.Shutdown();
    return 0;
}
