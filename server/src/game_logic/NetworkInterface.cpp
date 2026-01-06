#include "NetworkInterface.h"
#include <iostream>
#include <functional>
#include <cstdlib>
#include <vector>
#include <algorithm>
#include <fstream>

static std::string get_python_cmd_prefix() {
    std::string script = "logic_wrapper.py";
    // Check if script exists in current directory
    {
        std::ifstream f(script);
        if (f.good()) {
             #ifdef _WIN32
             return "python " + script;
             #else
             return "python3 " + script;
             #endif
        }
    }
    // Check if script exists in game_logic/ subdirectory
    {
        std::string sub = "game_logic/logic_wrapper.py";
        std::ifstream f(sub);
        if (f.good()) {
             #ifdef _WIN32
             return "python " + sub;
             #else
             return "python3 " + sub;
             #endif
        }
    }
    // Check if script exists in src/game_logic/ subdirectory
    {
        std::string sub = "src/game_logic/logic_wrapper.py";
        std::ifstream f(sub);
        if (f.good()) {
             #ifdef _WIN32
             return "python " + sub;
             #else
             return "python3 " + sub;
             #endif
        }
    }
    
    // Default fallback
    #ifdef _WIN32
    return "python " + script;
    #else
    return "python3 " + script;
    #endif
}

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
             std::string cmd_prefix = get_python_cmd_prefix();
             std::string command = cmd_prefix + " \"{\\\"action\\\": \\\"leave_lobby\\\", \\\"player_id\\\": " + std::to_string(player_id) + "}\"";
             system(command.c_str());
        }
    } else {
        // Unidentified client disconnected
    }
}


static int get_json_int(const std::string& json, const std::string& key) {
    std::string key_str = "\"" + key + "\":";
    size_t pos = json.find(key_str);
    if (pos == std::string::npos) {
         key_str = "\"" + key + "\": "; 
         pos = json.find(key_str);
    }
    if (pos == std::string::npos) return 0;
    
    size_t val_start = pos + key_str.length();
    // Skip non-digits (like " or space)
    while (val_start < json.length() && (json[val_start] < '0' || json[val_start] > '9') && json[val_start] != '-') val_start++;
    
    return std::atoi(json.c_str() + val_start);
}

static std::string get_json_string(const std::string& json, const std::string& key) {
    std::string key_str = "\"" + key + "\":";
    size_t pos = json.find(key_str);
    if (pos == std::string::npos) {
         key_str = "\"" + key + "\": "; 
         pos = json.find(key_str);
    }
    if (pos == std::string::npos) return "";
    
    size_t val_start = pos + key_str.length();
    // find start quote
    size_t quote_start = json.find("\"", val_start);
    if (quote_start == std::string::npos) return "";

    size_t quote_end = json.find("\"", quote_start + 1);
    if (quote_end == std::string::npos) return "";

    return json.substr(quote_start + 1, quote_end - quote_start - 1);
}

std::string NetworkInterface::execute_logic_command(const std::string& request) {
    std::string escaped_request;
    for (char c : request) {
        if (c == '"') {
            escaped_request += "\\\"";
        } else {
            escaped_request += c;
        }
    }

    std::string cmd_prefix = get_python_cmd_prefix();
    std::string command = cmd_prefix + " \"" + escaped_request + "\"";
    
    std::string result = "";
    FILE* pipe_stream = nullptr;

#ifdef _WIN32
    pipe_stream = _popen(command.c_str(), "r");
#else
    pipe_stream = popen(command.c_str(), "r");
#endif

    if (!pipe_stream) {
        return "{\"status\": \"error\", \"message\": \"Failed to open pipe\"}";
    }

    char buffer[128];
    while (fgets(buffer, 128, pipe_stream) != NULL) {
        result += buffer;
    }

#ifdef _WIN32
    _pclose(pipe_stream);
#else
    pclose(pipe_stream);
#endif
    
    size_t first = result.find_first_not_of(" \t\n\r");
    if (first == std::string::npos) {
        result = "";
    } else {
        size_t last = result.find_last_not_of(" \t\n\r");
        result = result.substr(first, (last - first + 1));
    }
    
    if (result.empty()) {
        return "{\"status\": \"error\", \"message\": \"Empty response from logic\"}";
    }

    return result;
}

