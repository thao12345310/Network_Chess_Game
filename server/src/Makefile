# Makefile for Chess Game Server
# Build from server/src/

# Detect OS
ifeq ($(OS),Windows_NT)
    TARGET = server.exe
    LIBS = -lws2_32
    RM = del /Q
    MKDIR = if not exist
else
    TARGET = server
    LIBS = -pthread
    RM = rm -f
    MKDIR = mkdir -p
endif

# Directories
GAME_LOGIC_DIR = game_logic
BUILD_DIR = build
PROTOCOL_DIR = protocol

# Source files
MAIN_SRC = main.cpp
SERVER_SRC = Server.cpp
SESSION_SRC = ClientSession.cpp
MATCHMAKING_SRC = MatchmakingService.cpp
MESSAGE_HANDLER_SRC = MessageHandler.cpp

# Header include paths
# Ensure nlohmann/json.hpp is available in include path
INCLUDES = -I. -I$(GAME_LOGIC_DIR)

# Compiler flags
CXX = g++
CXXFLAGS = -std=c++14 -Wall -Wextra $(INCLUDES)

# Default target
all: $(TARGET)

# Build executable
$(TARGET): $(MAIN_SRC) $(SERVER_SRC) $(SESSION_SRC) $(MATCHMAKING_SRC) $(MESSAGE_HANDLER_SRC)
	@echo Building server...
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(MAIN_SRC) $(SERVER_SRC) $(SESSION_SRC) $(MATCHMAKING_SRC) $(MESSAGE_HANDLER_SRC) $(LIBS)
	@echo Build complete: $(TARGET)

# Clean build files
clean:
	@echo Cleaning...
	$(RM) $(TARGET) $(TARGET).exe
	@echo Clean complete.

# Run the server
run: $(TARGET)
	@echo Starting server...
	./$(TARGET)

# Help target
help:
	@echo "Available targets:"
	@echo "  all     - Build the server (default)"
	@echo "  clean   - Remove build files"
	@echo "  run     - Build and run the server"
	@echo "  help    - Show this help message"

.PHONY: all clean run help
