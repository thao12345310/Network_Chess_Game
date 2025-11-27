#ifndef NETWORK_INTERFACE_H
#define NETWORK_INTERFACE_H

#include <memory>
#include <string>

#include "StreamServer.h"

class NetworkInterface {
public:
    NetworkInterface(int port);
    ~NetworkInterface();
    void start();

private:
    int port;
    std::unique_ptr<StreamServer> streamServer;

    std::string process_request(const std::string& request);
};

#endif // NETWORK_INTERFACE_H
