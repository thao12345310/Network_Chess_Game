# Makefile for Chess Game Server
# Build từ thư mục server/

# Detect OS
ifeq ($(OS),Windows_NT)
    TARGET = server.exe
    LIBS = -lws2_32
    RM = del /Q
else
    TARGET = server
    LIBS = -pthread
    RM = rm -f
endif

# Directories
SRC_DIR = src
GAME_LOGIC_DIR = $(SRC_DIR)/game_logic
BUILD_DIR = build

# Source files
MAIN_SRC = $(GAME_LOGIC_DIR)/main.cpp
NETWORK_INTERFACE_SRC = $(GAME_LOGIC_DIR)/NetworkInterface.cpp
STREAM_SERVER_SRC = $(SRC_DIR)/StreamServer.cpp

# Header include paths
INCLUDES = -I$(SRC_DIR) -I$(GAME_LOGIC_DIR)

# Compiler flags
CXX = g++
CXXFLAGS = -std=c++14 -Wall -Wextra $(INCLUDES)

# Default target
all: $(TARGET)

# Build executable
$(TARGET): $(MAIN_SRC) $(NETWORK_INTERFACE_SRC) $(STREAM_SERVER_SRC)
	@echo Building server from server/ directory...
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(MAIN_SRC) $(NETWORK_INTERFACE_SRC) $(STREAM_SERVER_SRC) $(LIBS)
	@echo Build complete: $(TARGET)

# Clean build files
clean:
	@echo Cleaning...
	$(RM) $(TARGET) $(TARGET).exe
ifeq ($(OS),Windows_NT)
	if exist $(BUILD_DIR) rmdir /S /Q $(BUILD_DIR)
else
	rm -rf $(BUILD_DIR)
endif
	@echo Clean complete.

# Run the server
run: $(TARGET)
	@echo Starting server...
ifeq ($(OS),Windows_NT)
	.\$(TARGET)
else
	./$(TARGET)
endif

# Help target
help:
	@echo "Available targets:"
	@echo "  all     - Build the server (default)"
	@echo "  clean   - Remove build files"
	@echo "  run     - Build and run the server"
	@echo "  help    - Show this help message"
	@echo ""
	@echo "Build from: server/ directory"

.PHONY: all clean run help

