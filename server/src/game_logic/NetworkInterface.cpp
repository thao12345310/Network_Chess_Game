#include "NetworkInterface.h"
#include "Protocol.h"
#include <iostream>
#include <functional>
#include <cstdlib>
#include <vector>
#include <algorithm>
#include <fstream>

static std::string get_python_cmd_prefix()
{
    std::string script = "logic_wrapper.py";
    // Check if script exists in current directory
    {
        std::ifstream f(script);
        if (f.good())
        {
            return "python3 " + script;
        }
    }
    // Check if script exists in game_logic/ subdirectory
    {
        std::string sub = "game_logic/logic_wrapper.py";
        std::ifstream f(sub);
        if (f.good())
        {
            return "python3 " + sub;
        }
    }
    // Check if script exists in src/game_logic/ subdirectory
    {
        std::string sub = "src/game_logic/logic_wrapper.py";
        std::ifstream f(sub);
        if (f.good())
        {
            return "python3 " + sub;
        }
    }

    // Default fallback
    return "python3 " + script;
}

NetworkInterface::NetworkInterface(int port) : port(port)
{
    streamServer = std::make_unique<StreamServer>(
        port, [this](SOCKET clientSocket, const std::string &request)
        { return process_request(clientSocket, request); });

    streamServer->setOnConnectionClosed([this](SOCKET clientSocket)
                                        { handle_disconnect(clientSocket); });
}

NetworkInterface::~NetworkInterface() = default;

void NetworkInterface::start()
{
    if (!streamServer)
    {
        std::cerr << "Stream server is not initialized" << std::endl;
        return;
    }

    streamServer->start();
}

void NetworkInterface::handle_disconnect(SOCKET clientSocket)
{
    std::lock_guard<std::mutex> lock(session_mutex);
    auto it = client_sessions.find(clientSocket);
    if (it != client_sessions.end())
    {
        int player_id = it->second;
        std::cout << "Client disconnected: Socket " << clientSocket << " (Player " << player_id << ")" << std::endl;

        // Remove from session map
        client_sessions.erase(it);

        // Remove from ready players (Network logic)
        auto rit = std::remove(ready_players.begin(), ready_players.end(), player_id);
        if (rit != ready_players.end())
        {
            ready_players.erase(rit, ready_players.end());
            // Optionally: call python to sync DB
            std::string cmd_prefix = get_python_cmd_prefix();
            std::string command = cmd_prefix + " \"{\\\"action\\\": \\\"leave_lobby\\\", \\\"player_id\\\": " + std::to_string(player_id) + "}\"";
            system(command.c_str());
        }
        
        // Remove from matchmaking queue if waiting
        for (auto mit = matchmaking_queue.begin(); mit != matchmaking_queue.end(); ++mit)
        {
            if (mit->player_id == player_id)
            {
                matchmaking_queue.erase(mit);
                std::cout << "Removed player " << player_id << " from matchmaking queue" << std::endl;
                break;
            }
        }
    }
    else
    {
        // Unidentified client disconnected
    }
}

static int get_json_int(const std::string &json, const std::string &key)
{
    std::string key_str = "\"" + key + "\":";
    size_t pos = json.find(key_str);
    if (pos == std::string::npos)
    {
        key_str = "\"" + key + "\": ";
        pos = json.find(key_str);
    }
    if (pos == std::string::npos)
        return 0;

    size_t val_start = pos + key_str.length();
    // Skip non-digits (like " or space)
    while (val_start < json.length() && (json[val_start] < '0' || json[val_start] > '9') && json[val_start] != '-')
        val_start++;

    return std::atoi(json.c_str() + val_start);
}

static std::string get_json_string(const std::string &json, const std::string &key)
{
    std::string key_str = "\"" + key + "\":";
    size_t pos = json.find(key_str);
    if (pos == std::string::npos)
    {
        key_str = "\"" + key + "\": ";
        pos = json.find(key_str);
    }
    if (pos == std::string::npos)
        return "";

    size_t val_start = pos + key_str.length();
    // find start quote
    size_t quote_start = json.find("\"", val_start);
    if (quote_start == std::string::npos)
        return "";

    size_t quote_end = json.find("\"", quote_start + 1);
    if (quote_end == std::string::npos)
        return "";

    return json.substr(quote_start + 1, quote_end - quote_start - 1);
}

static double get_json_double(const std::string &json, const std::string &key)
{
    std::string key_str = "\"" + key + "\":";
    size_t pos = json.find(key_str);
    if (pos == std::string::npos)
    {
        key_str = "\"" + key + "\": ";
        pos = json.find(key_str);
    }
    if (pos == std::string::npos)
        return 600.0; // Default fallback

    size_t val_start = pos + key_str.length();
    // Skip spaces
    while (val_start < json.length() && (json[val_start] == ' ' || json[val_start] == '\t'))
        val_start++;

    // Check if we hit end or invalid char
    if (val_start >= json.length())
        return 600.0;

    // Parse double manually to avoid complex dependencies or just use atof
    return std::atof(json.c_str() + val_start);
}

std::string NetworkInterface::execute_logic_command(const std::string &request)
{
    std::string escaped_request;
    for (char c : request)
    {
        if (c == '"')
        {
            escaped_request += "\\\"";
        }
        else
        {
            escaped_request += c;
        }
    }

    std::string cmd_prefix = get_python_cmd_prefix();
    std::string command = cmd_prefix + " \"" + escaped_request + "\"";

    std::string result = "";
    FILE *pipe_stream = popen(command.c_str(), "r");

    if (!pipe_stream)
    {
        return "{\"status\": \"error\", \"message\": \"Failed to open pipe\"}";
    }

    char buffer[128];
    while (fgets(buffer, 128, pipe_stream) != NULL)
    {
        result += buffer;
    }

    pclose(pipe_stream);

    size_t first = result.find_first_not_of(" \t\n\r");
    if (first == std::string::npos)
    {
        result = "";
    }
    else
    {
        size_t last = result.find_last_not_of(" \t\n\r");
        result = result.substr(first, (last - first + 1));
    }

    if (result.empty())
    {
        return "{\"status\": \"error\", \"message\": \"Empty response from logic\"}";
    }

    return result;
}

