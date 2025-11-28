# Detect OS
ifeq ($(OS),Windows_NT)
    TARGET = server.exe
    LIBS = -lws2_32
    RM = del
else
    TARGET = server
    LIBS = -pthread
    RM = rm -f
endif

all: $(TARGET)

$(TARGET): main.cpp NetworkInterface.cpp ../StreamServer.cpp
	g++ -o $(TARGET) main.cpp NetworkInterface.cpp ../StreamServer.cpp -I.. $(LIBS)

clean:
	$(RM) $(TARGET)
