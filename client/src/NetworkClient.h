#ifndef NETWORK_CLIENT_H
#define NETWORK_CLIENT_H

#include <string>
#include <functional>
#include <json/json.h> // hoặc nlohmann/json

class NetworkClient {
private:
    int sockfd;
    std::string serverIP;
    int serverPort;
    bool connected;
    std::string sessionToken;
    
public:
    NetworkClient(const std::string& ip, int port);
    ~NetworkClient();
    
    // Connection
    bool connectToServer();
    void disconnect();
    bool isConnected() const;
    
    // Send/Receive
    bool sendMessage(const Json::Value& message);
    Json::Value receiveMessage();
    
    // Helper
    std::string getSessionToken() const;
    void setSessionToken(const std::string& token);
};

#endif