#include "NetworkInterface.h"
#include <iostream>
#include <thread>
#include <vector>
#include <sstream>

#pragma comment(lib, "ws2_32.lib")

NetworkInterface::NetworkInterface(int port) : port(port), running(false), server_socket(INVALID_SOCKET) {
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2, 2), &wsaData);
}

NetworkInterface::~NetworkInterface() {
    if (server_socket != INVALID_SOCKET) {
        closesocket(server_socket);
    }
    WSACleanup();
}

void NetworkInterface::start() {
    server_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (server_socket == INVALID_SOCKET) {
        std::cerr << "Failed to create socket" << std::endl;
        return;
    }

    sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    server_addr.sin_port = htons(port);

    if (bind(server_socket, (sockaddr*)&server_addr, sizeof(server_addr)) == SOCKET_ERROR) {
        std::cerr << "Bind failed" << std::endl;
        return;
    }

    if (listen(server_socket, 5) == SOCKET_ERROR) {
        std::cerr << "Listen failed" << std::endl;
        return;
    }

    running = true;
    std::cout << "Game Logic Server listening on 127.0.0.1:" << port << std::endl;

    while (running) {
        SOCKET client_socket = accept(server_socket, NULL, NULL);
        if (client_socket == INVALID_SOCKET) {
            std::cerr << "Accept failed" << std::endl;
            continue;
        }
        
        std::thread client_thread(&NetworkInterface::handle_client, this, client_socket);
        client_thread.detach();
    }
}

void NetworkInterface::handle_client(SOCKET client_socket) {
    char buffer[4096];
    while (true) {
        int bytes_received = recv(client_socket, buffer, sizeof(buffer) - 1, 0);
        if (bytes_received <= 0) break;

        buffer[bytes_received] = '\0';
        std::string request(buffer);
        
        // Handle multiple commands in one buffer if necessary, 
        // but for now assume one command per recv or simple newline split
        std::stringstream ss(request);
        std::string line;
        while (std::getline(ss, line)) {
            if (line.empty()) continue;
            // Remove \r if present (Windows)
            if (!line.empty() && line.back() == '\r') line.pop_back();
            
            std::string response = process_request(line);
            int sent = send(client_socket, response.c_str(), response.length(), 0);
            send(client_socket, "\n", 1, 0);
        }
    }
    closesocket(client_socket);
}

std::string NetworkInterface::process_request(const std::string& request) {
    std::cout << "Received: " << request << std::endl;

    // Escape double quotes in JSON for command line
    std::string escaped_request;
    for (char c : request) {
        if (c == '"') {
            escaped_request += "\\\"";
        } else {
            escaped_request += c;
        }
    }

    std::string command = "python logic_wrapper.py \"" + escaped_request + "\"";
    
    std::string result = "";
    FILE* pipe = _popen(command.c_str(), "r");
    if (!pipe) {
        return "{\"status\": \"error\", \"message\": \"Failed to open pipe\"}";
    }

    char buffer[128];
    while (fgets(buffer, 128, pipe) != NULL) {
        result += buffer;
    }
    _pclose(pipe);
    
    // Trim whitespace/newlines from result
    size_t first = result.find_first_not_of(" \t\n\r");
    if (first == std::string::npos) {
        result = "";
    } else {
        size_t last = result.find_last_not_of(" \t\n\r");
        result = result.substr(first, (last - first + 1));
    }

    // If result is empty, something went wrong
    if (result.empty()) {
        return "{\"status\": \"error\", \"message\": \"Empty response from logic\"}";
    }

    return result;
}
