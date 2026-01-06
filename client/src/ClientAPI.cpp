#include "ClientAPI.h"
#include "GameClient.h"
#include <string>
#include <cstring>
#include <map>
#include <mutex>

// Thread-safe string buffer management
static std::map<ClientHandle, std::string> lastMessages;
static std::map<ClientHandle, std::string> lastUsernames;
static std::map<ClientHandle, std::string> lastGameIds;
static std::mutex bufferMutex;

// Wrapper struct
struct ClientWrapper
{
    GameClient *client;
    CMessageCallback loginCallback;
    CMessageCallback gameUpdateCallback;
    CMessageCallback playerListCallback;
    CMessageCallback challengeCallback;
    CErrorCallback errorCallback;

    ClientWrapper(const std::string &ip, int port)
        : client(new GameClient(ip, port)),
          loginCallback(nullptr),
          gameUpdateCallback(nullptr),
          playerListCallback(nullptr),
          challengeCallback(nullptr),
          errorCallback(nullptr) {}

    ~ClientWrapper()
    {
        delete client;
    }
};

extern "C"
{

    ClientHandle client_create(const char *serverIP, int port)
    {
        try
        {
            ClientWrapper *wrapper = new ClientWrapper(serverIP, port);
            return static_cast<ClientHandle>(wrapper);
        }
        catch (...)
        {
            return nullptr;
        }
    }

    void client_destroy(ClientHandle handle)
    {
        if (!handle)
            return;

        ClientWrapper *wrapper = static_cast<ClientWrapper *>(handle);

        // Clean up buffers
        {
            std::lock_guard<std::mutex> lock(bufferMutex);
            lastMessages.erase(handle);
            lastUsernames.erase(handle);
            lastGameIds.erase(handle);
        }

        delete wrapper;
    }

    int client_connect(ClientHandle handle)
    {
        if (!handle)
            return 0;
        ClientWrapper *wrapper = static_cast<ClientWrapper *>(handle);
        return wrapper->client->connect() ? 1 : 0;
    }

    void client_disconnect(ClientHandle handle)
    {
        if (!handle)
            return;
        ClientWrapper *wrapper = static_cast<ClientWrapper *>(handle);
        wrapper->client->disconnect();
    }

    int client_is_connected(ClientHandle handle)
    {
        if (!handle)
            return 0;
        ClientWrapper *wrapper = static_cast<ClientWrapper *>(handle);
        return wrapper->client->connect() ? 1 : 0; // Check if connected via network client
    }

    void client_set_login_callback(ClientHandle handle, CMessageCallback callback)
    {
        if (!handle)
            return;
        ClientWrapper *wrapper = static_cast<ClientWrapper *>(handle);
        wrapper->loginCallback = callback;

        wrapper->client->setLoginCallback([handle, callback](const Json::Value &msg)
                                          {
        if (callback) {
            Json::StreamWriterBuilder writer;
            writer["indentation"] = "";
            std::string msgStr = Json::writeString(writer, msg);
            callback(msgStr.c_str());
        } });
    }

    void client_set_game_update_callback(ClientHandle handle, CMessageCallback callback)
    {
        if (!handle)
            return;
        ClientWrapper *wrapper = static_cast<ClientWrapper *>(handle);
        wrapper->gameUpdateCallback = callback;

        wrapper->client->setGameUpdateCallback([handle, callback](const Json::Value &msg)
                                               {
        if (callback) {
            Json::StreamWriterBuilder writer;
            writer["indentation"] = "";
            std::string msgStr = Json::writeString(writer, msg);
            callback(msgStr.c_str());
        } });
    }

    void client_set_player_list_callback(ClientHandle handle, CMessageCallback callback)
    {
        if (!handle)
            return;
        ClientWrapper *wrapper = static_cast<ClientWrapper *>(handle);
        wrapper->playerListCallback = callback;

        wrapper->client->setPlayerListCallback([handle, callback](const Json::Value &msg)
                                               {
        if (callback) {
            Json::StreamWriterBuilder writer;
            writer["indentation"] = "";
            std::string msgStr = Json::writeString(writer, msg);
            callback(msgStr.c_str());
        } });
    }

    void client_set_challenge_callback(ClientHandle handle, CMessageCallback callback)
    {
        if (!handle)
            return;
        ClientWrapper *wrapper = static_cast<ClientWrapper *>(handle);
        wrapper->challengeCallback = callback;

        wrapper->client->setChallengeCallback([handle, callback](const Json::Value &msg)
                                              {
        if (callback) {
            Json::StreamWriterBuilder writer;
            writer["indentation"] = "";
            std::string msgStr = Json::writeString(writer, msg);
            callback(msgStr.c_str());
        } });
    }

    void client_set_error_callback(ClientHandle handle, CErrorCallback callback)
    {
        if (!handle)
            return;
        ClientWrapper *wrapper = static_cast<ClientWrapper *>(handle);
        wrapper->errorCallback = callback;

        wrapper->client->setErrorCallback([handle, callback](const std::string &err)
                                          {
        if (callback) {
            callback(err.c_str());
        } });
    }

    int client_login(ClientHandle handle, const char *username, const char *password)
    {
        if (!handle)
            return 0;
        ClientWrapper *wrapper = static_cast<ClientWrapper *>(handle);
        return wrapper->client->login(username, password) ? 1 : 0;
    }

    int client_register(ClientHandle handle, const char *username, const char *password, const char *email)
    {
        if (!handle)
            return 0;
        ClientWrapper *wrapper = static_cast<ClientWrapper *>(handle);
        return wrapper->client->registerAccount(username, password, email ? email : "") ? 1 : 0;
    }

    void client_logout(ClientHandle handle)
    {
        if (!handle)
            return;
        ClientWrapper *wrapper = static_cast<ClientWrapper *>(handle);
        wrapper->client->logout();
    }

    int client_request_player_list(ClientHandle handle)
    {
        if (!handle)
            return 0;
        ClientWrapper *wrapper = static_cast<ClientWrapper *>(handle);
        return wrapper->client->requestPlayerList() ? 1 : 0;
    }

    int client_join_lobby(ClientHandle handle)
    {
        if (!handle)
            return 0;
        ClientWrapper *wrapper = static_cast<ClientWrapper *>(handle);
        return wrapper->client->joinLobby() ? 1 : 0;
    }

    int client_find_match(ClientHandle handle)
    {
        if (!handle)
            return 0;
        // Using sendChallenge as proxy for matchmaking
        return 1; // Stub - implement actual matchmaking
    }

    int client_send_challenge(ClientHandle handle, const char *opponentUsername)
    {
        if (!handle || !opponentUsername)
            return 0;
        ClientWrapper *wrapper = static_cast<ClientWrapper *>(handle);
        return wrapper->client->sendChallenge(opponentUsername) ? 1 : 0;
    }

    int client_accept_challenge(ClientHandle handle, const char *challengerId)
    {
        if (!handle || !challengerId)
            return 0;
        ClientWrapper *wrapper = static_cast<ClientWrapper *>(handle);
        return wrapper->client->acceptChallenge(challengerId) ? 1 : 0;
    }

    int client_send_move(ClientHandle handle, const char *fromPos, const char *toPos)
    {
        if (!handle)
            return 0;
        ClientWrapper *wrapper = static_cast<ClientWrapper *>(handle);
        return wrapper->client->sendMove(fromPos, toPos) ? 1 : 0;
    }

    int client_send_emoji(ClientHandle handle, const char *emoji)
    {
        // Implement if GameClient has emoji support
        return 0;
    }

    int client_resign(ClientHandle handle)
    {
        if (!handle)
            return 0;
        ClientWrapper *wrapper = static_cast<ClientWrapper *>(handle);
        return wrapper->client->resign() ? 1 : 0;
    }

    int client_offer_draw(ClientHandle handle)
    {
        if (!handle)
            return 0;
        ClientWrapper *wrapper = static_cast<ClientWrapper *>(handle);
        return wrapper->client->offerDraw() ? 1 : 0;
    }

    const char *client_get_username(ClientHandle handle)
    {
        if (!handle)
            return "";
        ClientWrapper *wrapper = static_cast<ClientWrapper *>(handle);

        std::lock_guard<std::mutex> lock(bufferMutex);
        lastUsernames[handle] = wrapper->client->getCurrentUsername();
        return lastUsernames[handle].c_str();
    }

    const char *client_get_game_id(ClientHandle handle)
    {
        if (!handle)
            return "";
        ClientWrapper *wrapper = static_cast<ClientWrapper *>(handle);

        std::lock_guard<std::mutex> lock(bufferMutex);
        lastGameIds[handle] = wrapper->client->getCurrentGameId();
        return lastGameIds[handle].c_str();
    }

    void client_set_game_id(ClientHandle handle, const char *gameId)
    {
        if (!handle)
            return;
        ClientWrapper *wrapper = static_cast<ClientWrapper *>(handle);
        wrapper->client->setGameId(gameId);
    }

    int client_has_message(ClientHandle handle)
    {
        if (!handle)
            return 0;
        ClientWrapper *wrapper = static_cast<ClientWrapper *>(handle);
        return wrapper->client->hasMessage() ? 1 : 0;
    }

    const char *client_get_next_message(ClientHandle handle)
    {
        if (!handle)
            return "";
        ClientWrapper *wrapper = static_cast<ClientWrapper *>(handle);

        Json::Value msg = wrapper->client->getNextMessage();
        if (msg.isNull())
            return "";

        std::lock_guard<std::mutex> lock(bufferMutex);
        Json::StreamWriterBuilder writer;
        writer["indentation"] = "";
        lastMessages[handle] = Json::writeString(writer, msg);
        return lastMessages[handle].c_str();
    }

    void client_process_messages(ClientHandle handle)
    {
        if (!handle)
            return;
        // This would be called in a loop to process incoming messages
        // The callbacks will be triggered automatically by GameClient's receive thread
    }

} // extern "C"
