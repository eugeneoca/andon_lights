import socket
import threading
import sys
import time

connections = []
ip = '0.0.0.0'
port = 2000
class Server:
    # Server TCP Connection
    def __init__(self, address,port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((address, port))
        self.sock.listen(50)
        print("Server listening on "+address+" on port "+str(port))

    def handle(self, conn, addr):
        data = conn.recv(1024)
        # Receive data from client
        print(addr[0]+":"+data)

        # Send ACK Message
        conn.send("OK")
        conn.close()
        connections.remove(conn)

    def run(self):
        while True:
            conn, addr = self.sock.accept()
            connections.append(conn)
            process = threading.Thread(target=self.handle, args=(conn, addr))
            process.daemon = True
            process.start()

class Client:
    # Client TCP Connection
    def __init__(self, address, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((address, port))
    def sendStatus(self, msg):
        self.sock.send(msg)
        while True:
            response = self.sock.recv(1024)
            print("Response: "+response)
            if response!="OK":
                self.sock.send(msg)
            else:
                self.sock.close()
                break

class WebServer:
    # Web Server TCP Connection
    def __init__(self):
        # Initialize Web Server through creating own socket
        pass
    def run(self):
        # Run Web Server on separate thread
        pass

    def get_header(self, code):
        # Resolve desired header
        pass

    def node_handler(self, conn, addr):
        # Given that client has been accepted, throw on new thread to avoid blocking
        pass

if len(sys.argv)>1:
    client = Client(sys.argv[1], port)
    client.sendStatus(sys.argv[2])
else:
    server = Server(ip, port)
    server.run()