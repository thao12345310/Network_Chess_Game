# Makefile for Chess Game Server
# Build từ thư mục server/src/

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

# Source files
MAIN_SRC = $(GAME_LOGIC_DIR)/main.cpp
NETWORK_INTERFACE_SRC = $(GAME_LOGIC_DIR)/NetworkInterface.cpp
STREAM_SERVER_SRC = StreamServer.cpp

# Header include paths
INCLUDES = -I. -I$(GAME_LOGIC_DIR)

# Object files (optional, for incremental builds)
MAIN_OBJ = $(BUILD_DIR)/main.o
NETWORK_INTERFACE_OBJ = $(BUILD_DIR)/NetworkInterface.o
STREAM_SERVER_OBJ = $(BUILD_DIR)/StreamServer.o

# Compiler flags
CXX = g++
CXXFLAGS = -std=c++14 -Wall -Wextra $(INCLUDES)

# Default target
all: $(TARGET)

# Build executable
$(TARGET): $(MAIN_SRC) $(NETWORK_INTERFACE_SRC) $(STREAM_SERVER_SRC)
	@echo Building server...
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
	./$(TARGET)

# Help target
help:
	@echo "Available targets:"
	@echo "  all     - Build the server (default)"
	@echo "  clean   - Remove build files"
	@echo "  run     - Build and run the server"
	@echo "  help    - Show this help message"

.PHONY: all clean run help

