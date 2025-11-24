#ifndef NETWORK_INTERFACE_H
#define NETWORK_INTERFACE_H

#include <string>

#ifdef _WIN32
    #include <winsock2.h>
    #pragma comment(lib, "ws2_32.lib")
#else
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <unistd.h>
    #include <arpa/inet.h>
    #define SOCKET int
    #define INVALID_SOCKET -1
    #define SOCKET_ERROR -1
#endif

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
