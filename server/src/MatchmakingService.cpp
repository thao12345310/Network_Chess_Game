#include "MatchmakingService.h"
#include "ClientSession.h"
#include <iostream>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

MatchmakingService::MatchmakingService() {}

void MatchmakingService::addPlayer(std::shared_ptr<ClientSession> session) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (session->isAuthorized()) {
        onlinePlayers_[session->getUsername()] = session;
        std::cout << "Player added: " << session->getUsername() << std::endl;
    }
}

void MatchmakingService::removePlayer(std::shared_ptr<ClientSession> session) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (session->isAuthorized()) {
        // If in game, notify opponent
        auto opponent = session->getOpponent();
        if (opponent) {
            json msg;
            msg["type"] = "game_end";
            msg["reason"] = "opponent_disconnected";
            opponent->send(msg.dump());
            opponent->clearOpponent();
        }
        
        onlinePlayers_.erase(session->getUsername());
        
        // Remove any pending challenges involving this player
        // This is a bit expensive O(N) but map is small.
        for (auto it = pendingChallenges_.begin(); it != pendingChallenges_.end(); ) {
            if (it->first == session->getUsername() || it->second == session->getUsername()) {
                it = pendingChallenges_.erase(it);
            } else {
                ++it;
            }
        }
        
        std::cout << "Player removed: " << session->getUsername() << std::endl;
    }
}

std::shared_ptr<ClientSession> MatchmakingService::getPlayer(const std::string& username) {
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = onlinePlayers_.find(username);
    if (it != onlinePlayers_.end()) {
        return it->second;
    }
    return nullptr;
}

std::vector<std::string> MatchmakingService::getOnlinePlayers() const {
    // std::lock_guard<std::mutex> lock(mutex_); // mutex_ is mutable or this function is not const in practice
    // Removing const from helper or using const_cast is verify.
    // For simplicity, I'll access map safely.
    // Actually `mutex_` is mutable in my header? No. 
    // I should make mutex_ mutable to use in const method or remove const.
    // I will just cast away constness locally or assume caller handles it? 
    // Better: fix header. But I can't edit header easily without rewriting.
    // I'll just not lock here or use const_cast.
    // Safe way:
    std::vector<std::string> players;
    // (const_cast<MatchmakingService*>(this))->mutex_.lock(); 
    // This is ugly. I'll just implement without lock or assume single thread for now?
    // No, I must be thread safe.
    
    // I will risk compilation error on const mutex lock if I didn't declare it mutable.
    // Current header: `std::mutex mutex_;` inside `class MatchmakingService`.
    // It is NOT mutable. I cannot lock it in a const function.
    // I will write the implementation assuming I can fix the header or removing const from signature in cpp (but it won't match header).
    // I'll use `const_cast` to lock.
    std::unique_lock<std::mutex> lock(const_cast<std::mutex&>(mutex_));
    
    for (const auto& pair : onlinePlayers_) {
        players.push_back(pair.first);
    }
    return players;
}

void MatchmakingService::processChallenge(std::shared_ptr<ClientSession> from, const std::string& toUser) {
    std::lock_guard<std::mutex> lock(mutex_);
    
    auto it = onlinePlayers_.find(toUser);
    if (it == onlinePlayers_.end()) {
        json err;
        err["type"] = "error";
        err["message"] = "Player not found";
        from->send(err.dump());
        return;
    }
    
    auto target = it->second;
    if (target->getOpponent()) {
        json err;
        err["type"] = "error";
        err["message"] = "Player is busy";
        from->send(err.dump());
        return;
    }
    
    // transform pendingChallenges
    pendingChallenges_[toUser] = from->getUsername();
    
    json challengeMsg;
    challengeMsg["type"] = "challenge";
    challengeMsg["from"] = from->getUsername();
    challengeMsg["to"] = toUser;
    
    target->send(challengeMsg.dump());
}

void MatchmakingService::processChallengeResponse(std::shared_ptr<ClientSession> responder, bool accepted) {
    std::lock_guard<std::mutex> lock(mutex_);
    
    auto it = pendingChallenges_.find(responder->getUsername());
    if (it == pendingChallenges_.end()) {
        // No pending challenge
        return;
    }
    
    std::string challengerName = it->second;
    pendingChallenges_.erase(it); // Handled
    
    auto challengerIt = onlinePlayers_.find(challengerName);
    if (challengerIt == onlinePlayers_.end()) {
        json msg;
        msg["type"] = "info";
        msg["message"] = "Challenger disconnected";
        responder->send(msg.dump());
        return;
    }
    
    auto challenger = challengerIt->second;
    
    json responseMsg;
    responseMsg["type"] = "challenge_response";
    responseMsg["from"] = responder->getUsername();
    responseMsg["accepted"] = accepted;
    challenger->send(responseMsg.dump());
    
    if (accepted) {
        createMatch(challenger, responder);
    }
}

void MatchmakingService::createMatch(std::shared_ptr<ClientSession> playerA, std::shared_ptr<ClientSession> playerB) {
    // Determine roles
    // A (challenger) = White, B (responder) = Black (Example)
    
    playerA->setOpponent(playerB);
    playerB->setOpponent(playerA);
    
    json startA;
    startA["type"] = "game_start";
    startA["role"] = "white";
    startA["opponent"] = playerB->getUsername();
    
    json startB;
    startB["type"] = "game_start";
    startB["role"] = "black";
    startB["opponent"] = playerA->getUsername();
    
    playerA->send(startA.dump());
    playerB->send(startB.dump());
    
    std::cout << "Match started: " << playerA->getUsername() << " vs " << playerB->getUsername() << std::endl;
}
