#include "MessageHandler.h"
#include "ClientSession.h"
#include "MatchmakingService.h"
#include <iostream>

MessageHandler::MessageHandler(MatchmakingService& matchmakingService) 
    : matchmakingService_(matchmakingService) {}

void MessageHandler::handleMessage(std::shared_ptr<ClientSession> session, const std::string& message) {
    try {
        json j = json::parse(message);
        std::string type = j.value("type", "unknown");
        
        std::cout << "Received message type: " << type << " from " << (session->isAuthorized() ? session->getUsername() : "anon") << std::endl;

        if (type == "login") {
            handleLogin(session, j);
        } else if (!session->isAuthorized()) {
            // Must login first
            json err;
            err["type"] = "error";
            err["message"] = "Authentication required";
            session->send(err.dump());
        } else if (type == "challenge") {
            handleChallenge(session, j);
        } else if (type == "challenge_response") {
            handleChallengeResponse(session, j);
        } else if (type == "move") {
            handleMove(session, j);
        } else if (type == "emoji") {
            handleEmoji(session, j);
        } else if (type == "list_players") {
            handleListPlayers(session);
        } else {
            std::cout << "Unknown message type: " << type << std::endl;
        }
    } catch (const json::parse_error& e) {
        std::cerr << "JSON parse error: " << e.what() << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "Error handling message: " << e.what() << std::endl;
    }
}

void MessageHandler::handleLogin(std::shared_ptr<ClientSession> session, const json& j) {
    std::string username = j.value("username", "");
    if (username.empty()) {
        return; 
    }
    // Simple "authentication" by setting username
    // Check if taken? For now just allow.
    session->setUsername(username);
    matchmakingService_.addPlayer(session);
    
    json response;
    response["type"] = "login_success";
    response["username"] = username;
    session->send(response.dump());
}

void MessageHandler::handleChallenge(std::shared_ptr<ClientSession> session, const json& j) {
    std::string targetUser = j.value("to", "");
    if (!targetUser.empty()) {
        matchmakingService_.processChallenge(session, targetUser);
    }
}

void MessageHandler::handleChallengeResponse(std::shared_ptr<ClientSession> session, const json& j) {
    bool accepted = j.value("accepted", false);
    matchmakingService_.processChallengeResponse(session, accepted);
}

void MessageHandler::handleMove(std::shared_ptr<ClientSession> session, const json& j) {
    auto opponent = session->getOpponent();
    if (opponent) {
        // Forward the move exactly as received
        // Check formatting? "data" usually.
        // The prompt says: { "type": "move", "from": "playerA", "data": "e2e4" }
        // We ensure "from" is correct.
        json forward = j;
        forward["from"] = session->getUsername(); // Ensure sender is correct
        opponent->send(forward.dump());
    }
}

void MessageHandler::handleEmoji(std::shared_ptr<ClientSession> session, const json& j) {
    auto opponent = session->getOpponent();
    if (opponent) {
        json forward = j;
        forward["from"] = session->getUsername();
        opponent->send(forward.dump());
    }
}

void MessageHandler::handleListPlayers(std::shared_ptr<ClientSession> session) {
    std::vector<std::string> players = matchmakingService_.getOnlinePlayers();
    json response;
    response["type"] = "player_list";
    response["players"] = players;
    session->send(response.dump());
}
