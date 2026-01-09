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
        constexpr const char* AUTH_LOGOUT_REQ = "AUTH_LOGOUT_REQ";
        constexpr const char* AUTH_LOGOUT_ACK = "AUTH_LOGOUT_ACK";
        
        // Lobby
        constexpr const char* LOBBY_LIST = "LOBBY_LIST";
        
        // Matchmaking
        constexpr const char* MATCH_FIND_REQ = "MATCH_FIND_REQ";
        constexpr const char* MATCH_CANCEL_REQ = "MATCH_CANCEL_REQ";
        constexpr const char* MATCH_CANCEL_ACK = "MATCH_CANCEL_ACK";
        constexpr const char* MATCH_START = "MATCH_START";
        
        // Gameplay
        constexpr const char* MOVE_REQ = "MOVE_REQ";
        constexpr const char* MOVE_ACK = "MOVE_ACK";
        constexpr const char* MOVE_UPDATE = "MOVE_UPDATE";
        
        // Interaction
        constexpr const char* EMOJI_SEND = "EMOJI_SEND";
        constexpr const char* EMOJI_UPDATE = "EMOJI_UPDATE";
        
        // Game Actions
        constexpr const char* GAME_RESIGN = "GAME_RESIGN";
        constexpr const char* GAME_END = "GAME_END";
        constexpr const char* DRAW_OFFER = "DRAW_OFFER";
        constexpr const char* DRAW_OFFER_ACK = "DRAW_OFFER_ACK";
        constexpr const char* DRAW_OFFER_NOTIFY = "DRAW_OFFER_NOTIFY";
        constexpr const char* DRAW_ACCEPT = "DRAW_ACCEPT";
        constexpr const char* DRAW_DECLINE = "DRAW_DECLINE";
        
        // Rematch
        constexpr const char* REMATCH_REQUEST = "REMATCH_REQUEST";
        constexpr const char* REMATCH_REQUEST_ACK = "REMATCH_REQUEST_ACK";
        constexpr const char* REMATCH_REQUEST_NOTIFY = "REMATCH_REQUEST_NOTIFY";
        constexpr const char* REMATCH_ACCEPT = "REMATCH_ACCEPT";
        constexpr const char* REMATCH_DECLINE = "REMATCH_DECLINE";
        constexpr const char* REMATCH_DECLINED_NOTIFY = "REMATCH_DECLINED_NOTIFY";
        
        // Errors
        constexpr const char* ERROR = "ERROR";

        // Challenge
        constexpr const char* CHALLENGE_REQ = "CHALLENGE_REQ";
        constexpr const char* CHALLENGE_RESP = "CHALLENGE_RESP"; // For accept/decline
        constexpr const char* CHALLENGE_NOTIFY = "CHALLENGE_NOTIFY"; // To target
    }

}

#endif // PROTOCOL_H
