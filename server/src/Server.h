#ifndef SERVER_H
#define SERVER_H

#include <vector>
#include <memory>
#include <mutex>
#include <atomic>
#include "MatchmakingService.h"
#include "MessageHandler.h"

// Forward declaration
class ClientSession;

class Server {
public:
    Server(int port = 5001);
    ~Server();

    void run();
    void stop();

    // Interface for Session to call back (e.g., on close)
    void onClientDisconnected(std::shared_ptr<ClientSession> session);
    
    // Send to specific client (thread safe helpers if needed)
    // But ClientSession has send(), so maybe not needed here directly.

private:
    int serverSocket_;
    int port_;
    std::atomic<bool> running_;

    MatchmakingService matchmakingService_;
    MessageHandler messageHandler_;

    std::vector<std::shared_ptr<ClientSession>> sessions_;
    std::mutex sessionsMutex_;

    void setupServerSocket();
    void handleNewConnection();
    void handleClientData(std::shared_ptr<ClientSession> session);
};

#endif // SERVER_H
