all: server

server: main.cpp NetworkInterface.cpp
	g++ -o server main.cpp NetworkInterface.cpp -lws2_32

clean:
	del server.exe
