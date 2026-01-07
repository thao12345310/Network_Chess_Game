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
    msg["messageType"] = "AUTH_LOGIN_REQ";
    msg["payload"]["username"] = username;
    msg["payload"]["password"] = password;

    if (netClient->sendMessage(msg))
    {
        currentUsername = username;
        return true;
    }
    return false;
}

bool GameClient::registerAccount(const std::string &username,
                                 const std::string &password)
{
    Json::Value msg;
    msg["messageType"] = "AUTH_REGISTER_REQ";
    msg["payload"]["username"] = username;
    msg["payload"]["password"] = password;

    return netClient->sendMessage(msg);
}

void GameClient::logout()
{
    Json::Value msg;
    msg["messageType"] = "AUTH_LOGOUT_REQ";
    msg["payload"] = Json::Value(Json::objectValue);

    netClient->sendMessage(msg);
    currentUsername.clear();
    currentGameId.clear();
}

bool GameClient::requestPlayerList()
{
    Json::Value msg;
    msg["messageType"] = "LOBBY_LIST";
    msg["payload"] = Json::Value(Json::objectValue);

    return netClient->sendMessage(msg);
}

bool GameClient::joinLobby()
{
    Json::Value msg;
    msg["messageType"] = "MATCH_FIND_REQ";
    msg["payload"]["mode"] = "random";

    return netClient->sendMessage(msg);
}

bool GameClient::sendChallenge(const std::string &opponentUsername)
{
    Json::Value msg;
    msg["messageType"] = "CHALLENGE_REQ";
    msg["payload"]["opponent_username"] = opponentUsername;

    return netClient->sendMessage(msg);
}

bool GameClient::acceptChallenge(const std::string &challengeId)
{
    Json::Value msg;
    msg["messageType"] = "CHALLENGE_RESP";
    // Send challenger_id as an integer - the server expects this field
    try {
        int challengerIdInt = std::stoi(challengeId);
        msg["payload"]["challenger_id"] = challengerIdInt;
    } catch (...) {
        // Fallback to string if conversion fails
        msg["payload"]["challenger_id"] = challengeId;
    }
    msg["payload"]["accepted"] = true;

    return netClient->sendMessage(msg);
}

bool GameClient::declineChallenge(const std::string &challengeId)
{
    Json::Value msg;
    msg["messageType"] = "CHALLENGE_RESP";
    // Send challenger_id as an integer - the server expects this field
    try {
        int challengerIdInt = std::stoi(challengeId);
        msg["payload"]["challenger_id"] = challengerIdInt;
    } catch (...) {
        // Fallback to string if conversion fails
        msg["payload"]["challenger_id"] = challengeId;
    }
    msg["payload"]["accepted"] = false;

    return netClient->sendMessage(msg);
}

bool GameClient::sendMove(const std::string &fromPos, const std::string &toPos)
{
    Json::Value msg;
    msg["messageType"] = "MOVE_REQ";
    try {
        msg["payload"]["game_id"] = std::stoi(currentGameId);
    } catch (...) {
        msg["payload"]["game_id"] = 0;
    }
    msg["payload"]["from"] = fromPos;
    msg["payload"]["to"] = toPos;
    // msg["payload"]["promotion"] = Json::Value::null;

    return netClient->sendMessage(msg);
}

bool GameClient::offerDraw()
{
    // NOTE: This message type is not in server protocol yet
    Json::Value msg;
    msg["messageType"] = "DRAW_OFFER";
    msg["payload"]["game_id"] = currentGameId;

    return netClient->sendMessage(msg);
}

bool GameClient::acceptDraw()
{
    // NOTE: This message type is not in server protocol yet
    Json::Value msg;
    msg["messageType"] = "DRAW_ACCEPT";
    msg["payload"]["game_id"] = currentGameId;

    return netClient->sendMessage(msg);
}

bool GameClient::declineDraw()
{
    // NOTE: This message type is not in server protocol yet
    Json::Value msg;
    msg["messageType"] = "DRAW_DECLINE";
    msg["payload"]["game_id"] = currentGameId;

    return netClient->sendMessage(msg);
}

bool GameClient::resign()
{
    // NOTE: This message type is not in server protocol yet
    Json::Value msg;
    msg["messageType"] = "GAME_RESIGN";
    msg["payload"]["game_id"] = currentGameId;

    return netClient->sendMessage(msg);
}

bool GameClient::requestRematch()
{
    // NOTE: This message type is not in server protocol yet
    Json::Value msg;
    msg["messageType"] = "MATCH_REMATCH_REQ";
    msg["payload"]["game_id"] = currentGameId;

    return netClient->sendMessage(msg);
}

bool GameClient::requestMatchHistory()
{
    // NOTE: This message type is not in server protocol yet
    Json::Value msg;
    msg["messageType"] = "MATCH_HISTORY_REQ";
    msg["payload"] = Json::Value(Json::objectValue);

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
    // Server uses "messageType" instead of "type"
    if (!msg.isMember("messageType"))
    {
        return;
    }

    std::string type = msg["messageType"].asString();

    // Handle payload data
    Json::Value payload = msg.isMember("payload") ? msg["payload"] : Json::Value();

    // Handle game_id from payload
    if (payload.isMember("game_id"))
    {
        currentGameId = std::to_string(payload["game_id"].asInt());
    }

    if (payload.isMember("user_id"))
    {
        currentPlayerId = payload["user_id"].asInt();
    }

    // Route to appropriate callback
    if (type == "AUTH_LOGIN_ACK" || type == "AUTH_REGISTER_ACK")
    {
        if (onLoginResponse)
        {
            onLoginResponse(msg);
        }
    }
    else if (type == "MOVE_UPDATE" || type == "MOVE_ACK" ||
             type == "MATCH_START" || type == "GAME_END")
    {
        if (onGameUpdate)
        {
            onGameUpdate(msg);
        }
    }
    else if (type == "LOBBY_LIST")
    {
        if (onPlayerListUpdate)
        {
            onPlayerListUpdate(msg);
        }
    }
    else if (type == "CHALLENGE_NOTIFY")
    {
        if (onChallengeReceived)
        {
            onChallengeReceived(msg);
        }
    }
    else if (type == "CHALLENGE_RESP")
    {
        // Maybe trigger game update or just log?
        // Usually UI updates status
        if (onGameUpdate)
        {
            onGameUpdate(msg);
        }
    }
    else if (type == "ERROR")
    {
        if (onError)
        {
            std::string errorMsg = payload.isMember("reason") ? payload["reason"].asString() : "Unknown error";
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

void GameClient::setGameId(const std::string &gameId)
{
    currentGameId = gameId;
}

// =====================================

// client/main.cpp (Test program)
