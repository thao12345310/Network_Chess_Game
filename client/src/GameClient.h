#ifndef GAME_CLIENT_H
#define GAME_CLIENT_H

#include "NetworkClient.h"
#include <queue>
#include <mutex>
#include <thread>
#include <functional>
#include <atomic>
#include <jsoncpp/json/json.h>   // THÊM DÒNG NÀY

using MessageCallback = std::function<void(const Json::Value&)>;
using ErrorCallback = std::function<void(const std::string&)>;

class GameClient {
private:
    NetworkClient* netClient;
    std::thread receiveThread;
    std::queue<Json::Value> messageQueue;
    std::mutex queueMutex;
    std::atomic<bool> running;
    
    std::string currentUsername;
    std::string currentGameId;
    
    // Callbacks
    MessageCallback onGameUpdate;
    MessageCallback onChallengeReceived;
    MessageCallback onPlayerListUpdate;
    MessageCallback onLoginResponse;
    ErrorCallback onError;
    
    void receiveLoop();
    void processMessage(const Json::Value& msg);
    
public:
    GameClient(const std::string& serverIP, int port);
    ~GameClient();
    
    bool connect();
    void disconnect();
    
    // Authentication
    bool login(const std::string& username, const std::string& password);
    bool registerAccount(const std::string& username, const std::string& password, 
                        const std::string& email = "");
    void logout();
    
    // Player list & matchmaking
    bool requestPlayerList();
    bool sendChallenge(const std::string& opponentUsername);
    bool acceptChallenge(const std::string& challengeId);
    bool declineChallenge(const std::string& challengeId);
    
    // Game actions
    bool sendMove(const std::string& fromPos, const std::string& toPos);
    bool offerDraw();
    bool acceptDraw();
    bool declineDraw();
    bool resign();
    bool requestRematch();
    
    // Match history
    bool requestMatchHistory();
    
    // Callbacks
    void setGameUpdateCallback(MessageCallback cb);
    void setChallengeCallback(MessageCallback cb);
    void setPlayerListCallback(MessageCallback cb);
    void setLoginCallback(MessageCallback cb);
    void setErrorCallback(ErrorCallback cb);
    
    // Utility
    Json::Value getNextMessage();
    bool hasMessage();
    std::string getCurrentUsername() const;
    std::string getCurrentGameId() const;
};

#endif