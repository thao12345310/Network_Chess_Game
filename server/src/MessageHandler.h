#ifndef MESSAGE_HANDLER_H
#define MESSAGE_HANDLER_H

#include <string>
#include <functional>
#include <map>
#include <nlohmann/json.hpp>

class ClientSession;
class MatchmakingService;

using json = nlohmann::json;

class MessageHandler {
public:
    MessageHandler(MatchmakingService& matchmakingService);
    
    void handleMessage(std::shared_ptr<ClientSession> session, const std::string& message);

private:
    MatchmakingService& matchmakingService_;

    void handleRegister(std::shared_ptr<ClientSession> session, const json& j);
    void handleLogin(std::shared_ptr<ClientSession> session, const json& j);
    // Remove old handleChallenge (replaced by matchmaking)
    // void handleChallenge(std::shared_ptr<ClientSession> session, const json& j);
    // void handleChallengeResponse(std::shared_ptr<ClientSession> session, const json& j);
    
    void handleMatchFind(std::shared_ptr<ClientSession> session, const json& j);
    
    void handleMove(std::shared_ptr<ClientSession> session, const json& j);
    void handleEmoji(std::shared_ptr<ClientSession> session, const json& j);
    void handleListPlayers(std::shared_ptr<ClientSession> session);

    // Protocol Helpers
    std::string buildResponse(const std::string& messageType, int responseCode, const json& payload);
    void sendError(std::shared_ptr<ClientSession> session, int code, const std::string& reason);
};

#endif // MESSAGE_HANDLER_H
