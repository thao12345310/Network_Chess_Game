#ifndef NETWORK_INTERFACE_H
#define NETWORK_INTERFACE_H

#include <string>
#include <winsock2.h>

class NetworkInterface {
public:
    NetworkInterface(int port);
    ~NetworkInterface();
    void start();

private:
    int port;
    SOCKET server_socket;
    bool running;

    void handle_client(SOCKET client_socket);
    std::string process_request(const std::string& request);
};

#endif // NETWORK_INTERFACE_H
