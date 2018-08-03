import socket
import threading
import sys
import time
import datetime
import random
import uuid
from pprint import pprint

connections = []
database = []
active_ip = []
mac_active = []
last_reports = []
port = 4000

# Broadcast responder - UDP connection for fast Server IP lookup
lookup_port = 4001
local_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    # For local network instance
    local_sock.connect(('8.8.8.8', 80))
except:
    # For internal network instance
    local_sock.connect((socket.gethostbyname(socket.gethostname()), 80))
local_ip = local_sock.getsockname()[0]

class BroadcastServer():
    # Broadcast responder
    def __init__(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0', port))
        print("BROADCAST SERVER on port " + str(port))
    
    def run(self):
        pThread = threading.Thread(target=self.process)
        pThread.daemon = True
        pThread.start()

    def process(self):
        while True:
            data, addr = self.sock.recvfrom(512)
            if data=="ip" and addr[0] not in active_ip:
                active_ip.append(addr[0])
                print(str(addr) + " found this server.")
                self.sock.sendto(self.sock.getsockname()[0],addr)
            elif data=="ip":
                self.sock.sendto(self.sock.getsockname()[0],addr)

# END Broadcast responder

collections = []

class Server:
    # Server TCP Connection
    def __init__(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
                active_ip.remove(addr[0])
                print(addr[0]+":"+str(addr[1])+" disconnected")
                break
            if not data:
                conn.close()
                connections.remove(conn)
                active_ip.remove(addr[0])
                print(addr[0]+":"+str(addr[1])+" disconnected")
                break
            # Receive data from client
            with self.lock:
                global database
                print(addr[0]+","+data)
                database.append(data)

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

        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_sock.bind(('0.0.0.0', 4002))
        self.tCatch = threading.Thread(target=self.ip_catch)
        self.tCatch.daemon = True
        

        self.find_server()

        transmitter = threading.Thread(target=self.begin_transmission, args=(self.server_ip, port))
        transmitter.daemon = True
        transmitter.start()

    def find_server(self):
        try:
            self.tCatch.start()
        except:
            pass
        # Find server
        while True:
            if self.server_ip:
                try:
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.sock.connect((self.server_ip, port))
                    print("Server ip is " + self.server_ip)
                    break
                except:
                    print("Connection failed.")
                    #self.server_ip = ''
                    #time.sleep(1)
                    break
            for fourth in range(1, 256):
                global local_ip
                arr_ip = str(local_ip).split(".")
                first = arr_ip[0]
                second = arr_ip[1]
                third = arr_ip[2]
                base_ip = first + "." + second + "." + third
                global lookup_port
                self.host = (base_ip+"."+str(fourth), lookup_port)
                self.udp_sock.sendto("ip", self.host)
            time.sleep(1)
            self.host = ''
        print("Broadcast session ended.")
        # End Find Server

    def ip_catch(self):
        print("Waiting for server response...")
        while True:
            try:
                data, addr = self.udp_sock.recvfrom(512)
                if data:
                    self.server_ip = addr[0]
                    break
            except:
                self.server_ip = ''
                    


    def run(self):
        global local_sock
        while True:
            print(local_sock.getsockname()[0] + " on port " + str(port))
            data = ""
            try:
                data = self.sock.recv(1024)
            finally:
                if not data:
                    print("Connection lost.")
                    self.sock.close()
                    break

    def begin_transmission(self, address, port):
        status = 0
        while True:
            # Send to server
            try:
                pin_1 = hardware.setMode(1,"OUT")
                dt = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
                mac = hex(uuid.getnode())[2:-1]
                mac = ':'.join(a+b for a,b in zip(mac[::2], mac[1::2]))
                self.sock.send(mac+","+ str(random.randint(1,3)) +"," +dt)
                time.sleep(1)
            except:
                if status == 0:
                    status = 1
                    print("Transmission stopped.")
                

class WebServer:
    # Web Server TCP Connection
    def __init__(self):
        # Initialize Web Server through creating own socket
        self.port = 40
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
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
        self.threads = []
        while True:
            # New Connection accepted
            conn, addr = self.sock.accept()
            threading.Thread(target=self.node_handler, args=(conn, addr)).start()

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
        global database
        global mac_active
        global last_reports
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

            # Get active MAC
            if file_serve == "/active_mac":
                time_now = datetime.datetime.now()
                date_format = "%Y-%m-%d %H:%M:%S"
                response = self.get_header(200).encode()
                if database:
                    for item in database:
                        item_arr = item.split(',')
                        item_time = datetime.datetime.strptime(item_arr[2], date_format)
                        delta_time = time_now-item_time
                        delta_time_seconds = delta_time.total_seconds()
                        if delta_time_seconds<10:
                            if item_arr[0] not in mac_active:
                                mac_active.append(item_arr[0])
                        else:
                            try:
                                mac_active.remove(item_arr[0])
                            except:
                                pass
                    response += str(mac_active)
                conn.send(response)
                conn.close()
                output += "\n"
                return

            # Get last reports
            if file_serve == "/last_reports":
                time_now = datetime.datetime.now()
                date_format = "%Y-%m-%d %H:%M:%S"
                
                response = self.get_header(200).encode()
                if database:
                    last = ''
                    if mac_active:
                        for mac in mac_active:
                            for item in database:
                                item_arr = item.split(',')
                                if mac == item_arr[0]:
                                    last = item
                            
                            if last:
                                temp = last.split(',')
                                mac = temp[0]
                                for i,report in enumerate(last_reports):
                                    report_mac = report.split(',')[0]
                                    if report_mac == mac:
                                        last_reports.pop(i)
                            last_reports.append(last)
                        
                    response += str(last_reports)
                conn.send(response)
                conn.close()
                output += "\n"
                return

        print("HERE")
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
        print(output)

if len(sys.argv)>1:
    client = Client(port)
    client.run()
else:

    _tempsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # For local network instance
        _tempsock.connect(("8.8.8.8", 80))
    except:
        # For internal network instance
        _tempsock.connect((socket.gethostbyname(socket.gethostname()), 80))
    print("SERVER IP: " + _tempsock.getsockname()[0])
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