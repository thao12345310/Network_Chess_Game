#ifndef NETWORK_INTERFACE_H
#define NETWORK_INTERFACE_H

#include <memory>
#include <string>
#include <map>
#include <vector>
#include <mutex>
#include <algorithm>

#include "StreamServer.h"

class NetworkInterface {
public:
    NetworkInterface(int port);
    ~NetworkInterface();
    void start();

private:
    int port;
    std::unique_ptr<StreamServer> streamServer;

    std::string process_request(SOCKET clientSocket, const std::string& request);
    void handle_disconnect(SOCKET clientSocket);
    
    // In-memory session tracking
    std::mutex session_mutex;
    std::map<SOCKET, int> client_sessions; // Socket -> PlayerID
    std::vector<int> ready_players; // Just IDs for now
};

#endif // NETWORK_INTERFACE_H
