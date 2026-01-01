#ifndef CLIENT_SESSION_H
#define CLIENT_SESSION_H

#include <string>
#include <memory>
#include <vector>
#include <mutex>

class Server;
class MessageHandler;

class ClientSession : public std::enable_shared_from_this<ClientSession> {
public:
    ClientSession(int socketV, Server* server);
    ~ClientSession();

    void start();
    void send(const std::string& message);
    void close();

    int getSocket() const { return socket_; }
    std::string getUsername() const { return username_; }
    void setUsername(const std::string& name) { username_ = name; }
    
    bool isAuthorized() const { return !username_.empty(); }

    void setOpponent(std::shared_ptr<ClientSession> opponent);
    std::shared_ptr<ClientSession> getOpponent() const;
    void clearOpponent();

private:
    int socket_;
    Server* server_;
    std::string username_;
    std::weak_ptr<ClientSession> opponent_;
    
    // In a real async server, we would have read buffers here.
    // For this implementation, the Server loop might handle reading, 
    // or this class handles it if we use threads.
    // Given the requirements "Multiple clients (use select, poll, or multithreading)",
    // I will implement a read method that can be called by the Server when data is available.
    
    std::mutex sessionMutex_;
};

#endif // CLIENT_SESSION_H