std::string NetworkInterface::process_request(SOCKET clientSocket, const std::string& request) {
    std::cout << "Received: " << request << std::endl;

    // Challenge Logic
    bool is_challenge = false;
    if (request.find("\"action\": \"challenge\"") != std::string::npos || 
        request.find("\"action\":\"challenge\"") != std::string::npos ||
        request.find("\"type\": \"SEND_CHALLENGE\"") != std::string::npos ||
        request.find("\"type\":\"SEND_CHALLENGE\"") != std::string::npos) {
        is_challenge = true;
    }

    if (is_challenge) {
        int target_id = get_json_int(request, "target_id");
        
        // Resolve username if target_id is missing
        if (target_id == 0) {
            std::string opponent_username = get_json_string(request, "opponent_username");
            if (!opponent_username.empty()) {
                 std::string resolve_req = "{\"action\": \"get_player_id\", \"username\": \"" + opponent_username + "\"}";
                 std::string resolve_res = execute_logic_command(resolve_req);
                 target_id = get_json_int(resolve_res, "player_id");
            }
        }

        int sender_id = 0;
        
        {
            std::lock_guard<std::mutex> lock(session_mutex);
            if (client_sessions.find(clientSocket) != client_sessions.end()) {
                sender_id = client_sessions[clientSocket];
            }
        }

        if (sender_id == 0) return "{\"status\": \"error\", \"message\": \"You are not logged in\"}";

        if (target_id == 0) return "{\"status\": \"error\", \"message\": \"Player not found or not specified\"}";

        std::lock_guard<std::mutex> lock(session_mutex);
        SOCKET targetSocket = INVALID_SOCKET;
        for (auto const& [sock, pid] : client_sessions) {
            if (pid == target_id) {
                targetSocket = sock;
                break;
            }
        }

        if (targetSocket != INVALID_SOCKET) {
             std::string msg = "{\"type\": \"challenge_request\", \"from_id\": " + std::to_string(sender_id) + "}";
             send(targetSocket, msg.c_str(), static_cast<int>(msg.length()), 0);
             send(targetSocket, "\n", 1, 0);
             return "{\"status\": \"success\", \"message\": \"Challenge sent\"}";
        } else {
            return "{\"status\": \"error\", \"message\": \"Player not found online\"}";
        }
    }
    
    if (request.find("\"action\": \"accept_challenge\"") != std::string::npos || request.find("\"action\":\"accept_challenge\"") != std::string::npos) {
        int challenger_id = get_json_int(request, "challenger_id");
        int my_id = 0;

         {
            std::lock_guard<std::mutex> lock(session_mutex);
            if (client_sessions.find(clientSocket) != client_sessions.end()) {
                my_id = client_sessions[clientSocket];
            }
        }
        
        // 1. Create Game
        std::string create_req = "{\"action\": \"create_game\", \"white_id\": " + std::to_string(challenger_id) + ", \"black_id\": " + std::to_string(my_id) + "}";
        std::string create_res = execute_logic_command(create_req);
        
        int game_id = get_json_int(create_res, "game_id");
        if (game_id == 0) {
             return "{\"status\": \"error\", \"message\": \"Failed to create game\"}";
        }

        // 2. Notify Challenger
        std::lock_guard<std::mutex> lock(session_mutex);
        SOCKET challengerSocket = INVALID_SOCKET;
        for (auto const& [sock, pid] : client_sessions) {
            if (pid == challenger_id) {
                challengerSocket = sock;
                break;
            }
        }

        if (challengerSocket != INVALID_SOCKET) {
             std::string msg = "{\"type\": \"challenge_accepted\", \"game_id\": " + std::to_string(game_id) + ", \"opponent_id\": " + std::to_string(my_id) + ", \"color\": \"white\"}";
             send(challengerSocket, msg.c_str(), static_cast<int>(msg.length()), 0);
             send(challengerSocket, "\n", 1, 0);
        }

        // 3. Return to Acceptor
        return "{\"status\": \"success\", \"type\": \"challenge_accepted\", \"game_id\": " + std::to_string(game_id) + ", \"opponent_id\": " + std::to_string(challenger_id) + ", \"color\": \"black\"}";
    }

    if (request.find("\"action\": \"decline_challenge\"") != std::string::npos || request.find("\"action\":\"decline_challenge\"") != std::string::npos) {
         int challenger_id = get_json_int(request, "challenger_id");
         int my_id = 0;
          {
            std::lock_guard<std::mutex> lock(session_mutex);
            if (client_sessions.find(clientSocket) != client_sessions.end()) {
                my_id = client_sessions[clientSocket];
            }
        }

         std::lock_guard<std::mutex> lock(session_mutex);
         SOCKET challengerSocket = INVALID_SOCKET;
        for (auto const& [sock, pid] : client_sessions) {
            if (pid == challenger_id) {
                challengerSocket = sock;
                break;
            }
        }
        if (challengerSocket != INVALID_SOCKET) {
             std::string msg = "{\"type\": \"challenge_declined\", \"from_id\": " + std::to_string(my_id) + "}";
             send(challengerSocket, msg.c_str(), static_cast<int>(msg.length()), 0);
             send(challengerSocket, "\n", 1, 0);
        }
        return "{\"status\": \"success\"}";
    }


    std::string result = execute_logic_command(request);

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
                     if (it != ready_players.end()) {
                        ready_players.erase(it, ready_players.end());
                     }
                 }
            }
        }
    }

    return result;
}
