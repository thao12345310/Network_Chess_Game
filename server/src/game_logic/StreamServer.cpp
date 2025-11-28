#include "StreamServer.h"

#include <iostream>
#include <sstream>
#include <thread>

StreamServer::StreamServer(int port, MessageHandler handler)
    : port(port), handler(std::move(handler)), serverSocket(INVALID_SOCKET), running(false) {
#ifdef _WIN32
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        std::cerr << "WSAStartup failed" << std::endl;
    }
#endif
}

StreamServer::~StreamServer() {
    stop();
#ifdef _WIN32
    WSACleanup();
#endif
}

void StreamServer::stop() {
    running = false;
    if (serverSocket != INVALID_SOCKET) {
#ifdef _WIN32
        closesocket(serverSocket);
#else
        close(serverSocket);
#endif
        serverSocket = INVALID_SOCKET;
    }
}

void StreamServer::start() {
    serverSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (serverSocket == INVALID_SOCKET) {
        std::cerr << "Failed to create socket" << std::endl;
        return;
    }

    int opt = 1;
    setsockopt(serverSocket, SOL_SOCKET, SO_REUSEADDR, reinterpret_cast<char *>(&opt), sizeof(opt));

    sockaddr_in serverAddr{};
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = inet_addr("127.0.0.1");
    serverAddr.sin_port = htons(port);

    if (bind(serverSocket, reinterpret_cast<sockaddr *>(&serverAddr), sizeof(serverAddr)) == SOCKET_ERROR) {
        std::cerr << "Bind failed" << std::endl;
        stop();
        return;
    }

    if (listen(serverSocket, 5) == SOCKET_ERROR) {
        std::cerr << "Listen failed" << std::endl;
        stop();
        return;
    }

    running = true;
    std::cout << "Stream server listening on 127.0.0.1:" << port << std::endl;

    while (running) {
        SOCKET clientSocket = accept(serverSocket, nullptr, nullptr);
        if (!running) {
            break;
        }

        if (clientSocket == INVALID_SOCKET) {
            std::cerr << "Accept failed" << std::endl;
            continue;
        }

        std::thread clientThread(&StreamServer::handleClient, this, clientSocket);
        clientThread.detach();
    }

    stop();
}

void StreamServer::handleClient(SOCKET clientSocket) {
    std::string messageBuffer;
    char buffer[4096];
    
    while (true) {
        int bytesReceived = recv(clientSocket, buffer, sizeof(buffer) - 1, 0);
        if (bytesReceived <= 0) {
            break;
        }

        buffer[bytesReceived] = '\0';
        messageBuffer += std::string(buffer, bytesReceived);

        // Process complete messages (lines ending with \n)
        size_t pos;
        while ((pos = messageBuffer.find('\n')) != std::string::npos) {
            std::string line = messageBuffer.substr(0, pos);
            messageBuffer.erase(0, pos + 1);

            // Remove \r if present (Windows line ending)
            if (!line.empty() && line.back() == '\r') {
                line.pop_back();
            }

            if (line.empty()) {
                continue;
            }

            std::string response = handler ? handler(line) : "";
            if (response.empty()) {
                response = "{\"status\": \"error\", \"message\": \"Empty response\"}";
            }
            send(clientSocket, response.c_str(), static_cast<int>(response.length()), 0);
            send(clientSocket, "\n", 1, 0);
        }
    }

#ifdef _WIN32
    closesocket(clientSocket);
#else
    close(clientSocket);
#endif
}

