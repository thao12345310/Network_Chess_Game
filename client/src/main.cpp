#include "GameClient.h"
#include <iostream>

int main()
{
    GameClient client("127.0.0.1", 8080);

    // Set callbacks
    client.setGameUpdateCallback([](const Json::Value &msg)
                                 { std::cout << "Game update: " << msg.toStyledString() << std::endl; });

    client.setErrorCallback([](const std::string &err)
                            { std::cerr << "Error: " << err << std::endl; });

    // Connect and login
    if (client.connect())
    {
        std::cout << "Connected to server!" << std::endl;

        if (client.login("player1", "password123"))
        {
            std::cout << "Logged in successfully!" << std::endl;

            // Test commands
            std::string cmd;
            while (std::cin >> cmd)
            {
                if (cmd == "move")
                {
                    std::string move;
                    std::cin >> move;
                    client.sendMove(move);
                }
                else if (cmd == "resign")
                {
                    client.resign();
                }
                else if (cmd == "quit")
                {
                    break;
                }
            }
        }
    }

    client.disconnect();
    return 0;
}