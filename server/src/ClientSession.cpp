#include "ClientSession.h"
#include "Server.h"
#include <iostream>
#include <unistd.h>
#include <sys/socket.h>
#include <cstring>

ClientSession::ClientSession(int socketV, Server* server) 
    : socket_(socketV), server_(server) {
}

ClientSession::~ClientSession() {
    close();
}

void ClientSession::start() {
    // any initialization
}

void ClientSession::send(const std::string& message) {
    std::lock_guard<std::mutex> lock(sessionMutex_);
    if (socket_ < 0) return;

    // Append newline if not present for delineation, if we decide on NDJSON
    // But let's just send what is requested.
    // Ideally we send size prefix or use a delimiter. 
    // I'll append a newline to ensure the receiver can separate messages.
    std::string data = message + "\n";
    
    ssize_t sent = ::send(socket_, data.c_str(), data.length(), 0);
    if (sent < 0) {
        std::cerr << "Failed to send data to client " << socket_ << std::endl;
        // potentially close session
    }
}

void ClientSession::close() {
    std::lock_guard<std::mutex> lock(sessionMutex_);
    if (socket_ >= 0) {
        ::close(socket_);
        socket_ = -1;
        std::cout << "Session closed for " << (username_.empty() ? "unknown" : username_) << std::endl;
    }
}

void ClientSession::setOpponent(std::shared_ptr<ClientSession> opponent) {
    opponent_ = opponent;
}

std::shared_ptr<ClientSession> ClientSession::getOpponent() const {
    return opponent_.lock();
}

void ClientSession::clearOpponent() {
    opponent_.reset();
}
