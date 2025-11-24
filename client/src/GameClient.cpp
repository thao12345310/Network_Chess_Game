#include "GameClient.h"
#include <iostream>
#include <chrono>

GameClient::GameClient(const std::string& serverIP, int port) 
    : running(false) {
    netClient = new NetworkClient(serverIP, port);
}

GameClient::~GameClient() {
    disconnect();
    delete netClient;
}

bool GameClient::connect() {
    if (!netClient->connectToServer()) {
        return false;
    }
    
    running = true;
    receiveThread = std::thread(&GameClient::receiveLoop, this);
    return true;
}

void GameClient::disconnect() {
    running = false;
    
    if (receiveThread.joinable()) {
        receiveThread.join();
    }
    
    netClient->disconnect();
}

bool GameClient::login(const std::string& username, const std::string& password) {
    Json::Value msg;
    msg["type"] = "LOGIN";
    msg["username"] = username;
    msg["password"] = password;
    msg["timestamp"] = static_cast<int>(std::time(nullptr));
    
    if (netClient->sendMessage(msg)) {
        currentUsername = username;
        return true;
    }
    return false;
}

bool GameClient::registerAccount(const std::string& username, 
                                 const std::string& password,
                                 const std::string& email) {
    Json::Value msg;
    msg["type"] = "REGISTER";
    msg["username"] = username;
    msg["password"] = password;
    msg["email"] = email;
    msg["timestamp"] = static_cast<int>(std::time(nullptr));
    
    return netClient->sendMessage(msg);
}

void GameClient::logout() {
    Json::Value msg;
    msg["type"] = "LOGOUT";
    msg["session_token"] = netClient->getSessionToken();
    
    netClient->sendMessage(msg);
    currentUsername.clear();
    currentGameId.clear();
}

bool GameClient::requestPlayerList() {
    Json::Value msg;
    msg["type"] = "GET_PLAYER_LIST";
    msg["session_token"] = netClient->getSessionToken();
    
    return netClient->sendMessage(msg);
}

bool GameClient::sendChallenge(const std::string& opponentUsername) {
    Json::Value msg;
    msg["type"] = "SEND_CHALLENGE";
    msg["opponent_username"] = opponentUsername;
    msg["session_token"] = netClient->getSessionToken();
    msg["timestamp"] = static_cast<int>(std::time(nullptr));
    
    return netClient->sendMessage(msg);
}

bool GameClient::acceptChallenge(const std::string& challengeId) {
    Json::Value msg;
    msg["type"] = "ACCEPT_CHALLENGE";
    msg["challenge_id"] = challengeId;
    msg["session_token"] = netClient->getSessionToken();
    
    return netClient->sendMessage(msg);
}

bool GameClient::declineChallenge(const std::string& challengeId) {
    Json::Value msg;
    msg["type"] = "DECLINE_CHALLENGE";
    msg["challenge_id"] = challengeId;
    msg["session_token"] = netClient->getSessionToken();
    
    return netClient->sendMessage(msg);
}

bool GameClient::sendMove(const std::string& fromPos, const std::string& toPos) {
    Json::Value msg;
    msg["type"] = "MOVE";
    msg["game_id"] = currentGameId;
    msg["from"] = fromPos;
    msg["to"] = toPos;
    msg["session_token"] = netClient->getSessionToken();
    msg["timestamp"] = static_cast<int>(std::time(nullptr));
    
    return netClient->sendMessage(msg);
}

bool GameClient::offerDraw() {
    Json::Value msg;
    msg["type"] = "OFFER_DRAW";
    msg["game_id"] = currentGameId;
    msg["session_token"] = netClient->getSessionToken();
    
    return netClient->sendMessage(msg);
}

bool GameClient::acceptDraw() {
    Json::Value msg;
    msg["type"] = "ACCEPT_DRAW";
    msg["game_id"] = currentGameId;
    msg["session_token"] = netClient->getSessionToken();
    
    return netClient->sendMessage(msg);
}

bool GameClient::declineDraw() {
    Json::Value msg;
    msg["type"] = "DECLINE_DRAW";
    msg["game_id"] = currentGameId;
    msg["session_token"] = netClient->getSessionToken();
    
    return netClient->sendMessage(msg);
}

bool GameClient::resign() {
    Json::Value msg;
    msg["type"] = "RESIGN";
    msg["game_id"] = currentGameId;
    msg["session_token"] = netClient->getSessionToken();
    
    return netClient->sendMessage(msg);
}

bool GameClient::requestRematch() {
    Json::Value msg;
    msg["type"] = "REQUEST_REMATCH";
    msg["game_id"] = currentGameId;
    msg["session_token"] = netClient->getSessionToken();
    
    return netClient->sendMessage(msg);
}

bool GameClient::requestMatchHistory() {
    Json::Value msg;
    msg["type"] = "GET_MATCH_HISTORY";
    msg["session_token"] = netClient->getSessionToken();
    
    return netClient->sendMessage(msg);
}

