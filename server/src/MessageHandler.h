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

    void handleLogin(std::shared_ptr<ClientSession> session, const json& j);
    void handleChallenge(std::shared_ptr<ClientSession> session, const json& j);
    void handleChallengeResponse(std::shared_ptr<ClientSession> session, const json& j);
    void handleMove(std::shared_ptr<ClientSession> session, const json& j);
    void handleEmoji(std::shared_ptr<ClientSession> session, const json& j);
    void handleListPlayers(std::shared_ptr<ClientSession> session);
};

#endif // MESSAGE_HANDLER_H
