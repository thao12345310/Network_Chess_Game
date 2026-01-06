# Makefile for Chess Client

CXX = g++
CXXFLAGS = -std=c++11 -Wall -Iinclude -fPIC
LDFLAGS = -pthread

# Try to use pkg-config for jsoncpp, fallback to -ljsoncpp
JSONCPP_CFLAGS := $(shell pkg-config --cflags jsoncpp 2>/dev/null)
JSONCPP_LIBS := $(shell pkg-config --libs jsoncpp 2>/dev/null)

ifeq ($(JSONCPP_LIBS),)
	JSONCPP_CFLAGS = -I/usr/include/jsoncpp
	JSONCPP_LIBS = -ljsoncpp
endif

CXXFLAGS += $(JSONCPP_CFLAGS)
LDFLAGS += $(JSONCPP_LIBS)

# Windows specific flags
ifeq ($(OS),Windows_NT)
	LDFLAGS += -lws2_32
	SHARED_EXT = dll
	SHARED_FLAGS = -shared -DBUILD_DLL
	LIB_PREFIX = 
else
	SHARED_EXT = so
	SHARED_FLAGS = -shared -fPIC
	LIB_PREFIX = lib
endif

# Source files
SRCDIR = src
SOURCES = $(SRCDIR)/NetworkClient.cpp $(SRCDIR)/GameClient.cpp $(SRCDIR)/ClientAPI.cpp
MAIN_SOURCE = $(SRCDIR)/main.cpp
OBJECTS = $(SOURCES:.cpp=.o)
MAIN_OBJ = $(MAIN_SOURCE:.cpp=.o)

TARGET = chess_client
SHARED_LIB = $(LIB_PREFIX)chessclient.$(SHARED_EXT)

# Default target - build both executable and shared library
all: $(TARGET) $(SHARED_LIB)

# Build executable
$(TARGET): $(OBJECTS) $(MAIN_OBJ)
	$(CXX) -o $@ $^ $(LDFLAGS)

# Build shared library (for Python integration)
$(SHARED_LIB): $(OBJECTS)
	$(CXX) $(SHARED_FLAGS) -o $@ $^ $(LDFLAGS)

# Compile source files to object files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Clean build files
clean:
	rm -f $(SRCDIR)/*.o $(TARGET) $(TARGET).exe $(SHARED_LIB) *.dll *.so

# Run the client
run: $(TARGET)
	./$(TARGET)

# Install shared library (optional)
install: $(SHARED_LIB)
	@echo "Shared library built: $(SHARED_LIB)"
	@echo "Copy to ../ui/ for Python integration"
	cp $(SHARED_LIB) ../ui/

.PHONY: all clean run install