void GameClient::receiveLoop() {
    while (running) {
        Json::Value msg = netClient->receiveMessage();
        
        if (!msg.isNull()) {
            {
                std::lock_guard<std::mutex> lock(queueMutex);
                messageQueue.push(msg);
            }
            
            // Process with callbacks immediately
            processMessage(msg);
        }
        
        // Small sleep to prevent busy waiting
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
}

void GameClient::processMessage(const Json::Value& msg) {
    if (!msg.isMember("type")) {
        return;
    }
    
    std::string type = msg["type"].asString();
    
    // Handle session token
    if (msg.isMember("session_token")) {
        netClient->setSessionToken(msg["session_token"].asString());
    }
    
    // Handle game_id
    if (msg.isMember("game_id")) {
        currentGameId = msg["game_id"].asString();
    }
    
    // Route to appropriate callback
    if (type == "LOGIN_SUCCESS" || type == "LOGIN_FAILED" || 
        type == "REGISTER_SUCCESS" || type == "REGISTER_FAILED") {
        if (onLoginResponse) {
            onLoginResponse(msg);
        }
    } 
    else if (type == "GAME_UPDATE" || type == "GAME_START" || 
             type == "GAME_END" || type == "MOVE_RESULT") {
        if (onGameUpdate) {
            onGameUpdate(msg);
        }
    } 
    else if (type == "CHALLENGE_RECEIVED" || type == "CHALLENGE_ACCEPTED" || 
             type == "CHALLENGE_DECLINED") {
        if (onChallengeReceived) {
            onChallengeReceived(msg);
        }
    } 
    else if (type == "PLAYER_LIST") {
        if (onPlayerListUpdate) {
            onPlayerListUpdate(msg);
        }
    } 
    else if (type == "ERROR") {
        if (onError) {
            std::string errorMsg = msg.isMember("message") ? 
                msg["message"].asString() : "Unknown error";
            onError(errorMsg);
        }
    }
}

void GameClient::setGameUpdateCallback(MessageCallback cb) {
    onGameUpdate = cb;
}

void GameClient::setChallengeCallback(MessageCallback cb) {
    onChallengeReceived = cb;
}

void GameClient::setPlayerListCallback(MessageCallback cb) {
    onPlayerListUpdate = cb;
}

void GameClient::setLoginCallback(MessageCallback cb) {
    onLoginResponse = cb;
}

void GameClient::setErrorCallback(ErrorCallback cb) {
    onError = cb;
}

bool GameClient::hasMessage() {
    std::lock_guard<std::mutex> lock(queueMutex);
    return !messageQueue.empty();
}

Json::Value GameClient::getNextMessage() {
    std::lock_guard<std::mutex> lock(queueMutex);
    if (messageQueue.empty()) {
        return Json::Value();
    }
    
    Json::Value msg = messageQueue.front();
    messageQueue.pop();
    return msg;
}

std::string GameClient::getCurrentUsername() const {
    return currentUsername;
}

std::string GameClient::getCurrentGameId() const {
    return currentGameId;
}

// =====================================

// client/main.cpp (Test program)
#include "GameClient.h"
#include <iostream>
#include <thread>
#include <chrono>

void printMenu() {
    std::cout << "\n=== Chess Client Menu ===" << std::endl;
    std::cout << "1. Login" << std::endl;
    std::cout << "2. Register" << std::endl;
    std::cout << "3. Get player list" << std::endl;
    std::cout << "4. Send challenge" << std::endl;
    std::cout << "5. Make move (e.g., e2 e4)" << std::endl;
    std::cout << "6. Resign" << std::endl;
    std::cout << "7. Offer draw" << std::endl;
    std::cout << "8. Get match history" << std::endl;
    std::cout << "9. Logout" << std::endl;
    std::cout << "0. Quit" << std::endl;
    std::cout << "Choice: ";
}

int main() {
    GameClient client("127.0.0.1", 8080);
    
    // Setup callbacks
    client.setLoginCallback([](const Json::Value& msg) {
        std::cout << "\n[LOGIN] " << msg.toStyledString() << std::endl;
    });
    
    client.setGameUpdateCallback([](const Json::Value& msg) {
        std::cout << "\n[GAME UPDATE] " << msg.toStyledString() << std::endl;
    });
    
    client.setChallengeCallback([](const Json::Value& msg) {
        std::cout << "\n[CHALLENGE] " << msg.toStyledString() << std::endl;
    });
    
    client.setPlayerListCallback([](const Json::Value& msg) {
        std::cout << "\n[PLAYERS] " << msg.toStyledString() << std::endl;
    });
    
    client.setErrorCallback([](const std::string& err) {
        std::cerr << "\n[ERROR] " << err << std::endl;
    });
    
    // Connect
    std::cout << "Connecting to server..." << std::endl;
    if (!client.connect()) {
        std::cerr << "Failed to connect!" << std::endl;
        return 1;
    }
    
    std::cout << "Connected successfully!" << std::endl;
    
    // Main loop
    int choice;
    while (true) {
        printMenu();
        std::cin >> choice;
        
        if (choice == 0) {
            break;
        }
        
        switch (choice) {
            case 1: {
                std::string username, password;
                std::cout << "Username: ";
                std::cin >> username;
                std::cout << "Password: ";
                std::cin >> password;
                client.login(username, password);
                break;
            }
            case 2: {
                std::string username, password, email;
                std::cout << "Username: ";
                std::cin >> username;
                std::cout << "Password: ";
                std::cin >> password;
                std::cout << "Email: ";
                std::cin >> email;
                client.registerAccount(username, password, email);
                break;
            }
            case 3:
                client.requestPlayerList();
                break;
            case 4: {
                std::string opponent;
                std::cout << "Opponent username: ";
                std::cin >> opponent;
                client.sendChallenge(opponent);
                break;
            }
            case 5: {
                std::string from, to;
                std::cout << "From position (e.g., e2): ";
                std::cin >> from;
                std::cout << "To position (e.g., e4): ";
                std::cin >> to;
                client.sendMove(from, to);
                break;
            }
            case 6:
                client.resign();
                break;
            case 7:
                client.offerDraw();
                break;
            case 8:
                client.requestMatchHistory();
                break;
            case 9:
                client.logout();
                break;
            default:
                std::cout << "Invalid choice!" << std::endl;
        }
        
        // Give time for response
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    
    client.disconnect();
    std::cout << "Disconnected. Goodbye!" << std::endl;
    
    return 0;
}