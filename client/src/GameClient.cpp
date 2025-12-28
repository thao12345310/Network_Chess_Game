#include "GameClient.h"
#include <iostream>
#include <chrono>
#include <ctime>               // để dùng std::time
#include <jsoncpp/json/json.h> // an toàn nếu chưa có

GameClient::GameClient(const std::string &serverIP, int port)
    : running(false)
{
    netClient = new NetworkClient(serverIP, port);
}

GameClient::~GameClient()
{
    disconnect();
    delete netClient;
}

bool GameClient::connect()
{
    if (!netClient->connectToServer())
    {
        return false;
    }

    running = true;
    receiveThread = std::thread(&GameClient::receiveLoop, this);
    return true;
}

void GameClient::disconnect()
{
    running = false;

    if (receiveThread.joinable())
    {
        receiveThread.join();
    }

    netClient->disconnect();
}

bool GameClient::login(const std::string &username, const std::string &password)
{
    Json::Value msg;
    msg["type"] = "LOGIN";
    msg["username"] = username;
    msg["password"] = password;
    // msg["timestamp"] = static_cast<int>(std::time(nullptr));

    if (netClient->sendMessage(msg))
    {
        currentUsername = username;
        return true;
    }
    return false;
}

bool GameClient::registerAccount(const std::string &username,
                                 const std::string &password,
                                 const std::string &email)
{
    Json::Value msg;
    msg["type"] = "REGISTER";
    msg["username"] = username;
    msg["password"] = password;
    msg["email"] = email;
    // msg["timestamp"] = static_cast<int>(std::time(nullptr));

    return netClient->sendMessage(msg);
}

void GameClient::logout()
{
    Json::Value msg;
    msg["type"] = "LOGOUT";
    msg["session_token"] = netClient->getSessionToken();

    netClient->sendMessage(msg);
    currentUsername.clear();
    currentGameId.clear();
}

bool GameClient::requestPlayerList()
{
    Json::Value msg;
    msg["type"] = "GET_PLAYER_LIST";
    // msg["session_token"] = netClient->getSessionToken();

    return netClient->sendMessage(msg);
}

bool GameClient::sendChallenge(const std::string &opponentUsername)
{
    Json::Value msg;
    msg["type"] = "SEND_CHALLENGE";
    msg["opponent_username"] = opponentUsername;
    // msg["session_token"] = netClient->getSessionToken();
    // msg["timestamp"] = static_cast<int>(std::time(nullptr));

    return netClient->sendMessage(msg);
}

bool GameClient::acceptChallenge(const std::string &challengeId)
{
    Json::Value msg;
    msg["type"] = "ACCEPT_CHALLENGE";
    msg["challenge_id"] = challengeId;
    //msg["session_token"] = netClient->getSessionToken();

    return netClient->sendMessage(msg);
}

bool GameClient::declineChallenge(const std::string &challengeId)
{
    Json::Value msg;
    msg["type"] = "DECLINE_CHALLENGE";
    msg["challenge_id"] = challengeId;
    //msg["session_token"] = netClient->getSessionToken();

    return netClient->sendMessage(msg);
}

bool GameClient::sendMove(const std::string &fromPos, const std::string &toPos)
{
    Json::Value msg;
    msg["type"] = "MOVE";
    msg["game_id"] = currentGameId;
    msg["from"] = fromPos;
    msg["to"] = toPos;
    // msg["session_token"] = netClient->getSessionToken();
    // msg["timestamp"] = static_cast<int>(std::time(nullptr));

    return netClient->sendMessage(msg);
}

bool GameClient::offerDraw()
{
    Json::Value msg;
    msg["type"] = "OFFER_DRAW";
    msg["game_id"] = currentGameId;
    //msg["session_token"] = netClient->getSessionToken();

    return netClient->sendMessage(msg);
}

bool GameClient::acceptDraw()
{
    Json::Value msg;
    msg["type"] = "ACCEPT_DRAW";
    msg["game_id"] = currentGameId;
    msg["session_token"] = netClient->getSessionToken();

    return netClient->sendMessage(msg);
}

