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
    std::vector<int> ready_players; // Players in lobby
    
    // Matchmaking queue entry with player_id and selected game mode
    struct MatchmakingEntry {
        int player_id;
        std::string mode; // BLITZ, RAPID, CLASSICAL
    };
    std::vector<MatchmakingEntry> matchmaking_queue; // Players waiting for random match

    // Helper for executing Python logic
    std::string execute_logic_command(const std::string& json_input);

};

#endif // NETWORK_INTERFACE_H
