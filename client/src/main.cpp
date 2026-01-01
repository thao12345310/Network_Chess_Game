#include "GameClient.h"
#include <iostream>
#include <thread>
#include <chrono>

void printMenu() {
    std::cout << "\n=== Chess Client Menu ===" << std::endl;
    std::cout << "1. Login" << std::endl;
    std::cout << "2. Register" << std::endl;
    std::cout << "3. Get player list" << std::endl;
    std::cout << "4. Send challenge" << std::endl;
    std::cout << "5. Make move (e.g., e2 e4)" << std::endl;
    std::cout << "6. Resign" << std::endl;
    std::cout << "7. Offer draw" << std::endl;
    std::cout << "8. Get match history" << std::endl;
    std::cout << "9. Logout" << std::endl;
    std::cout << "10. Join Lobby (Must do to appear in list)" << std::endl;
    std::cout << "0. Quit" << std::endl;
    std::cout << "Choice: ";
}

int main() {
    GameClient client("127.0.0.1", 5001);  // Game logic server port
    
    // Setup callbacks
    client.setLoginCallback([](const Json::Value& msg) {
        std::cout << "\n[LOGIN] " << msg.toStyledString() << std::endl;
    });
    
    client.setGameUpdateCallback([](const Json::Value& msg) {
        std::cout << "\n[GAME UPDATE] " << msg.toStyledString() << std::endl;
    });
    
    client.setChallengeCallback([](const Json::Value& msg) {
        std::cout << "\n[CHALLENGE] " << msg.toStyledString() << std::endl;
    });
    
    client.setPlayerListCallback([](const Json::Value& msg) {
        std::cout << "\n[PLAYERS] " << msg.toStyledString() << std::endl;
    });
    
    client.setErrorCallback([](const std::string& err) {
        std::cerr << "\n[ERROR] " << err << std::endl;
    });
    
    // Connect
    std::cout << "Connecting to server..." << std::endl;
    if (!client.connect()) {
        std::cerr << "Failed to connect!" << std::endl;
        return 1;
    }
    
    std::cout << "Connected successfully!" << std::endl;
    
    // Main loop
    int choice;
    while (true) {
        printMenu();
        std::cin >> choice;
        
        if (choice == 0) {
            break;
        }
        
        switch (choice) {
            case 1: {
                std::string username, password;
                std::cout << "Username: ";
                std::cin >> username;
                std::cout << "Password: ";
                std::cin >> password;
                client.login(username, password);
                break;
            }
            case 2: {
                std::string username, password, email;
                std::cout << "Username: ";
                std::cin >> username;
                std::cout << "Password: ";
                std::cin >> password;
                std::cout << "Email: ";
                std::cin >> email;
                client.registerAccount(username, password, email);
                break;
            }
            case 3:
                client.requestPlayerList();
                break;
            case 4: {
                std::string opponent;
                std::cout << "Opponent username: ";
                std::cin >> opponent;
                client.sendChallenge(opponent);
                break;
            }
            case 5: {
                // Check if game_id is set
                if (client.getCurrentGameId().empty()) {
                    std::string gameId;
                    std::cout << "No game_id set. Enter game_id (or create game first): ";
                    std::cin >> gameId;
                    if (!gameId.empty()) {
                        client.setGameId(gameId);
                    } else {
                        std::cout << "Cannot make move without game_id!" << std::endl;
                        break;
                    }
                }
                
                std::string from, to;
                std::cout << "From position (e.g., e2): ";
                std::cin >> from;
                std::cout << "To position (e.g., e4): ";
                std::cin >> to;
                client.sendMove(from, to);
                break;
            }
            case 6:
                client.resign();
                break;
            case 7:
                client.offerDraw();
                break;
            case 8:
                client.requestMatchHistory();
                break;
            case 9:
                client.logout();
                break;
            case 10:
                client.joinLobby();
                std::cout << "Request sent to join lobby..." << std::endl;
                break;
            default:
                std::cout << "Invalid choice!" << std::endl;
        }
        
        // Give time for response
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    
    client.disconnect();
    std::cout << "Disconnected. Goodbye!" << std::endl;
    
    return 0;
}