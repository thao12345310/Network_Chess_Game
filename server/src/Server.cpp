#include "Server.h"
#include <iostream>

Server::Server(int port) {
    std::cout << "Initializing Server on port " << port << "..." << std::endl;
    networkInterface = std::make_unique<NetworkInterface>(port);
}

Server::~Server() {
    std::cout << "Server shutting down..." << std::endl;
}

void Server::run() {
    std::cout << "Starting Server..." << std::endl;
    if (networkInterface) {
        networkInterface->start();
    }
}
