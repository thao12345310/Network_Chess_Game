#ifndef NETWORK_CLIENT_H
#define NETWORK_CLIENT_H

#include <string>
#include <functional>
#include <jsoncpp/json/json.h>

// Socket headers - Windows/Linux compatibility
#ifdef _WIN32
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #pragma comment(lib, "ws2_32.lib")
#else
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <arpa/inet.h>
    #include <unistd.h>
    #define closesocket close
#endif

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

private:
    // Private helper methods
    bool sendRaw(const std::string& data);
    std::string receiveRaw();
};

#endif