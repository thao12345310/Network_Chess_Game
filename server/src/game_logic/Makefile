# Linux only
TARGET = server
LIBS = -pthread
RM = rm -f

all: $(TARGET)

$(TARGET): main.cpp NetworkInterface.cpp ../StreamServer.cpp
	g++ -o $(TARGET) main.cpp NetworkInterface.cpp ../StreamServer.cpp -I.. $(LIBS)

clean:
	$(RM) $(TARGET)
