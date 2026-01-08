#ifndef LOGIC_UTILS_H
#define LOGIC_UTILS_H

#include <string>
#include <fstream>
#include <cstdlib>
#include <cstdio>
#include <iostream>

// Helper Functions for Python Integration - Inline to be included in multiple files

inline std::string get_python_cmd_prefix() {
    std::string script = "logic_wrapper.py";
    // Check if script exists in current directory
    {
        std::ifstream f(script);
        if (f.good()) {
             return "python3 " + script;
        }
    }
    // Check if script exists in game_logic/ subdirectory
    {
        std::string sub = "game_logic/logic_wrapper.py";
        std::ifstream f(sub);
        if (f.good()) {
             return "python3 " + sub;
        }
    }
    // Check if script exists in src/game_logic/ subdirectory
    {
        std::string sub = "src/game_logic/logic_wrapper.py";
        std::ifstream f(sub);
        if (f.good()) {
             return "python3 " + sub;
        }
    }
    
    // Default fallback
    return "python3 " + script;
}

inline std::string executePythonCommand(const std::string& request) {
    std::string escaped_request;
    for (char c : request) {
        if (c == '"') {
            escaped_request += "\\\"";
        } else {
            escaped_request += c;
        }
    }

    std::string cmd_prefix = get_python_cmd_prefix();
    std::string command = cmd_prefix + " \"" + escaped_request + "\"";
    
    std::string result = "";
    FILE* pipe_stream = popen(command.c_str(), "r");

    if (!pipe_stream) {
        return "{\"status\": \"error\", \"message\": \"Failed to open pipe\"}";
    }

    char buffer[128];
    while (fgets(buffer, 128, pipe_stream) != NULL) {
        result += buffer;
    }

    pclose(pipe_stream);
    
    // Trim whitespace
    size_t first = result.find_first_not_of(" \t\n\r");
    if (first == std::string::npos) {
        result = "";
    } else {
        size_t last = result.find_last_not_of(" \t\n\r");
        result = result.substr(first, (last - first + 1));
    }
    
    if (result.empty()) {
        return "{\"status\": \"error\", \"message\": \"Empty response from logic\"}";
    }

    return result;
}

#endif // LOGIC_UTILS_H
