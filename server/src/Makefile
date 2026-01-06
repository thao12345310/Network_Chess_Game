# Compiler settings
CXX = g++
CXXFLAGS = -std=c++17 -Wall -I. -Igame_logic

# OS specific settings
ifeq ($(OS),Windows_NT)
    TARGET = server.exe
    LIBS = -lws2_32
    RM = del /Q
else
    TARGET = server
    LIBS = -pthread
    RM = rm -f
endif

# Source files for the Game Logic Server (NetworkInterface)
# Using game_logic/main.cpp as the entry point
SRCS = main.cpp game_logic/NetworkInterface.cpp StreamServer.cpp

# Default target
all: $(TARGET)

$(TARGET): $(SRCS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SRCS) $(LIBS)

clean:
	$(RM) $(TARGET)