bool GameClient::declineDraw()
{
    Json::Value msg;
    msg["type"] = "DECLINE_DRAW";
    msg["game_id"] = currentGameId;
    msg["session_token"] = netClient->getSessionToken();

    return netClient->sendMessage(msg);
}

bool GameClient::resign()
{
    Json::Value msg;
    msg["type"] = "RESIGN";
    msg["game_id"] = currentGameId;
    msg["session_token"] = netClient->getSessionToken();

    return netClient->sendMessage(msg);
}

bool GameClient::requestRematch()
{
    Json::Value msg;
    msg["type"] = "REQUEST_REMATCH";
    msg["game_id"] = currentGameId;
    msg["session_token"] = netClient->getSessionToken();

    return netClient->sendMessage(msg);
}

bool GameClient::requestMatchHistory()
{
    Json::Value msg;
    msg["type"] = "GET_MATCH_HISTORY";
    msg["session_token"] = netClient->getSessionToken();

    return netClient->sendMessage(msg);
}

void GameClient::receiveLoop()
{
    while (running)
    {
        Json::Value msg = netClient->receiveMessage();

        if (!msg.isNull())
        {
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

void GameClient::processMessage(const Json::Value &msg)
{
    if (!msg.isMember("type"))
    {
        return;
    }

    std::string type = msg["type"].asString();

    // Handle session token
    if (msg.isMember("session_token"))
    {
        netClient->setSessionToken(msg["session_token"].asString());
    }

    // Handle game_id
    if (msg.isMember("game_id"))
    {
        currentGameId = msg["game_id"].asString();
    }

    // Route to appropriate callback
    if (type == "LOGIN_SUCCESS" || type == "LOGIN_FAILED" ||
        type == "REGISTER_SUCCESS" || type == "REGISTER_FAILED")
    {
        if (onLoginResponse)
        {
            onLoginResponse(msg);
        }
    }
    else if (type == "GAME_UPDATE" || type == "GAME_START" ||
             type == "GAME_END" || type == "MOVE_RESULT")
    {
        if (onGameUpdate)
        {
            onGameUpdate(msg);
        }
    }
    else if (type == "CHALLENGE_RECEIVED" || type == "CHALLENGE_ACCEPTED" ||
             type == "CHALLENGE_DECLINED")
    {
        if (onChallengeReceived)
        {
            onChallengeReceived(msg);
        }
    }
    else if (type == "PLAYER_LIST")
    {
        if (onPlayerListUpdate)
        {
            onPlayerListUpdate(msg);
        }
    }
    else if (type == "ERROR")
    {
        if (onError)
        {
            std::string errorMsg = msg.isMember("message") ? msg["message"].asString() : "Unknown error";
            onError(errorMsg);
        }
    }
}

void GameClient::setGameUpdateCallback(MessageCallback cb)
{
    onGameUpdate = cb;
}

void GameClient::setChallengeCallback(MessageCallback cb)
{
    onChallengeReceived = cb;
}

void GameClient::setPlayerListCallback(MessageCallback cb)
{
    onPlayerListUpdate = cb;
}

void GameClient::setLoginCallback(MessageCallback cb)
{
    onLoginResponse = cb;
}

void GameClient::setErrorCallback(ErrorCallback cb)
{
    onError = cb;
}

bool GameClient::hasMessage()
{
    std::lock_guard<std::mutex> lock(queueMutex);
    return !messageQueue.empty();
}

Json::Value GameClient::getNextMessage()
{
    std::lock_guard<std::mutex> lock(queueMutex);
    if (messageQueue.empty())
    {
        return Json::Value();
    }

    Json::Value msg = messageQueue.front();
    messageQueue.pop();
    return msg;
}

std::string GameClient::getCurrentUsername() const
{
    return currentUsername;
}

std::string GameClient::getCurrentGameId() const
{
    return currentGameId;
}

void GameClient::setGameId(const std::string& gameId)
{
    currentGameId = gameId;
}

// =====================================

// client/main.cpp (Test program)
