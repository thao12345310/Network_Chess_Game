#include "NetworkInterface.h"
#include <iostream>
#include <functional>
#include <cstdlib>
#include <vector>
#include <algorithm>

NetworkInterface::NetworkInterface(int port) : port(port) {
    streamServer = std::make_unique<StreamServer>(
        port, [this](SOCKET clientSocket, const std::string &request) { return process_request(clientSocket, request); });
    
    streamServer->setOnConnectionClosed([this](SOCKET clientSocket) {
        handle_disconnect(clientSocket);
    });
}

NetworkInterface::~NetworkInterface() = default;

void NetworkInterface::start() {
    if (!streamServer) {
        std::cerr << "Stream server is not initialized" << std::endl;
        return;
    }

    streamServer->start();
}

void NetworkInterface::handle_disconnect(SOCKET clientSocket) {
    std::lock_guard<std::mutex> lock(session_mutex);
    auto it = client_sessions.find(clientSocket);
    if (it != client_sessions.end()) {
        int player_id = it->second;
        std::cout << "Client disconnected: Socket " << clientSocket << " (Player " << player_id << ")" << std::endl;
        
        // Remove from session map
        client_sessions.erase(it);
        
        // Remove from ready players (Network logic)
        auto rit = std::remove(ready_players.begin(), ready_players.end(), player_id);
        if (rit != ready_players.end()) {
            ready_players.erase(rit, ready_players.end());
            // Optionally: call python to sync DB
             std::string command = "python3 logic_wrapper.py \"{\\\"action\\\": \\\"leave_lobby\\\", \\\"player_id\\\": " + std::to_string(player_id) + "}\"";
             #ifdef _WIN32
             command = "python logic_wrapper.py \"{\\\"action\\\": \\\"leave_lobby\\\", \\\"player_id\\\": " + std::to_string(player_id) + "}\"";
             #endif
             system(command.c_str());
        }
    } else {
        // Unidentified client disconnected
    }
}

std::string NetworkInterface::process_request(SOCKET clientSocket, const std::string& request) {
    std::cout << "Received: " << request << std::endl;

    std::string escaped_request;
    for (char c : request) {
        if (c == '"') {
            escaped_request += "\\\"";
        } else {
            escaped_request += c;
        }
    }

    std::string command = "python3 logic_wrapper.py \"" + escaped_request + "\"";
#ifdef _WIN32
    command = "python logic_wrapper.py \"" + escaped_request + "\"";
#endif
    
    std::string result = "";
    FILE* pipe = nullptr;

#ifdef _WIN32
    pipe = _popen(command.c_str(), "r");
#else
    pipe = popen(command.c_str(), "r");
#endif

    if (!pipe) {
        return "{\"status\": \"error\", \"message\": \"Failed to open pipe\"}";
    }

    char buffer[128];
    while (fgets(buffer, 128, pipe) != NULL) {
        result += buffer;
    }

#ifdef _WIN32
    _pclose(pipe);
#else
    pclose(pipe);
#endif
    
    size_t first = result.find_first_not_of(" \t\n\r");
    if (first == std::string::npos) {
        result = "";
    } else {
        size_t last = result.find_last_not_of(" \t\n\r");
        result = result.substr(first, (last - first + 1));
    }

    // Network Logic: Intercept successful Lobby actions to update session map
    if (result.find("\"status\": \"success\"") != std::string::npos) {
        if (request.find("\"action\": \"join_lobby\"") != std::string::npos || 
            request.find("\"action\":\"join_lobby\"") != std::string::npos) {
            
            // Extract player_id (Simple parsing)
            std::string key = "\"player_id\":";
            size_t pos = request.find(key);
            if (pos != std::string::npos) {
                int pid = std::atoi(request.c_str() + pos + key.length());
                if (pid > 0) {
                    std::lock_guard<std::mutex> lock(session_mutex);
                    client_sessions[clientSocket] = pid;
                    
                    if (std::find(ready_players.begin(), ready_players.end(), pid) == ready_players.end()) {
                        ready_players.push_back(pid);
                    }
                }
            }
        }
        else if (request.find("\"action\": \"leave_lobby\"") != std::string::npos ||
                 request.find("\"action\":\"leave_lobby\"") != std::string::npos) {
            // Extract player_id
            std::string key = "\"player_id\":";
            size_t pos = request.find(key);
            if (pos != std::string::npos) {
                 int pid = std::atoi(request.c_str() + pos + key.length());
                 if (pid > 0) {
                     std::lock_guard<std::mutex> lock(session_mutex);
                     // Note: We don't remove from client_sessions because they are still connected, just not in lobby
                     auto it = std::remove(ready_players.begin(), ready_players.end(), pid);
                     ready_players.erase(it, ready_players.end());
                 }
            }
        }
    }

    if (result.empty()) {
        return "{\"status\": \"error\", \"message\": \"Empty response from logic\"}";
    }

    return result;
}