std::string NetworkInterface::process_request(SOCKET clientSocket, const std::string &request)
{
    std::cout << "Received: " << request << std::endl;

    std::string type = get_json_string(request, "type");
    std::string action = get_json_string(request, "action");
    std::string messageType = get_json_string(request, "messageType");

    // Normalize type/action
    if (type.empty())
        type = messageType;
    if (action.empty())
        action = type;

    // Matchmaking / Challenge Handling
    if (type == Protocol::MessageType::CHALLENGE_REQ || action == "challenge" || type == "SEND_CHALLENGE")
    {
        int target_id = get_json_int(request, "target_id");

        // Resolve username if target_id is missing
        if (target_id == 0)
        {
            std::string opponent_username = get_json_string(request, "opponent_username");
            if (!opponent_username.empty())
            {
                std::string resolve_req = "{\"action\": \"get_player_id\", \"username\": \"" + opponent_username + "\"}";
                std::string resolve_res = execute_logic_command(resolve_req);
                target_id = get_json_int(resolve_res, "player_id");
            }
        }

        int sender_id = 0;

        {
            std::lock_guard<std::mutex> lock(session_mutex);
            if (client_sessions.find(clientSocket) != client_sessions.end())
            {
                sender_id = client_sessions[clientSocket];
            }
        }

        if (sender_id == 0)
            return "{\"status\": \"error\", \"message\": \"You are not logged in\"}";

        if (target_id == 0)
            return "{\"status\": \"error\", \"message\": \"Player not found or not specified\"}";

        std::lock_guard<std::mutex> lock(session_mutex);
        SOCKET targetSocket = INVALID_SOCKET;
        for (auto const &[sock, pid] : client_sessions)
        {
            if (pid == target_id)
            {
                targetSocket = sock;
                break;
            }
        }

        if (targetSocket != INVALID_SOCKET)
        {
            // Send CHALLENGE_NOTIFY to target player with proper format
            std::string mode = get_json_string(request, "mode");
            if (mode.empty())
                mode = "RAPID";

            std::string msg = "{\"messageType\": \"CHALLENGE_NOTIFY\", \"responseCode\": 200, \"payload\": {"
                              "\"from_id\": " +
                              std::to_string(sender_id) + ", "
                                                          "\"mode\": \"" +
                              mode + "\", "
                                     "\"challenger_id\": " +
                              std::to_string(sender_id) + "}}";
            send(targetSocket, msg.c_str(), static_cast<int>(msg.length()), 0);
            send(targetSocket, "\n", 1, 0);
            return "{\"messageType\": \"CHALLENGE_REQ\", \"responseCode\": 200, \"payload\": {\"status\": \"sent\"}}";
        }
        else
        {
            return "{\"messageType\": \"ERROR\", \"responseCode\": 404, \"payload\": {\"reason\": \"Player not found online\"}}";
        }
    }

    // MATCH_FIND_REQ - Random Matchmaking
    else if (type == "MATCH_FIND_REQ" || action == "MATCH_FIND_REQ")
    {
        int my_id = 0;
        {
            std::lock_guard<std::mutex> lock(session_mutex);
            if (client_sessions.find(clientSocket) != client_sessions.end())
            {
                my_id = client_sessions[clientSocket];
            }
        }

        if (my_id == 0)
        {
            return "{\"messageType\": \"ERROR\", \"responseCode\": 401, \"payload\": {\"reason\": \"Not logged in\"}}";
        }

        // Get requested game mode
        std::string requested_mode = get_json_string(request, "mode");
        if (requested_mode.empty()) requested_mode = "RAPID";
        
        std::cout << "DEBUG MATCHMAKING: Player " << my_id << " requests mode: [" << requested_mode << "]" << std::endl;

        std::lock_guard<std::mutex> lock(session_mutex);
        
        // Debug: Print current queue state
        std::cout << "DEBUG MATCHMAKING: Current queue (" << matchmaking_queue.size() << " players):" << std::endl;
        for (const auto& entry : matchmaking_queue)
        {
            std::cout << "  - Player " << entry.player_id << ", mode: [" << entry.mode << "]" << std::endl;
        }

        // Check if already in queue (by player_id) - update mode if different
        bool already_in_queue = false;
        for (auto& entry : matchmaking_queue)
        {
            if (entry.player_id == my_id)
            {
                if (entry.mode == requested_mode)
                {
                    // Same mode, just waiting
                    return "{\"messageType\": \"MATCH_FIND_ACK\", \"responseCode\": 200, \"payload\": {\"status\": \"waiting\"}}";
                }
                else
                {
                    // Different mode requested - update and continue to find new match
                    std::cout << "Player " << my_id << " changed mode from [" << entry.mode << "] to [" << requested_mode << "]" << std::endl;
                    entry.mode = requested_mode;
                    already_in_queue = true;
                    break;
                }
            }
        }

        // Add to queue with mode (if not already in queue)
        if (!already_in_queue)
        {
            MatchmakingEntry my_entry;
            my_entry.player_id = my_id;
            my_entry.mode = requested_mode;
            matchmaking_queue.push_back(my_entry);
            std::cout << "Player " << my_id << " joined matchmaking queue with mode: " << requested_mode << ". Queue size: " << matchmaking_queue.size() << std::endl;
        }

        // Find a compatible opponent (same mode)
        int match_idx = -1;
        for (size_t i = 0; i < matchmaking_queue.size(); ++i)
        {
            // Skip self (we just added ourselves at the end)
            if (matchmaking_queue[i].player_id == my_id) continue;
            
            // Check if modes match
            if (matchmaking_queue[i].mode == requested_mode)
            {
                match_idx = static_cast<int>(i);
                break;
            }
        }

        // If found a compatible opponent
        if (match_idx >= 0)
        {
            int player1_id = matchmaking_queue[match_idx].player_id;
            int player2_id = my_id;
            std::string mode = requested_mode;

            // Remove both players from queue
            // Remove player1 first (match_idx), then find and remove player2 (my_id)
            matchmaking_queue.erase(matchmaking_queue.begin() + match_idx);
            
            // Now find and remove my_id (index might have shifted)
            for (auto it = matchmaking_queue.begin(); it != matchmaking_queue.end(); ++it)
            {
                if (it->player_id == my_id)
                {
                    matchmaking_queue.erase(it);
                    break;
                }
            }

            // Create game via Python
            std::string create_req = "{\"action\": \"create_game\", \"white_id\": " + std::to_string(player1_id) +
                                     ", \"black_id\": " + std::to_string(player2_id) + ", \"mode\": \"" + mode + "\"}";
            std::string create_res = execute_logic_command(create_req);
            int game_id = get_json_int(create_res, "game_id");

            if (game_id == 0)
            {
                // Put players back in queue
                MatchmakingEntry entry1, entry2;
                entry1.player_id = player1_id;
                entry1.mode = mode;
                entry2.player_id = player2_id;
                entry2.mode = mode;
                matchmaking_queue.insert(matchmaking_queue.begin(), entry2);
                matchmaking_queue.insert(matchmaking_queue.begin(), entry1);
                return "{\"messageType\": \"ERROR\", \"responseCode\": 500, \"payload\": {\"reason\": \"Failed to create game\"}}";
            }

            // Find sockets for both players
            SOCKET socket1 = INVALID_SOCKET, socket2 = INVALID_SOCKET;
            for (auto const &[sock, pid] : client_sessions)
            {
                if (pid == player1_id)
                    socket1 = sock;
                if (pid == player2_id)
                    socket2 = sock;
            }

            // Determine time control string
            std::string time_control = "10+0";
            if (mode == "BLITZ")
                time_control = "5+0";
            else if (mode == "CLASSICAL")
                time_control = "30+0";

            // Send MATCH_START to player1 (white)
            if (socket1 != INVALID_SOCKET)
            {
                std::string msg1 = "{\"messageType\": \"MATCH_START\", \"responseCode\": 200, \"payload\": {"
                                   "\"game_id\": " +
                                   std::to_string(game_id) + ", "
                                                             "\"opponent_id\": " +
                                   std::to_string(player2_id) + ", "
                                                                "\"your_color\": \"white\", "
                                                                "\"time_control\": \"" +
                                   time_control + "\"}}";
                send(socket1, msg1.c_str(), static_cast<int>(msg1.length()), 0);
                send(socket1, "\n", 1, 0);
            }

            // Send MATCH_START to player2 (black)
            if (socket2 != INVALID_SOCKET)
            {
                std::string msg2 = "{\"messageType\": \"MATCH_START\", \"responseCode\": 200, \"payload\": {"
                                   "\"game_id\": " +
                                   std::to_string(game_id) + ", "
                                                             "\"opponent_id\": " +
                                   std::to_string(player1_id) + ", "
                                                                "\"your_color\": \"black\", "
                                                                "\"time_control\": \"" +
                                   time_control + "\"}}";
                send(socket2, msg2.c_str(), static_cast<int>(msg2.length()), 0);
                send(socket2, "\n", 1, 0);
            }

            std::cout << "Match created! Game " << game_id << ": Player " << player1_id << " (white) vs Player " << player2_id << " (black) [Mode: " << mode << "]" << std::endl;

            // Return acknowledgment to the requesting client
            return "{\"messageType\": \"MATCH_START\", \"responseCode\": 200, \"payload\": {"
                   "\"game_id\": " +
                   std::to_string(game_id) + ", "
                                             "\"opponent_id\": " +
                   std::to_string(my_id == player1_id ? player2_id : player1_id) + ", "
                                                                                   "\"your_color\": \"" +
                   std::string(my_id == player1_id ? "white" : "black") + "\", "
                                                                          "\"time_control\": \"" +
                   time_control + "\"}}";
        }

        // Still waiting for opponent with same mode
        return "{\"messageType\": \"MATCH_FIND_ACK\", \"responseCode\": 200, \"payload\": {\"status\": \"waiting\", \"message\": \"Waiting for opponent with same game mode...\"}}";
    }

    // MATCH_CANCEL_REQ - Cancel Matchmaking
    else if (type == "MATCH_CANCEL_REQ" || action == "MATCH_CANCEL_REQ")
    {
        int my_id = 0;
        {
            std::lock_guard<std::mutex> lock(session_mutex);
            if (client_sessions.find(clientSocket) != client_sessions.end())
            {
                my_id = client_sessions[clientSocket];
            }
        }

        if (my_id == 0)
        {
            return "{\"messageType\": \"ERROR\", \"responseCode\": 401, \"payload\": {\"reason\": \"Not logged in\"}}";
        }

        std::lock_guard<std::mutex> lock(session_mutex);
        
        // Find and remove player from matchmaking queue
        bool found = false;
        for (auto it = matchmaking_queue.begin(); it != matchmaking_queue.end(); ++it)
        {
            if (it->player_id == my_id)
            {
                matchmaking_queue.erase(it);
                found = true;
                std::cout << "Player " << my_id << " cancelled matchmaking. Queue size: " << matchmaking_queue.size() << std::endl;
                break;
            }
        }

        if (found)
        {
            return "{\"messageType\": \"MATCH_CANCEL_ACK\", \"responseCode\": 200, \"payload\": {\"status\": \"cancelled\", \"message\": \"Matchmaking cancelled successfully\"}}";
        }
        else
        {
            return "{\"messageType\": \"MATCH_CANCEL_ACK\", \"responseCode\": 200, \"payload\": {\"status\": \"not_in_queue\", \"message\": \"You were not in the matchmaking queue\"}}";
        }
    }

    // LOBBY_LIST - Get list of online players
    else if (type == "LOBBY_LIST" || action == "LOBBY_LIST")
    {
        // Build list of online players from client_sessions (actual connected players)
        std::vector<int> online_player_ids;
        {
            std::lock_guard<std::mutex> lock(session_mutex);
            for (const auto& [sock, pid] : client_sessions)
            {
                online_player_ids.push_back(pid);
            }
        }
        
        std::cout << "LOBBY_LIST: Found " << online_player_ids.size() << " online players" << std::endl;
        
        // Build players array by fetching info for each online player from database
        std::string players_arr = "[";
        bool first = true;
        for (int pid : online_player_ids)
        {
            // Get player info from database
            std::string get_info_req = "{\"action\": \"get_player_info\", \"player_id\": " + std::to_string(pid) + "}";
            std::string info_res = execute_logic_command(get_info_req);
            
            // Extract username and elo from response
            std::string username = get_json_string(info_res, "username");
            int elo = get_json_int(info_res, "elo");
            
            // Skip if we couldn't get player info
            if (username.empty()) continue;
            
            if (!first) players_arr += ", ";
            first = false;
            
            players_arr += "{\"player_id\": " + std::to_string(pid) + 
                          ", \"username\": \"" + username + "\"" +
                          ", \"elo\": " + std::to_string(elo) + "}";
        }
        players_arr += "]";
        
        std::string response = "{\"messageType\": \"LOBBY_LIST\", \"responseCode\": 200, \"payload\": {\"players\": " + players_arr + "}}";
        std::cout << "LOBBY_LIST response: " << response << std::endl;
        return response;
    }

    // LEADERBOARD_REQ - Get top players by ELO
    else if (type == "LEADERBOARD_REQ" || action == "LEADERBOARD_REQ")
    {
        std::string list_res = execute_logic_command("{\"action\": \"get_leaderboard\"}");

        // Extract leaderboard array
        size_t lb_start = list_res.find("\"leaderboard\":");
        if (lb_start != std::string::npos)
        {
            size_t arr_start = list_res.find("[", lb_start);
            // Need to find matching closing bracket, simplified assuming no nested brackets in username
            // Actually users might use nested brackets? No, valid JSON structure for list of objects.
            // But simply finding ']' might be premature if username contains ']'.
            // However logic_wrapper produces standard JSON.
            // Let's rely on logic_wrapper output format which is usually compact or standard.
            // Better: find the LAST ']' corresponding to the first '['.
            // Since it's a flat list of dicts, it shouldn't be too nested, but just finding ANY ']' might stop early.
            // But LOBBY_LIST uses find("]", arr_start), so I'll trust that for now or improve it.
            // Actually, `execute_logic_command` returns the full JSON object string.
            // The JSON from python is {"status": "success", "leaderboard": [...]}
            // So finding "]" at the end should work.
            size_t arr_end = list_res.find_last_of("]");

            if (arr_start != std::string::npos && arr_end != std::string::npos && arr_end > arr_start)
            {
                std::string lb_arr = list_res.substr(arr_start, arr_end - arr_start + 1);
                return "{\"messageType\": \"LEADERBOARD\", \"responseCode\": 200, \"payload\": {\"leaderboard\": " + lb_arr + "}}";
            }
        }
        return "{\"messageType\": \"LEADERBOARD\", \"responseCode\": 200, \"payload\": {\"leaderboard\": []}}";
    }

    // Accept/Decline Challenge - Handle both old format and new CHALLENGE_RESP format
    else if (action == "accept_challenge" || type == "accept_challenge" ||
             type == "CHALLENGE_RESP" || action == "CHALLENGE_RESP")
    {

        std::cout << "DEBUG: Entered CHALLENGE_RESP handler" << std::endl;

        // Check if this is accept or decline
        std::string accepted_str = get_json_string(request, "accepted");
        bool is_accepted = (accepted_str == "true" || accepted_str.empty()); // Default to accept if not specified

        // Also check payload.accepted for nested format - look for true as well
        if (request.find("\"accepted\": false") != std::string::npos ||
            request.find("\"accepted\":false") != std::string::npos)
        {
            is_accepted = false;
        }
        // Also check for true to confirm acceptance
        if (request.find("\"accepted\":true") != std::string::npos ||
            request.find("\"accepted\": true") != std::string::npos)
        {
            is_accepted = true;
        }

        std::cout << "DEBUG: is_accepted = " << (is_accepted ? "true" : "false") << std::endl;

        // Get challenger ID - try multiple fields
        int challenger_id = get_json_int(request, "challenger_id");
        if (challenger_id == 0)
            challenger_id = get_json_int(request, "from_id");
        if (challenger_id == 0)
            challenger_id = get_json_int(request, "challenge_id"); // Sometimes challenge_id is the sender's ID

        std::cout << "DEBUG: challenger_id = " << challenger_id << std::endl;
        int my_id = 0;
        {
            std::lock_guard<std::mutex> lock(session_mutex);
            if (client_sessions.find(clientSocket) != client_sessions.end())
            {
                my_id = client_sessions[clientSocket];
            }
        }

        if (challenger_id == 0)
        {
            return "{\"messageType\": \"ERROR\", \"responseCode\": 400, \"payload\": {\"reason\": \"Missing challenger_id\"}}";
        }

        if (!is_accepted)
        {
            // Decline challenge
            std::lock_guard<std::mutex> lock(session_mutex);
            SOCKET challengerSocket = INVALID_SOCKET;
            for (auto const &[sock, pid] : client_sessions)
            {
                if (pid == challenger_id)
                {
                    challengerSocket = sock;
                    break;
                }
            }
            if (challengerSocket != INVALID_SOCKET)
            {
                std::string msg = "{\"messageType\": \"CHALLENGE_RESP\", \"responseCode\": 200, \"payload\": {\"accepted\": false, \"from_id\": " + std::to_string(my_id) + "}}";
                send(challengerSocket, msg.c_str(), static_cast<int>(msg.length()), 0);
                send(challengerSocket, "\n", 1, 0);
            }
            return "{\"messageType\": \"CHALLENGE_RESP\", \"responseCode\": 200, \"payload\": {\"status\": \"declined\"}}";
        }

        // Accept challenge - Create Game
        std::string mode = get_json_string(request, "mode");
        if (mode.empty())
            mode = "RAPID";

        std::string create_req = "{\"action\": \"create_game\", \"white_id\": " + std::to_string(challenger_id) + ", \"black_id\": " + std::to_string(my_id) + ", \"mode\": \"" + mode + "\"}";
        std::cout << "DEBUG: Creating game with: " << create_req << std::endl;
        std::string create_res = execute_logic_command(create_req);
        std::cout << "DEBUG: Python response: " << create_res << std::endl;

        int game_id = get_json_int(create_res, "game_id");
        std::cout << "DEBUG: Parsed game_id: " << game_id << std::endl;
        if (game_id == 0)
        {
            std::cout << "ERROR: Game creation failed!" << std::endl;
            return "{\"messageType\": \"ERROR\", \"responseCode\": 500, \"payload\": {\"reason\": \"Failed to create game\"}}";
        }

        // Determine time control string
        std::string time_control = "10+0";
        if (mode == "BLITZ")
            time_control = "5+0";
        else if (mode == "CLASSICAL")
            time_control = "30+0";

        // Notify Challenger with MATCH_START
        std::lock_guard<std::mutex> lock(session_mutex);
        SOCKET challengerSocket = INVALID_SOCKET;
        for (auto const &[sock, pid] : client_sessions)
        {
            if (pid == challenger_id)
            {
                challengerSocket = sock;
                break;
            }
        }

        if (challengerSocket != INVALID_SOCKET)
        {
            std::string msg = "{\"messageType\": \"MATCH_START\", \"responseCode\": 200, \"payload\": {"
                              "\"game_id\": " +
                              std::to_string(game_id) + ", "
                                                        "\"opponent_id\": " +
                              std::to_string(my_id) + ", "
                                                      "\"your_color\": \"white\", "
                                                      "\"time_control\": \"" +
                              time_control + "\"}}";
            send(challengerSocket, msg.c_str(), static_cast<int>(msg.length()), 0);
            send(challengerSocket, "\n", 1, 0);
        }

        std::cout << "Challenge accepted! Game " << game_id << ": Player " << challenger_id << " (white) vs Player " << my_id << " (black)" << std::endl;

        // Return MATCH_START to Acceptor
        return "{\"messageType\": \"MATCH_START\", \"responseCode\": 200, \"payload\": {"
               "\"game_id\": " +
               std::to_string(game_id) + ", "
                                         "\"opponent_id\": " +
               std::to_string(challenger_id) + ", "
                                               "\"your_color\": \"black\", "
                                               "\"time_control\": \"" +
               time_control + "\"}}";
    }

    // Decline Challenge
    else if (action == "decline_challenge" || type == "decline_challenge")
    {
        int challenger_id = get_json_int(request, "challenger_id");
        int my_id = 0;
        {
            std::lock_guard<std::mutex> lock(session_mutex);
            if (client_sessions.find(clientSocket) != client_sessions.end())
            {
                my_id = client_sessions[clientSocket];
            }
        }

        std::lock_guard<std::mutex> lock(session_mutex);
        SOCKET challengerSocket = INVALID_SOCKET;
        for (auto const &[sock, pid] : client_sessions)
        {
            if (pid == challenger_id)
            {
                challengerSocket = sock;
                break;
            }
        }
        if (challengerSocket != INVALID_SOCKET)
        {
            std::string msg = "{\"type\": \"challenge_declined\", \"from_id\": " + std::to_string(my_id) + "}";
            send(challengerSocket, msg.c_str(), static_cast<int>(msg.length()), 0);
            send(challengerSocket, "\n", 1, 0);
        }
        return "{\"status\": \"success\"}";
    }

    // GAME_RESIGN - Player resigns from game
    else if (type == Protocol::MessageType::GAME_RESIGN || action == "GAME_RESIGN")
    {
        int game_id = get_json_int(request, "game_id");
        int my_id = 0;
        {
            std::lock_guard<std::mutex> lock(session_mutex);
            if (client_sessions.find(clientSocket) != client_sessions.end())
            {
                my_id = client_sessions[clientSocket];
            }
        }

        if (my_id == 0)
        {
            return "{\"messageType\": \"ERROR\", \"responseCode\": 401, \"payload\": {\"reason\": \"Not logged in\"}}";
        }

        if (game_id == 0)
        {
            return "{\"messageType\": \"ERROR\", \"responseCode\": 400, \"payload\": {\"reason\": \"Missing game_id\"}}";
        }

        // Call Python to handle resign logic (update game result, calculate ELO)
        std::string resign_req = "{\"action\": \"resign_game\", \"game_id\": " + std::to_string(game_id) +
                                 ", \"player_id\": " + std::to_string(my_id) + "}";
        std::string resign_res = execute_logic_command(resign_req);

        // Check if resign was successful
        bool success = (resign_res.find("\"status\": \"success\"") != std::string::npos) ||
                       (resign_res.find("\"responseCode\": 200") != std::string::npos);

        if (success)
        {
            // Get opponent_id and new ELOs from response
            int opponent_id = get_json_int(resign_res, "opponent_id");
            int winner_elo = get_json_int(resign_res, "winner_elo");
            int loser_elo = get_json_int(resign_res, "loser_elo");

            // Notify opponent that game ended by resignation
            if (opponent_id > 0)
            {
                std::lock_guard<std::mutex> lock(session_mutex);
                SOCKET opponentSocket = INVALID_SOCKET;
                for (auto const &[sock, pid] : client_sessions)
                {
                    if (pid == opponent_id)
                    {
                        opponentSocket = sock;
                        break;
                    }
                }

                if (opponentSocket != INVALID_SOCKET)
                {
                    std::string end_msg = "{\"messageType\": \"GAME_END\", \"responseCode\": 200, \"payload\": {"
                                          "\"game_id\": " +
                                          std::to_string(game_id) + ", "
                                                                    "\"result\": \"win\", "
                                                                    "\"reason\": \"opponent_resigned\", "
                                                                    "\"new_elo\": " +
                                          std::to_string(winner_elo) + "}}";
                    send(opponentSocket, end_msg.c_str(), static_cast<int>(end_msg.length()), 0);
                    send(opponentSocket, "\n", 1, 0);
                    std::cout << "Notified player " << opponent_id << " of resignation" << std::endl;
                }
            }

            // Return GAME_END to resigning player
            return "{\"messageType\": \"GAME_END\", \"responseCode\": 200, \"payload\": {"
                   "\"game_id\": " +
                   std::to_string(game_id) + ", "
                                             "\"result\": \"loss\", "
                                             "\"reason\": \"resigned\", "
                                             "\"new_elo\": " +
                   std::to_string(loser_elo) + "}}";
        }
        else
        {
            // Resign failed
            std::string error_reason = get_json_string(resign_res, "message");
            if (error_reason.empty())
                error_reason = "Failed to resign";
            return "{\"messageType\": \"ERROR\", \"responseCode\": 500, \"payload\": {\"reason\": \"" + error_reason + "\"}}";
        }
    }

    // DRAW_OFFER - Player offers a draw
    else if (type == Protocol::MessageType::DRAW_OFFER || action == "DRAW_OFFER" || type == "DRAW_OFFER")
    {
        int game_id = get_json_int(request, "game_id");
        int my_id = 0;
        {
            std::lock_guard<std::mutex> lock(session_mutex);
            if (client_sessions.find(clientSocket) != client_sessions.end())
            {
                my_id = client_sessions[clientSocket];
            }
        }

        if (my_id == 0)
        {
            return "{\"messageType\": \"ERROR\", \"responseCode\": 401, \"payload\": {\"reason\": \"Not logged in\"}}";
        }

        if (game_id == 0)
        {
            return "{\"messageType\": \"ERROR\", \"responseCode\": 400, \"payload\": {\"reason\": \"Missing game_id\"}}";
        }

        // Get opponent_id from game info
        std::string game_req = "{\"action\": \"get_game_info\", \"game_id\": " + std::to_string(game_id) + "}";
        std::string game_res = execute_logic_command(game_req);

        int white_id = get_json_int(game_res, "white_id");
        int black_id = get_json_int(game_res, "black_id");
        int opponent_id = (my_id == white_id) ? black_id : white_id;

        if (opponent_id == 0)
        {
            return "{\"messageType\": \"ERROR\", \"responseCode\": 404, \"payload\": {\"reason\": \"Game not found or opponent not identified\"}}";
        }

        // Notify opponent of withdraw offer
        {
            std::lock_guard<std::mutex> lock(session_mutex);
            SOCKET opponentSocket = INVALID_SOCKET;
            for (auto const &[sock, pid] : client_sessions)
            {
                if (pid == opponent_id)
                {
                    opponentSocket = sock;
                    break;
                }
            }

            if (opponentSocket != INVALID_SOCKET)
            {
                std::string notify_msg = "{\"messageType\": \"DRAW_OFFER_NOTIFY\", \"responseCode\": 200, \"payload\": {"
                                         "\"game_id\": " +
                                         std::to_string(game_id) + ", "
                                                                   "\"from_id\": " +
                                         std::to_string(my_id) + "}}";
                send(opponentSocket, notify_msg.c_str(), static_cast<int>(notify_msg.length()), 0);
                send(opponentSocket, "\n", 1, 0);
                std::cout << "Sent draw offer to player " << opponent_id << std::endl;
            }
            else
            {
                return "{\"messageType\": \"ERROR\", \"responseCode\": 404, \"payload\": {\"reason\": \"Opponent not online\"}}";
            }
        }

        // Return acknowledgment to sender
        return "{\"messageType\": \"DRAW_OFFER_ACK\", \"responseCode\": 200, \"payload\": {"
               "\"game_id\": " +
               std::to_string(game_id) + ", "
                                         "\"status\": \"sent\"}}";
    }

    // DRAW_ACCEPT - Player accepts draw offer
    else if (type == Protocol::MessageType::DRAW_ACCEPT || action == "DRAW_ACCEPT" || type == "DRAW_ACCEPT")
    {
        int game_id = get_json_int(request, "game_id");
        int my_id = 0;
        {
            std::lock_guard<std::mutex> lock(session_mutex);
            if (client_sessions.find(clientSocket) != client_sessions.end())
            {
                my_id = client_sessions[clientSocket];
            }
        }

        if (my_id == 0)
        {
            return "{\"messageType\": \"ERROR\", \"responseCode\": 401, \"payload\": {\"reason\": \"Not logged in\"}}";
        }

        if (game_id == 0)
        {
            return "{\"messageType\": \"ERROR\", \"responseCode\": 400, \"payload\": {\"reason\": \"Missing game_id\"}}";
        }

        // Call Python to process draw acceptance
        std::string draw_req = "{\"action\": \"accept_draw\", \"game_id\": " + std::to_string(game_id) + "}";
        std::string draw_res = execute_logic_command(draw_req);

        // Parse response
        bool success = (draw_res.find("\"status\": \"success\"") != std::string::npos);

        if (success)
        {
            int white_id = get_json_int(draw_res, "white_id");
            int black_id = get_json_int(draw_res, "black_id");
            int white_elo = get_json_int(draw_res, "white_elo");
            int black_elo = get_json_int(draw_res, "black_elo");

            // Broadcast GAME_END to both players
            {
                std::lock_guard<std::mutex> lock(session_mutex);

                for (auto const &[sock, pid] : client_sessions)
                {
                    if (pid == white_id || pid == black_id)
                    {
                        int player_elo = (pid == white_id) ? white_elo : black_elo;
                        std::string end_msg = "{\"messageType\": \"GAME_END\", \"responseCode\": 200, \"payload\": {"
                                              "\"game_id\": " +
                                              std::to_string(game_id) + ", "
                                                                        "\"result\": \"draw\", "
                                                                        "\"reason\": \"draw_accepted\", "
                                                                        "\"new_elo\": " +
                                              std::to_string(player_elo) + "}}";
                        send(sock, end_msg.c_str(), static_cast<int>(end_msg.length()), 0);
                        send(sock, "\n", 1, 0);
                    }
                }
            }

            std::cout << "Draw accepted for game " << game_id << std::endl;

            return "{\"messageType\": \"GAME_END\", \"responseCode\": 200, \"payload\": {"
                   "\"game_id\": " +
                   std::to_string(game_id) + ", "
                                             "\"result\": \"draw\", "
                                             "\"reason\": \"draw_accepted\"}}";
        }
        else
        {
            std::string error_reason = get_json_string(draw_res, "message");
            if (error_reason.empty())
                error_reason = "Failed to accept draw";
            return "{\"messageType\": \"ERROR\", \"responseCode\": 500, \"payload\": {\"reason\": \"" + error_reason + "\"}}";
        }
    }

    // DRAW_DECLINE - Player declines draw offer
    else if (type == Protocol::MessageType::DRAW_DECLINE || action == "DRAW_DECLINE" || type == "DRAW_DECLINE")
    {
        int game_id = get_json_int(request, "game_id");
        int my_id = 0;
        {
            std::lock_guard<std::mutex> lock(session_mutex);
            if (client_sessions.find(clientSocket) != client_sessions.end())
            {
                my_id = client_sessions[clientSocket];
            }
        }

        if (game_id == 0)
        {
            return "{\"messageType\": \"ERROR\", \"responseCode\": 400, \"payload\": {\"reason\": \"Missing game_id\"}}";
        }

        std::cout << "Draw declined for game " << game_id << " by player " << my_id << std::endl;

        // Just acknowledge - game continues
        return "{\"messageType\": \"DRAW_DECLINE_ACK\", \"responseCode\": 200, \"payload\": {"
               "\"game_id\": " +
               std::to_string(game_id) + ", "
                                         "\"status\": \"declined\"}}";
    }

    // ========== REMATCH FLOW ==========

    // REMATCH_REQUEST - Player requests rematch after game ends
    else if (type == Protocol::MessageType::REMATCH_REQUEST || action == "REMATCH_REQUEST" || type == "REMATCH_REQUEST")
    {
        int game_id = get_json_int(request, "game_id");
        int my_id = 0;
        {
            std::lock_guard<std::mutex> lock(session_mutex);
            if (client_sessions.find(clientSocket) != client_sessions.end())
            {
                my_id = client_sessions[clientSocket];
            }
        }

        if (game_id == 0)
        {
            return "{\"messageType\": \"ERROR\", \"responseCode\": 400, \"payload\": {\"reason\": \"Missing game_id\"}}";
        }

        std::cout << "Rematch requested for game " << game_id << " by player " << my_id << std::endl;

        // Get game info to find opponent
        std::string get_game_req = "{\"action\": \"get_game_info\", \"game_id\": " + std::to_string(game_id) + "}";
        std::string game_result = execute_logic_command(get_game_req);

        int white_id = get_json_int(game_result, "white_id");
        int black_id = get_json_int(game_result, "black_id");

        int opponent_id = (my_id == white_id) ? black_id : white_id;

        if (opponent_id == 0)
        {
            return "{\"messageType\": \"ERROR\", \"responseCode\": 404, \"payload\": {\"reason\": \"Opponent not found\"}}";
        }

        std::cout << "Notifying opponent " << opponent_id << " about rematch request" << std::endl;

        // Find opponent socket and notify
        {
            std::lock_guard<std::mutex> lock(session_mutex);
            SOCKET opponentSocket = INVALID_SOCKET;
            for (auto const &[sock, pid] : client_sessions)
            {
                if (pid == opponent_id)
                {
                    opponentSocket = sock;
                    break;
                }
            }

            if (opponentSocket != INVALID_SOCKET)
            {
                // Send REMATCH_REQUEST_NOTIFY to opponent
                std::string notify_msg = "{\"messageType\": \"REMATCH_REQUEST_NOTIFY\", \"responseCode\": 200, \"payload\": {"
                                         "\"game_id\": " +
                                         std::to_string(game_id) + ", "
                                                                   "\"requester_id\": " +
                                         std::to_string(my_id) + "}}";
                send(opponentSocket, notify_msg.c_str(), static_cast<int>(notify_msg.length()), 0);
                send(opponentSocket, "\n", 1, 0);
                std::cout << "Sent REMATCH_REQUEST_NOTIFY to player " << opponent_id << std::endl;
            }
        }

        // Return acknowledgment to requester
        return "{\"messageType\": \"REMATCH_REQUEST_ACK\", \"responseCode\": 200, \"payload\": {"
               "\"game_id\": " +
               std::to_string(game_id) + ", "
                                         "\"status\": \"waiting_for_opponent\"}}";
    }

    // REMATCH_ACCEPT - Player accepts rematch request
    else if (type == Protocol::MessageType::REMATCH_ACCEPT || action == "REMATCH_ACCEPT" || type == "REMATCH_ACCEPT")
    {
        int old_game_id = get_json_int(request, "game_id");
        int my_id = 0;
        {
            std::lock_guard<std::mutex> lock(session_mutex);
            if (client_sessions.find(clientSocket) != client_sessions.end())
            {
                my_id = client_sessions[clientSocket];
            }
        }

        if (old_game_id == 0)
        {
            return "{\"messageType\": \"ERROR\", \"responseCode\": 400, \"payload\": {\"reason\": \"Missing game_id\"}}";
        }

        std::cout << "Rematch accepted for game " << old_game_id << " by player " << my_id << std::endl;

        // Get old game info
        std::string get_game_req = "{\"action\": \"get_game_info\", \"game_id\": " + std::to_string(old_game_id) + "}";
        std::string game_result = execute_logic_command(get_game_req);

        int old_white_id = get_json_int(game_result, "white_id");
        int old_black_id = get_json_int(game_result, "black_id");
        std::string mode = get_json_string(game_result, "mode");

        if (mode.empty())
        {
            mode = "RAPID"; // Default mode
        }

        // Switch colors for new game
        int new_white_id = old_black_id;
        int new_black_id = old_white_id;

        // Create new game with switched colors
        std::string create_req = "{\"action\": \"create_game\", "
                                 "\"white_id\": " +
                                 std::to_string(new_white_id) + ", "
                                                                "\"black_id\": " +
                                 std::to_string(new_black_id) + ", "
                                                                "\"mode\": \"" +
                                 mode + "\"}";
        std::string create_result = execute_logic_command(create_req);

        int new_game_id = get_json_int(create_result, "game_id");

        if (new_game_id == 0)
        {
            return "{\"messageType\": \"ERROR\", \"responseCode\": 500, \"payload\": {\"reason\": \"Failed to create new game\"}}";
        }

        std::cout << "Created new game " << new_game_id << " (rematch of " << old_game_id << ")" << std::endl;

        // Notify both players about new game
        {
            std::lock_guard<std::mutex> lock(session_mutex);

            // Find both player sockets
            SOCKET white_socket = INVALID_SOCKET;
            SOCKET black_socket = INVALID_SOCKET;

            for (auto const &[sock, pid] : client_sessions)
            {
                if (pid == new_white_id)
                    white_socket = sock;
                if (pid == new_black_id)
                    black_socket = sock;
            }

            std::string notify_msg = "{\"messageType\": \"MATCH_START\", \"responseCode\": 200, \"payload\": {"
                                     "\"game_id\": " +
                                     std::to_string(new_game_id) + ", "
                                                                   "\"white_id\": " +
                                     std::to_string(new_white_id) + ", "
                                                                    "\"black_id\": " +
                                     std::to_string(new_black_id) + ", "
                                                                    "\"mode\": \"" +
                                     mode + "\", "
                                            "\"is_rematch\": true, "
                                            "\"old_game_id\": " +
                                     std::to_string(old_game_id) + "}}";

            if (white_socket != INVALID_SOCKET)
            {
                send(white_socket, notify_msg.c_str(), static_cast<int>(notify_msg.length()), 0);
                send(white_socket, "\n", 1, 0);
                std::cout << "Sent MATCH_START (rematch) to white player " << new_white_id << std::endl;
            }

            if (black_socket != INVALID_SOCKET)
            {
                send(black_socket, notify_msg.c_str(), static_cast<int>(notify_msg.length()), 0);
                send(black_socket, "\n", 1, 0);
                std::cout << "Sent MATCH_START (rematch) to black player " << new_black_id << std::endl;
            }
        }

        return "{\"messageType\": \"REMATCH_ACCEPT_ACK\", \"responseCode\": 200, \"payload\": {"
               "\"new_game_id\": " +
               std::to_string(new_game_id) + ", "
                                             "\"old_game_id\": " +
               std::to_string(old_game_id) + "}}";
    }

    // REMATCH_DECLINE - Player declines rematch request
    else if (type == Protocol::MessageType::REMATCH_DECLINE || action == "REMATCH_DECLINE" || type == "REMATCH_DECLINE")
    {
        int game_id = get_json_int(request, "game_id");
        int my_id = 0;
        {
            std::lock_guard<std::mutex> lock(session_mutex);
            if (client_sessions.find(clientSocket) != client_sessions.end())
            {
                my_id = client_sessions[clientSocket];
            }
        }

        if (game_id == 0)
        {
            return "{\"messageType\": \"ERROR\", \"responseCode\": 400, \"payload\": {\"reason\": \"Missing game_id\"}}";
        }

        std::cout << "Rematch declined for game " << game_id << " by player " << my_id << std::endl;

        // Get game info to find requester (opponent)
        std::string get_game_req = "{\"action\": \"get_game_info\", \"game_id\": " + std::to_string(game_id) + "}";
        std::string game_result = execute_logic_command(get_game_req);

        int white_id = get_json_int(game_result, "white_id");
        int black_id = get_json_int(game_result, "black_id");

        int requester_id = (my_id == white_id) ? black_id : white_id;

        // Notify requester that rematch was declined
        {
            std::lock_guard<std::mutex> lock(session_mutex);
            SOCKET requesterSocket = INVALID_SOCKET;
            for (auto const &[sock, pid] : client_sessions)
            {
                if (pid == requester_id)
                {
                    requesterSocket = sock;
                    break;
                }
            }

            if (requesterSocket != INVALID_SOCKET)
            {
                std::string notify_msg = "{\"messageType\": \"REMATCH_DECLINED_NOTIFY\", \"responseCode\": 200, \"payload\": {"
                                         "\"game_id\": " +
                                         std::to_string(game_id) + "}}";
                send(requesterSocket, notify_msg.c_str(), static_cast<int>(notify_msg.length()), 0);
                send(requesterSocket, "\n", 1, 0);
                std::cout << "Sent REMATCH_DECLINED_NOTIFY to player " << requester_id << std::endl;
            }
        }

        return "{\"messageType\": \"REMATCH_DECLINE_ACK\", \"responseCode\": 200, \"payload\": {"
               "\"game_id\": " +
               std::to_string(game_id) + ", "
                                         "\"status\": \"declined\"}}";
    }

    // Forward logic to Python (AUTH, LOBBY, etc.)
    std::string result = execute_logic_command(request);

    // Network Logic: Intercept successful Lobby and Login actions
    // Check for responseCode: 200 or status: success
    bool isSuccess = (result.find("\"responseCode\": 200") != std::string::npos) ||
                     (result.find("\"responseCode\":200") != std::string::npos) ||
                     (result.find("\"status\": \"success\"") != std::string::npos);

    if (isSuccess)
    {
        std::string resType = get_json_string(result, "messageType");
        if (resType.empty())
            resType = get_json_string(result, "type");

        if (action == "join_lobby" || type == "join_lobby")
        {
            int pid = get_json_int(request, "player_id");
            if (pid == 0)
                pid = get_json_int(result, "player_id");

            if (pid > 0)
            {
                std::lock_guard<std::mutex> lock(session_mutex);
                client_sessions[clientSocket] = pid;
                if (std::find(ready_players.begin(), ready_players.end(), pid) == ready_players.end())
                {
                    ready_players.push_back(pid);
                }
            }
        }
        else if (action == "leave_lobby" || type == "leave_lobby")
        {
            int pid = get_json_int(request, "player_id");
            if (pid > 0)
            {
                std::lock_guard<std::mutex> lock(session_mutex);
                auto it = std::remove(ready_players.begin(), ready_players.end(), pid);
                if (it != ready_players.end())
                {
                    ready_players.erase(it, ready_players.end());
                }
            }
        }
        else if (resType == "AUTH_LOGIN_ACK" || resType == "LOGIN_SUCCESS")
        {
            // user_id is inside payload now
            int pid = get_json_int(result, "user_id");
            if (pid == 0)
                pid = get_json_int(result, "player_id");
            if (pid > 0)
            {
                std::cout << "Player logged in: " << pid << " on socket " << clientSocket << std::endl;
                {
                    std::lock_guard<std::mutex> lock(session_mutex);
                    client_sessions[clientSocket] = pid;
                }

                // Automatically add player to lobby
                std::string join_req = "{\"action\": \"join_lobby\", \"player_id\": " + std::to_string(pid) + "}";
                execute_logic_command(join_req);
                std::cout << "Player " << pid << " added to lobby" << std::endl;
            }
        }
        else if (resType == "MOVE_ACK")
        {
            std::string success_str = get_json_string(result, "success");
            bool is_success = (success_str == "true" || result.find("\"success\": true") != std::string::npos || result.find("\"success\":true") != std::string::npos);

            if (is_success)
            {
                int opponent_id = get_json_int(result, "opponent_id");
                std::string from_pos = get_json_string(result, "from");
                std::string to_pos = get_json_string(result, "to");
                std::string next_fen = get_json_string(result, "next_fen");
                double white_time = get_json_double(result, "white_time");
                double black_time = get_json_double(result, "black_time");

                // Construct MOVE_UPDATE
                // We should ideally extract the whole payload or reconstruct it
                // For now, let's just make a simple update message

                if (opponent_id > 0)
                {
                    std::lock_guard<std::mutex> lock(session_mutex);
                    SOCKET opponentSocket = INVALID_SOCKET;
                    for (auto const &[sock, pid] : client_sessions)
                    {
                        if (pid == opponent_id)
                        {
                            opponentSocket = sock;
                            break;
                        }
                    }

                    if (opponentSocket != INVALID_SOCKET)
                    {
                        // Broadcast MOVE_UPDATE
                        std::string update_msg = "{\"messageType\": \"MOVE_UPDATE\", \"responseCode\": 200, \"payload\": {"
                                                 "\"last_move\": {\"from\": \"" +
                                                 from_pos + "\", \"to\": \"" + to_pos + "\"}, "
                                                                                        "\"fen\": \"" +
                                                 next_fen + "\", "
                                                            "\"white_time\": " +
                                                 std::to_string(white_time) + ", "
                                                                              "\"black_time\": " +
                                                 std::to_string(black_time) + ", "
                                                                              "\"status\": \"update\"}}";
                        send(opponentSocket, update_msg.c_str(), static_cast<int>(update_msg.length()), 0);
                        send(opponentSocket, "\n", 1, 0);
                        std::cout << "Broadcasted MOVE_UPDATE to player " << opponent_id << std::endl;
                    }
                }

                // Check for Game Over (Checkmate/Draw/Timeout)
                std::string game_result = get_json_string(result, "game_result");
                if (game_result == "checkmate" || game_result == "draw" || game_result == "timeout")
                {
                    int white_id = get_json_int(result, "white_id");
                    int black_id = get_json_int(result, "black_id");
                    int new_white_elo = get_json_int(result, "new_white_elo");
                    int new_black_elo = get_json_int(result, "new_black_elo");
                    int winner_id = get_json_int(result, "winner_id");
                    int game_id = get_json_int(request, "game_id");

                    std::cout << "Game Over: " << game_result << " (Winner: " << winner_id << ")" << std::endl;

                    std::lock_guard<std::mutex> lock(session_mutex);
                    for (auto const &[sock, pid] : client_sessions)
                    {
                        if (pid == white_id || pid == black_id)
                        {
                            std::string result_str = "draw";
                            std::string reason_str = game_result;  // "checkmate", "draw", or "timeout"
                            int new_elo = 0;

                            if (pid == white_id)
                                new_elo = new_white_elo;
                            else
                                new_elo = new_black_elo;

                            if (game_result == "checkmate" || game_result == "timeout")
                            {
                                if (pid == winner_id)
                                    result_str = "win";
                                else
                                    result_str = "loss";
                            }

                            std::string end_msg = "{\"messageType\": \"GAME_END\", \"responseCode\": 200, \"payload\": {"
                                                  "\"game_id\": " +
                                                  std::to_string(game_id) + ", "
                                                                            "\"result\": \"" +
                                                  result_str + "\", "
                                                               "\"reason\": \"" +
                                                  reason_str + "\", "
                                                               "\"new_elo\": " +
                                                  std::to_string(new_elo) + "}}";

                            send(sock, end_msg.c_str(), static_cast<int>(end_msg.length()), 0);
                            send(sock, "\n", 1, 0);
                            std::cout << "Sent GAME_END to player " << pid << std::endl;
                        }
                    }
                }
            }
        }
    }

    return result;
}
