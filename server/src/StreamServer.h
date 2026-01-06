#ifndef STREAM_SERVER_H
#define STREAM_SERVER_H

#include <functional>
#include <string>

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
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

class StreamServer {
public:
    using MessageHandler = std::function<std::string(SOCKET, const std::string &)>;
    using OnConnectionClosed = std::function<void(SOCKET)>;

    StreamServer(int port, MessageHandler handler);
    ~StreamServer();

    void start();
    void stop();
    void setOnConnectionClosed(OnConnectionClosed callback);

private:
    void handleClient(SOCKET clientSocket);

    int port;
    MessageHandler handler;
    OnConnectionClosed onConnectionClosed;
    SOCKET serverSocket;
    bool running;
};

#endif // STREAM_SERVER_H

