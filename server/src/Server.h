#ifndef SERVER_H
#define SERVER_H

#include <memory>
#include "game_logic/NetworkInterface.h"

class Server {
public:
    Server(int port = 5001);
    ~Server();

    void run();

private:
    std::unique_ptr<NetworkInterface> networkInterface;
};

#endif // SERVER_H
