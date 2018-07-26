import socket
import threading
import sys
import time

connections = []
port = 2000

# Broadcast responder - UDP connection for fast Server IP lookup
lookup_port = 2001

class BroadcastServer():
    # Broadcast responder
    def __init__(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', port))
        print("BROADCAST SERVER on port " + str(port))
    
    def run(self):
        pThread = threading.Thread(target=self.process)
        pThread.daemon = True
        pThread.start()
    def process(self):
        while True:
            data, addr = self.sock.recvfrom(512)
            print(str(addr) + " found this server.")
            if data=="ip":
                self.sock.sendto(socket.gethostbyname(socket.gethostname()),addr)

# END Broadcast responder

class Server:
    # Server TCP Connection
    def __init__(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('0.0.0.0', port))
        self.sock.listen(50)
        print("STREAM SERVER on port "+str(port))

    def handle(self, conn, addr):
        global connections
        self.lock = threading.Lock()
        while True:
            try:
                data = conn.recv(1024)
            except:
                conn.close()
                connections.remove(conn)
                print(addr[0]+":"+str(addr[1])+" disconnected")
                break
            if not data:
                conn.close()
                connections.remove(conn)
                print(addr[0]+":"+str(addr[1])+" disconnected")
                break
            # Receive data from client
            with self.lock:
                print(addr[0]+":"+data)

    def process(self):
        while True:
            conn, addr = self.sock.accept()
            print(addr[0]+":"+str(addr[1])+" Connected")
            connections.append(conn)
            process = threading.Thread(target=self.handle, args=(conn, addr))
            process.daemon = True
            process.start()
    def run(self):
        proc = threading.Thread(target=self.process)
        proc.daemon = True
        proc.start()

class Hardware:
    def __init__(self):
        pass

    def setState(self, pin, value):
        pass
    
    def setMode(self, pin, mode):
        return 1

    def readState(self, pin):
        pass

if len(sys.argv)>1:
    hardware = Hardware()

class Client:
    # Client TCP Connection
    def __init__(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = ''
        
        # Find server
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp_sock.bind(('0.0.0.0', 2003))
        tCatch = threading.Thread(target=self.ip_catch)
        tCatch.daemon = True
        tCatch.start()
        found = False
        while not found:
            if self.server_ip:
                print("Server ip is " + self.server_ip)
                break
            for fourth in range(1, 256):
                local_ip = socket.gethostbyname(socket.gethostname())
                arr_ip = local_ip.split(".")
                first = arr_ip[0]
                second = arr_ip[1]
                third = arr_ip[2]
                base_ip = first + "." + second + "." + third
                global lookup_port
                host = (base_ip+"."+str(fourth), lookup_port)
                self.udp_sock.sendto("ip", host)
        # End Find Server

        self.sock.connect((self.server_ip, port))
        transmitter = threading.Thread(target=self.begin_transmission, args=(self.server_ip, port))
        transmitter.daemon = True
        transmitter.start()

    def ip_catch(self):
        while True:
            data, addr = self.udp_sock.recvfrom(512)
            if data:
                self.server_ip = addr[0]
                break

    def run(self):
        while True:
            print(socket.gethostbyname(socket.gethostname()) + " on port " + str(port))
            data = ""
            try:
                data = self.sock.recv(1024)
            finally:
                if not data:
                    print("Terminating connection.")
                    self.sock.close()
                    break

    def begin_transmission(self, address, port):
        while True:
            # Send to server
            try:
                pin_1 = hardware.setMode(1,"OUT")
                self.sock.send("Data: "+str(pin_1))
                time.sleep(1)
            except:
                print("Connection lost.")
                break

class WebServer:
    # Web Server TCP Connection
    def __init__(self):
        # Initialize Web Server through creating own socket
        self.port = 80
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind(('0.0.0.0', self.port))
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
        header += "Connection: close\n\n"
        return header

    def node_handler(self, conn, addr):
        # Given that client has been accepted, throw on new thread to avoid blocking
        self.lock = threading.Lock()
        output = ""
        data = conn.recv(1024)
        if not data: return
        output += "Request from: "+addr[0]+":"+str(addr[1]) + "\n"
        method = data.split(' ')[0]
        output += "REQUEST METHOD:\t"+ method + "\n"
        if method=="GET" or method == "HEAD":
            file_serve = data.split(' ')[1]
            file_serve = file_serve.split('?')[0] # Ignore ? character
            if file_serve == "/":
                file_serve = "/index.html"

            # Data Stream
            if file_serve == "/data":
                response = self.get_header(200).encode()
                response += "1110001110001110101 from port " + str(addr[1])
                conn.send(response)
                conn.close()
                output += "\n"
                with self.lock: print(output)
                return

        curr_file_serve = self.root_dir + file_serve
        output += "TARGET:\t\t" + curr_file_serve + "\n"
        try:
            f = open(curr_file_serve, 'rb')
            if method == "GET":
                response_data = f.read()
            f.close()
            response_header = self.get_header(200)
        except:
            output += "File not found. Serving 404 Page" + "\n"
            response_header = self.get_header(404)
            if method == "GET":
                response_data = b"<html><center><h1>404 Page not found</h1></center></html>"

        response = response_header.encode()
        if method == "GET":
            response += response_data
        conn.send(response)
        conn.close()
        output += "\n"
        with self.lock: print(output)

if len(sys.argv)>1:
    client = Client(port)
    client.run()
else:
    print("SERVER IP: " + socket.gethostbyname(socket.gethostname()))
    web = WebServer()
    web.run()
    server = Server(port)
    server.run()
    broadcastserver = BroadcastServer(lookup_port)
    broadcastserver.run()

    # Keep-Alive Loop
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Servers has been terminated.")
        exit()