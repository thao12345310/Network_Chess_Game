#include "NetworkInterface.h"
#include <iostream>
#include <thread>
#include <vector>
#include <sstream>

NetworkInterface::NetworkInterface(int port) : port(port), running(false), server_socket(INVALID_SOCKET) {
#ifdef _WIN32
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2, 2), &wsaData);
#endif
}

NetworkInterface::~NetworkInterface() {
    if (server_socket != INVALID_SOCKET) {
#ifdef _WIN32
        closesocket(server_socket);
        WSACleanup();
#else
        close(server_socket);
#endif
    }
}

void NetworkInterface::start() {
    server_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (server_socket == INVALID_SOCKET) {
        std::cerr << "Failed to create socket" << std::endl;
        return;
    }

    // Allow address reuse
    int opt = 1;
    setsockopt(server_socket, SOL_SOCKET, SO_REUSEADDR, (char*)&opt, sizeof(opt));

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
        
        std::stringstream ss(request);
        std::string line;
        while (std::getline(ss, line)) {
            if (line.empty()) continue;
            if (!line.empty() && line.back() == '\r') line.pop_back();
            
            std::string response = process_request(line);
            send(client_socket, response.c_str(), response.length(), 0);
            send(client_socket, "\n", 1, 0);
        }
    }
#ifdef _WIN32
    closesocket(client_socket);
#else
    close(client_socket);
#endif
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
