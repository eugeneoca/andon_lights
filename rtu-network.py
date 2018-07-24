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
        print("STREAM SERVER on port "+str(port))

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
    def __init__(self, address):
        # Initialize Web Server through creating own socket
        self.port = 80
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((address, self.port))
        print("WEB SERVER on port "+ str(self.port))

        # Server root dir
        self.root_dir = "www"

    def run(self):
        # Run Web Server on separate thread
        tProcess = threading.Thread(target=self.process)
        tProcess.daemon = True
        tProcess.start()

    def process(self):
        self.sock.listen(10)
        while True:
            # New Connection accepted
            conn, addr = self.sock.accept()
            tNode = threading.Thread(target=self.node_handler, args=(conn, addr))
            tNode.daemon = True
            tNode.start()

    def get_header(self, code):
        # Resolve desired header
        header = ''
        if code == 200:
            header += "HTTP/1.1 200 OK\n"
        elif code == 404:
            header += "HTTP/1.1 404 NOT FOUND\n"

        time_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        header += "Date: {now}\n".format(now=time_now)
        header += "RTU-NETWORK BUILT-IN WEBSERVER\n"
        header += "Accept: text/html\n"
        header += "Connection: close\n\n"
        return header

    def node_handler(self, conn, addr):
        # Given that client has been accepted, throw on new thread to avoid blocking
        data = conn.recv(1024)
        if not data: return
        print("Received connection from: "+addr[0]+":"+str(addr[1]))
        method = data.split(' ')[0]
        print("REQUEST METHOD:\t"+ method)
        if method=="GET" or method == "HEAD":
            file_serve = data.split(' ')[1]
            file_serve = file_serve.split('?')[0] # Ignore ? character
            if file_serve == "/":
                file_serve = "/index.html"

        curr_file_serve = self.root_dir + file_serve
        print("TARGET:\t\t" + curr_file_serve)
        try:
            f = open(curr_file_serve, 'rb')
            if method == "GET":
                response_data = f.read()
            f.close()
            response_header = self.get_header(200)
        except:
            print("File not found. Serving 404 Page")
            response_header = self.get_header(404)
            if method == "GET":
                response_data = b"<html><center><h1>404 Page not found</h1></center></html>"

        response = response_header.encode()
        if method == "GET":
            response += response_data
        conn.send(response)
        conn.close()
        print("\n")

if len(sys.argv)>1:
    client = Client(sys.argv[1], port)
    client.sendStatus(sys.argv[2])
else:
    web = WebServer(ip)
    web.run()
    server = Server(ip, port)
    server.run()