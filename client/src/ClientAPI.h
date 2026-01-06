#ifndef CLIENT_API_H
#define CLIENT_API_H

#ifdef __cplusplus
extern "C" {
#endif

// Opaque handle for client instance
typedef void* ClientHandle;

// Callback types (C API - using different names to avoid C++ conflicts)
typedef void (*CMessageCallback)(const char* jsonMessage);
typedef void (*CErrorCallback)(const char* errorMessage);

// Client lifecycle
ClientHandle client_create(const char* serverIP, int port);
void client_destroy(ClientHandle handle);

// Connection management
int client_connect(ClientHandle handle);
void client_disconnect(ClientHandle handle);
int client_is_connected(ClientHandle handle);

// Callback registration
void client_set_login_callback(ClientHandle handle, CMessageCallback callback);
void client_set_game_update_callback(ClientHandle handle, CMessageCallback callback);
void client_set_player_list_callback(ClientHandle handle, CMessageCallback callback);
void client_set_challenge_callback(ClientHandle handle, CMessageCallback callback);
void client_set_error_callback(ClientHandle handle, CErrorCallback callback);

// Authentication
int client_login(ClientHandle handle, const char* username, const char* password);
int client_register(ClientHandle handle, const char* username, const char* password, const char* email);
void client_logout(ClientHandle handle);

// Lobby operations
int client_request_player_list(ClientHandle handle);
int client_join_lobby(ClientHandle handle);
int client_find_match(ClientHandle handle);

// Challenge operations
int client_send_challenge(ClientHandle handle, const char* opponentUsername);
int client_accept_challenge(ClientHandle handle, const char* challengerId);

// Game operations
int client_send_move(ClientHandle handle, const char* fromPos, const char* toPos);
int client_send_emoji(ClientHandle handle, const char* emoji);
int client_resign(ClientHandle handle);
int client_offer_draw(ClientHandle handle);

// State accessors
const char* client_get_username(ClientHandle handle);
const char* client_get_game_id(ClientHandle handle);
void client_set_game_id(ClientHandle handle, const char* gameId);

// Message processing
int client_has_message(ClientHandle handle);
const char* client_get_next_message(ClientHandle handle);
void client_process_messages(ClientHandle handle);

#ifdef __cplusplus
}
#endif

#endif // CLIENT_API_H
