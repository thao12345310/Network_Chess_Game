#include "NetworkClient.h"
#include <iostream>
#include <sstream>
#include <cstring>
#include <errno.h>

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#else
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#endif

NetworkClient::NetworkClient(const std::string &ip, int port)
    : sockfd(-1), serverIP(ip), serverPort(port), connected(false)
{
#ifdef _WIN32
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2, 2), &wsaData);
#endif
}

NetworkClient::~NetworkClient()
{
    disconnect();
}

bool NetworkClient::connectToServer()
{
    // Create socket
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0)
    {
        std::cerr << "Socket creation failed: " << strerror(errno) << std::endl;
        return false;
    }

    // Set socket options (optional but recommended)
    int opt = 1;
    setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, (char *)&opt, sizeof(opt));

    // Set receive timeout
#ifdef _WIN32
    DWORD timeout = 5000; // 5 seconds in milliseconds
    setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, (char *)&timeout, sizeof(timeout));
#else
    struct timeval tv;
    tv.tv_sec = 5;
    tv.tv_usec = 0;
    setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
#endif

    // Server address
    struct sockaddr_in serverAddr;
    memset(&serverAddr, 0, sizeof(serverAddr));
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(serverPort);

    // Convert IP address
    if (inet_pton(AF_INET, serverIP.c_str(), &serverAddr.sin_addr) <= 0)
    {
        std::cerr << "Invalid address: " << serverIP << std::endl;
        closesocket(sockfd);
        sockfd = -1;
        return false;
    }

    // Connect
    if (connect(sockfd, (struct sockaddr *)&serverAddr, sizeof(serverAddr)) < 0)
    {
        std::cerr << "Connection failed: " << strerror(errno) << std::endl;
        closesocket(sockfd);
        sockfd = -1;
        return false;
    }

    connected = true;
    std::cout << "Connected to server " << serverIP << ":" << serverPort << std::endl;
    return true;
}

void NetworkClient::disconnect()
{
    if (sockfd >= 0)
    {
        closesocket(sockfd);
        sockfd = -1;
    }
#ifdef _WIN32
    WSACleanup();
#endif
    connected = false;
    sessionToken.clear();
}

bool NetworkClient::isConnected() const
{
    return connected;
}

bool NetworkClient::sendMessage(const Json::Value &message)
{
    if (!connected)
    {
        std::cerr << "Not connected to server" << std::endl;
        return false;
    }

    // Serialize JSON to string (compact format, single line)
    Json::StreamWriterBuilder writer;
    writer["indentation"] = "";  // Ensure compact format (no pretty printing)
    std::string jsonStr = Json::writeString(writer, message);

    // Add delimiter (newline) for message framing
    jsonStr += "\n";

    return sendRaw(jsonStr);
}

bool NetworkClient::sendRaw(const std::string &data)
{
    size_t totalSent = 0;
    size_t dataLen = data.length();

    while (totalSent < dataLen)
    {
        int sent = send(sockfd, data.c_str() + totalSent,
                        dataLen - totalSent, 0);

        if (sent < 0)
        {
            std::cerr << "Send failed: " << strerror(errno) << std::endl;
            connected = false;
            return false;
        }

        totalSent += sent;
    }

    return true;
}

Json::Value NetworkClient::receiveMessage()
{
    if (!connected)
    {
        return Json::Value();
    }

    std::string data = receiveRaw();
    if (data.empty())
    {
        return Json::Value();
    }

    // Parse JSON
    Json::CharReaderBuilder reader;
    Json::Value message;
    std::string errors;

    std::istringstream iss(data);
    if (!Json::parseFromStream(reader, iss, &message, &errors))
    {
        std::cerr << "JSON parse error: " << errors << std::endl;
        return Json::Value();
    }

    return message;
}

std::string NetworkClient::receiveRaw()
{
    std::string buffer;
    char ch;

    // Read until newline (message delimiter)
    while (true)
    {
        int received = recv(sockfd, &ch, 1, 0);

        if (received < 0)
        {
#ifdef _WIN32
            int err = WSAGetLastError();
            if (err == WSAETIMEDOUT || err == WSAEWOULDBLOCK)
#else
            if (errno == EAGAIN || errno == EWOULDBLOCK)
#endif
            {
                // Timeout - no data available
                break;
            }
            std::cerr << "Receive failed: " << strerror(errno) << std::endl;
            connected = false;
            return "";
        }
        else if (received == 0)
        {
            // Connection closed
            std::cerr << "Server closed connection" << std::endl;
            connected = false;
            return "";
        }

        if (ch == '\n')
        {
            break;
        }

        buffer += ch;
    }

    return buffer;
}

std::string NetworkClient::getSessionToken() const
{
    return sessionToken;
}

void NetworkClient::setSessionToken(const std::string &token)
{
    sessionToken = token;
}