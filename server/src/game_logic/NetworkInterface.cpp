#include "NetworkInterface.h"
#include <iostream>
#include <functional>

NetworkInterface::NetworkInterface(int port) : port(port) {
    streamServer = std::make_unique<StreamServer>(
        port, [this](const std::string &request) { return process_request(request); });
}

NetworkInterface::~NetworkInterface() = default;

void NetworkInterface::start() {
    if (!streamServer) {
        std::cerr << "Stream server is not initialized" << std::endl;
        return;
    }

    streamServer->start();
}

std::string NetworkInterface::process_request(const std::string& request) {
    std::cout << "Received: " << request << std::endl;

    std::string escaped_request;
    for (char c : request) {
        if (c == '"') {
            escaped_request += "\\\"";
        } else {
            escaped_request += c;
        }
    }

    std::string command = "python3 logic_wrapper.py \"" + escaped_request + "\"";
#ifdef _WIN32
    command = "python logic_wrapper.py \"" + escaped_request + "\"";
#endif
    
    std::string result = "";
    FILE* pipe = nullptr;

#ifdef _WIN32
    pipe = _popen(command.c_str(), "r");
#else
    pipe = popen(command.c_str(), "r");
#endif

    if (!pipe) {
        return "{\"status\": \"error\", \"message\": \"Failed to open pipe\"}";
    }

    char buffer[128];
    while (fgets(buffer, 128, pipe) != NULL) {
        result += buffer;
    }

#ifdef _WIN32
    _pclose(pipe);
#else
    pclose(pipe);
#endif
    
    size_t first = result.find_first_not_of(" \t\n\r");
    if (first == std::string::npos) {
        result = "";
    } else {
        size_t last = result.find_last_not_of(" \t\n\r");
        result = result.substr(first, (last - first + 1));
    }

    if (result.empty()) {
        return "{\"status\": \"error\", \"message\": \"Empty response from logic\"}";
    }

    return result;
}
