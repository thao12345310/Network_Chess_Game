#include "NetworkInterface.h"
#include <iostream>

int main() {
    // Start Server
    // Python logic handles DB initialization now
    NetworkInterface server(5001);
    server.start();

    return 0;
}
