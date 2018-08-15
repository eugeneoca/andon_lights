import socket
import threading
import sys
import time
import datetime
import random
import uuid
import json

connections = []
active_ip = []
inactive_ip = []
mac_active = []
last_reports = []
item = []

# DB Setup
dbconfig = {
  "user":"root",
  "host":"127.0.0.1",
  "database":"eaton"
}

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
    global connections
    global dbconfig
    global inactive_ip
    # Server TCP Connection
    def __init__(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0', port))
        self.sock.listen(50)
        print("STREAM SERVER on port "+str(port))

    def handle(self, conn, addr):
        self.lock = threading.Lock()
        while True:
            try:
                data = conn.recv(1024)
            except:
                conn.close()
                connections.remove(conn)
                active_ip.remove(addr[0])
                inactive_ip.append(addr[0])
                print(addr[0]+":"+str(addr[1])+" disconnected")
                break
            if not data:
                try:
                    conn.close()
                    connections.remove(conn)
                    active_ip.remove(addr[0])
                    inactive_ip.append(addr[0])
                    print(addr[0]+":"+str(addr[1])+" disconnected")
                except:
                    pass
                break
            # Receive data from client
            with self.lock:
                log = addr[0]+","+data
                # Put Data into the database
                log_arr = log.split(',')
                db = mysql.connect(**dbconfig)
                cursor = db.cursor()
                cursor.execute(
                    """INSERT INTO reports (devicename, ip, macaddress, status, datetime) VALUES (%s, %s,%s, %s, %s)""",
                    (log_arr[1], log_arr[0], log_arr[2], log_arr[3], log_arr[4])
                )
                try:
                    db.commit()
                except:
                    print("DATABASE: Error occured.")
                finally:
                    cursor.close()
                    db.close()

    def process(self):
        while True:
            conn, addr = self.sock.accept()
            print(addr[0]+":"+str(addr[1])+" Connected")
            if addr[0] in inactive_ip:
                inactive_ip.remove(addr[0])
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
                self.udp_sock.sendto("ip".encode(), self.host)
            time.sleep(1)
            self.host = ''
        print("Broadcast session ended.")
        # End Find Server

    def ip_catch(self):
        print("Waiting for server response...")
        while True:
            try:
                data, addr = self.udp_sock.recvfrom(512)
                if data.decode():
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
                self.sock.send(sys.argv[1]+","+mac+","+ str(random.randint(1,3)) +"," +dt)
                time.sleep(10)
            except:
                if status == 0:
                    status = 1
                    print("Transmission stopped.")
                

class WebServer:
    global mac_active
    global item
    global dbconfig
    global last_reports
    # Web Server TCP Connection
    def __init__(self):
        # Initialize Web Server through creating own socket
        self.port = 81
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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

    def get_lastitem(self):
        self.lock = threading.Lock()
        self.lock.acquire()
        db = mysql.connect(**dbconfig)
        cursor = db.cursor()
        cursor.execute("SELECT * FROM reports ORDER BY ID DESC LIMIT 1")
        result = cursor.fetchone()
        if result:
            item = result
        cursor.close()
        db.close()
        try:
            self.lock.release()
        except:
            pass

    def node_handler(self, conn, addr):
        self.lock = threading.Lock()
        self.lock.acquire()
        last_reports=[]
        output = ""
        data = conn.recv(1024)
        if not data:
            #print("WEB SERVER: " + str(addr))
            return

        # Parameters [METHOD, REQUEST]
        param = data.split(' ')
        method = param[0]
        request = param[1]
        output = self.get_header(200).encode()

        if method == "GET" and request == "/":
            indexpath = self.root_dir + "/index.html"
            f = open(indexpath, 'rb')
            output += f.read()
            f.close()
        elif method == "GET" and request == "/active":
            time_now = datetime.datetime.now()
            date_format = "%Y-%m-%d %H:%M:%S"
            threading.Thread(target=self.get_lastitem).start()
            for ip_item in active_ip:
                try:
                    # Get latest log from db
                    db = mysql.connect(**dbconfig);
                    cursor = db.cursor();
                    cursor.execute("SELECT * FROM reports WHERE ip = '%s' ORDER BY ID DESC LIMIT 1" % (ip_item));
                    result = cursor.fetchone();
                    last_reports.append(result)
                    cursor.close();
                    db.close();
                except Exception as e:
                    print(e)
                    
            output += str(json.dumps([active_ip,inactive_ip,last_reports]))
        else:
            output = self.get_header(404).encode()
            output += "404 Page not found."
        conn.send(output)
        conn.close()
    try:
        self.lock.release()
    except:
        pass

if len(sys.argv)>1:
    client = Client(port)
    client.run()
else:

    # Get Web Interface Structure
    base = open('structure.db', 'rb')
    base_arr = base.read().split(';')
    print(json.dumps(base_arr[0])[0])
    base.close()
    try:
        import mysql.connector as mysql
    except:
        print("Error importing module mysql.connector. Please execute: pip install mysql-connector")
        exit()
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