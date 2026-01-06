#ifndef PROTOCOL_H
#define PROTOCOL_H

#include <string>

namespace Protocol {

    // Response Codes
    namespace ResponseCode {
        constexpr int SUCCESS = 200;
        constexpr int CREATED = 201;
        constexpr int BAD_REQUEST = 400;
        constexpr int UNAUTHORIZED = 401;
        constexpr int FORBIDDEN = 403;
        constexpr int NOT_FOUND = 404;
        constexpr int CONFLICT = 409;
        constexpr int SERVER_ERROR = 500;
    }

    // Message Types
    namespace MessageType {
        // Auth
        constexpr const char* AUTH_REGISTER_REQ = "AUTH_REGISTER_REQ";
        constexpr const char* AUTH_REGISTER_ACK = "AUTH_REGISTER_ACK";
        constexpr const char* AUTH_LOGIN_REQ = "AUTH_LOGIN_REQ";
        constexpr const char* AUTH_LOGIN_ACK = "AUTH_LOGIN_ACK";
        
        // Lobby
        constexpr const char* LOBBY_LIST = "LOBBY_LIST";
        
        // Matchmaking
        constexpr const char* MATCH_FIND_REQ = "MATCH_FIND_REQ";
        constexpr const char* MATCH_START = "MATCH_START";
        
        // Gameplay
        constexpr const char* MOVE_REQ = "MOVE_REQ";
        constexpr const char* MOVE_ACK = "MOVE_ACK";
        constexpr const char* MOVE_UPDATE = "MOVE_UPDATE";
        
        // Interaction
        constexpr const char* EMOJI_SEND = "EMOJI_SEND";
        constexpr const char* EMOJI_UPDATE = "EMOJI_UPDATE";
        
        // Errors
        constexpr const char* ERROR = "ERROR";
    }

}

#endif // PROTOCOL_H
