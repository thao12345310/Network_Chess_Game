#include "NetworkClient.h"
#include <iostream>
#include <cstring>
#include <errno.h>

NetworkClient::NetworkClient(const std::string& ip, int port) 
    : sockfd(-1), serverIP(ip), serverPort(port), connected(false) {
}

NetworkClient::~NetworkClient() {
    disconnect();
}

bool NetworkClient::connectToServer() {
    // Create socket
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        std::cerr << "Socket creation failed: " << strerror(errno) << std::endl;
        return false;
    }
    
    // Set socket options (optional but recommended)
    int opt = 1;
    setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    
    // Set receive timeout
    struct timeval tv;
    tv.tv_sec = 5;  // 5 seconds timeout
    tv.tv_usec = 0;
    setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
    
    // Server address
    struct sockaddr_in serverAddr;
    memset(&serverAddr, 0, sizeof(serverAddr));
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(serverPort);
    
    // Convert IP address
    if (inet_pton(AF_INET, serverIP.c_str(), &serverAddr.sin_addr) <= 0) {
        std::cerr << "Invalid address: " << serverIP << std::endl;
        close(sockfd);
        sockfd = -1;
        return false;
    }
    
    // Connect
    if (connect(sockfd, (struct sockaddr*)&serverAddr, sizeof(serverAddr)) < 0) {
        std::cerr << "Connection failed: " << strerror(errno) << std::endl;
        close(sockfd);
        sockfd = -1;
        return false;
    }
    
    connected = true;
    std::cout << "Connected to server " << serverIP << ":" << serverPort << std::endl;
    return true;
}

void NetworkClient::disconnect() {
    if (sockfd >= 0) {
        close(sockfd);
        sockfd = -1;
    }
    connected = false;
    sessionToken.clear();
}

bool NetworkClient::isConnected() const {
    return connected;
}

bool NetworkClient::sendMessage(const Json::Value& message) {
    if (!connected) {
        std::cerr << "Not connected to server" << std::endl;
        return false;
    }
    
    // Serialize JSON to string
    Json::StreamWriterBuilder writer;
    std::string jsonStr = Json::writeString(writer, message);
    
    // Add delimiter (newline) for message framing
    jsonStr += "\n";
    
    return sendRaw(jsonStr);
}

bool NetworkClient::sendRaw(const std::string& data) {
    size_t totalSent = 0;
    size_t dataLen = data.length();
    
    while (totalSent < dataLen) {
        ssize_t sent = send(sockfd, data.c_str() + totalSent, 
                           dataLen - totalSent, 0);
        
        if (sent < 0) {
            std::cerr << "Send failed: " << strerror(errno) << std::endl;
            connected = false;
            return false;
        }
        
        totalSent += sent;
    }
    
    return true;
}

Json::Value NetworkClient::receiveMessage() {
    if (!connected) {
        return Json::Value();
    }
    
    std::string data = receiveRaw();
    if (data.empty()) {
        return Json::Value();
    }
    
    // Parse JSON
    Json::CharReaderBuilder reader;
    Json::Value message;
    std::string errors;
    
    std::istringstream iss(data);
    if (!Json::parseFromStream(reader, iss, &message, &errors)) {
        std::cerr << "JSON parse error: " << errors << std::endl;
        return Json::Value();
    }
    
    return message;
}

std::string NetworkClient::receiveRaw() {
    std::string buffer;
    char ch;
    
    // Read until newline (message delimiter)
    while (true) {
        ssize_t received = recv(sockfd, &ch, 1, 0);
        
        if (received < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                // Timeout - no data available
                break;
            }
            std::cerr << "Receive failed: " << strerror(errno) << std::endl;
            connected = false;
            return "";
        } else if (received == 0) {
            // Connection closed
            std::cerr << "Server closed connection" << std::endl;
            connected = false;
            return "";
        }
        
        if (ch == '\n') {
            break;
        }
        
        buffer += ch;
    }
    
    return buffer;
}

std::string NetworkClient::getSessionToken() const {
    return sessionToken;
}

void NetworkClient::setSessionToken(const std::string& token) {
    sessionToken = token;
}