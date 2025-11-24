# Makefile for Chess Client

CXX = g++
CXXFLAGS = -std=c++11 -Wall -Iinclude
LDFLAGS = -ljsoncpp -pthread

# Windows specific flags
ifeq ($(OS),Windows_NT)
	LDFLAGS += -lws2_32
else
	# Linux/WSL specific - pthread already added above
endif

# Source files
SRCDIR = src
SOURCES = $(wildcard $(SRCDIR)/*.cpp)
OBJECTS = $(SOURCES:.cpp=.o)
TARGET = chess_client

# Default target
all: $(TARGET)

# Link object files to create executable
$(TARGET): $(OBJECTS)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS)

# Compile source files to object files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Clean build files
clean:
	rm -f $(SRCDIR)/*.o $(TARGET) $(TARGET).exe

# Run the client
run: $(TARGET)
	./$(TARGET)

.PHONY: all clean run
