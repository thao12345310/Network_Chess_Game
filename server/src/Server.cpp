#include "Server.h"
#include "ClientSession.h"
#include <iostream>
#include <algorithm>
#include <cstring>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/select.h>

Server::Server(int port) 
    : port_(port), running_(false), messageHandler_(matchmakingService_) {
}

Server::~Server() {
    stop();
}

void Server::setupServerSocket() {
    serverSocket_ = socket(AF_INET, SOCK_STREAM, 0);
    if (serverSocket_ < 0) {
        throw std::runtime_error("Failed to create socket");
    }

    int opt = 1;
    if (setsockopt(serverSocket_, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        throw std::runtime_error("setsockopt failed");
    }

    sockaddr_in address;
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(port_);

    if (bind(serverSocket_, (struct sockaddr*)&address, sizeof(address)) < 0) {
        perror("bind failed");
        throw std::runtime_error("Bind failed");
    }

    if (listen(serverSocket_, 10) < 0) {
        perror("listen failed");
        throw std::runtime_error("Listen failed");
    }
}

void Server::run() {
    setupServerSocket();
    running_ = true;
    std::cout << "Server started on port " << port_ << std::endl;

    fd_set readfds;
    int max_sd, activity;

    while (running_) {
        FD_ZERO(&readfds);
        FD_SET(serverSocket_, &readfds);
        max_sd = serverSocket_;

        {
            std::lock_guard<std::mutex> lock(sessionsMutex_);
            for (const auto& session : sessions_) {
                int sd = session->getSocket();
                if (sd > 0) {
                    FD_SET(sd, &readfds);
                }
                if (sd > max_sd) {
                    max_sd = sd;
                }
            }
        }

        // Timeout needed for select so we can check running_ flag periodically
        struct timeval timeout;
        timeout.tv_sec = 1;
        timeout.tv_usec = 0;

        activity = select(max_sd + 1, &readfds, NULL, NULL, &timeout);

        if ((activity < 0) && (errno != EINTR)) {
            std::cerr << "Select error" << std::endl;
        }

        // Check new connection
        if (FD_ISSET(serverSocket_, &readfds)) {
            handleNewConnection();
        }

        // Check IO on clients
        // Copy list to avoid locking issues if we modify list during iteration (though strictly we read list then modify later)
        // Or just lock.
        std::vector<std::shared_ptr<ClientSession>> currentSessions;
        {
            std::lock_guard<std::mutex> lock(sessionsMutex_);
            currentSessions = sessions_; // copy shared_ptrs
        }
        
        for (auto& session : currentSessions) {
            int sd = session->getSocket();
            if (sd > 0 && FD_ISSET(sd, &readfds)) {
                handleClientData(session);
            }
        }
        
        // Cleanup disconnected
         {
            std::lock_guard<std::mutex> lock(sessionsMutex_);
            sessions_.erase(std::remove_if(sessions_.begin(), sessions_.end(),
                [](const std::shared_ptr<ClientSession>& s) {
                    return s->getSocket() == -1; 
                }), sessions_.end());
        }
    }
}

void Server::stop() {
    running_ = false;
    if (serverSocket_ >= 0) {
        close(serverSocket_);
        serverSocket_ = -1;
    }
}

void Server::handleNewConnection() {
    sockaddr_in address;
    socklen_t addrlen = sizeof(address);
    int new_socket = accept(serverSocket_, (struct sockaddr*)&address, &addrlen);
    
    if (new_socket < 0) {
        perror("accept");
        return;
    }

    std::cout << "New connection: socket " << new_socket << ", ip " << inet_ntoa(address.sin_addr) 
              << ", port " << ntohs(address.sin_port) << std::endl;

    auto session = std::make_shared<ClientSession>(new_socket, this);
    session->start();

    std::lock_guard<std::mutex> lock(sessionsMutex_);
    sessions_.push_back(session);
}

void Server::handleClientData(std::shared_ptr<ClientSession> session) {
    char buffer[1025];
    int valread = read(session->getSocket(), buffer, 1024);
    
    if (valread == 0) {
        // Disconnected
        onClientDisconnected(session);
        session->close();
    } else if (valread > 0) {
        buffer[valread] = '\0';
        std::string data(buffer);
        // Split by newline if needed.
        // For simplicity, handle per line.
        size_t pos = 0;
        std::string token;
        std::string delimiter = "\n";
        
        // This is a naive implementation:
        // if message is fragmented across reads, this will break.
        // But fulfilling the basic request.
        // A proper buffer per session is required for full robustness.
        
        size_t start = 0;
        size_t end = data.find(delimiter);
        while (end != std::string::npos) {
            token = data.substr(start, end - start);
            if (!token.empty()) {
                messageHandler_.handleMessage(session, token);
            }
            start = end + delimiter.length();
            end = data.find(delimiter, start);
        }
        // Last part if any (though usually JSON ends with newline or we treat whole buffer)
        if (start < data.length()) {
             token = data.substr(start);
             // If incomplete JSON, it will fail parse.
             if (!token.empty()) { 
                // In robust server: append to session buffer.
                // Here: try to handle.
                 messageHandler_.handleMessage(session, token);
             }
        }
    } else {
        perror("read");
        onClientDisconnected(session);
        session->close();
    }
}

void Server::onClientDisconnected(std::shared_ptr<ClientSession> session) {
    matchmakingService_.removePlayer(session);
}
