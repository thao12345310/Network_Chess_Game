#ifndef MATCHMAKING_SERVICE_H
#define MATCHMAKING_SERVICE_H

#include <string>
#include <vector>
#include <map>
#include <memory>
#include <mutex>

class ClientSession;

class MatchmakingService {
public:
    MatchmakingService();

    void addPlayer(std::shared_ptr<ClientSession> session);
    void removePlayer(std::shared_ptr<ClientSession> session);
    
    std::shared_ptr<ClientSession> getPlayer(const std::string& username);
    std::vector<std::string> getOnlinePlayers() const;

    // Challenge logic
    void processChallenge(std::shared_ptr<ClientSession> from, const std::string& toUser);
    void processChallengeResponse(std::shared_ptr<ClientSession> responder, bool accepted);

private:
    std::map<std::string, std::shared_ptr<ClientSession>> onlinePlayers_;
    std::mutex mutex_;
    
    // Map of responder -> challenger (pending challenges)
    std::map<std::string, std::string> pendingChallenges_;
    
    void createMatch(std::shared_ptr<ClientSession> playerA, std::shared_ptr<ClientSession> playerB);
};

#endif // MATCHMAKING_SERVICE_H
