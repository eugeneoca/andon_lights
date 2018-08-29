import socket
import threading
import sys
import time
import datetime
import random
import uuid
import json
import os
#import npyscreen # For Console GUI
#from fpdf import FPDF # For PDF Generation

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
        #print("BROADCAST SERVER on port " + str(port))
    
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
        #print("STREAM SERVER on port "+str(port))

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
                log = addr[0]+","+data.decode()
                # Put Data into the database
                log_arr = log.split(',')
                try:
                    db = mysql.connect(**dbconfig)
                except:
                    print("INSERT_DATA: No database connection. Teminating...")
                    os._exit(0)
                    time.sleep(2)
                try:
                    cursor = db.cursor()
                    cursor.execute(
                        """INSERT INTO reports (devicename, ip, macaddress, status, datetime) VALUES (%s, %s,%s, %s, %s)""",
                        (log_arr[1], log_arr[0], log_arr[2], log_arr[3], log_arr[4])
                    )
                except:
                    print("Database operation failed.")
                
                try:
                    db.commit()
                except:
                    print("Database operation failed.")
                try:
                    cursor.close()
                    db.close()
                except:
                    pass

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
                    print(self.server_ip)
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
        status = "GREEN\n"
        prev_state = "GREEN\n"
        while True:
            # Check status considering the conditions/rules.
            # 1 == RED
            # 2 == ORANGE
            # 3 == GREEN
            # 4 == RESPONDED
            try:
                # my local:: light_status = open('status.db', 'r').read()

                # RTU
                light_status = open('/var/txtalert/andon_lights/status.txt', 'r').read()
                # END RTU

                curr_state = light_status
                changed_state = curr_state!=prev_state
                if changed_state and curr_state:
                    # State has been changed
                    print("STATE HAS BEEN CHANGED: "+curr_state)

                    prev_state=curr_state
                    # Update server on state change
                    try:
                        # This will transmit data to the server
                        dt = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
                        mac = hex(uuid.getnode())[2:-1]
                        mac = ':'.join(a+b for a,b in zip(mac[::2], mac[1::2]))
                        self.sock.send(sys.argv[1]+","+mac+","+ str(curr_state) +"," +dt)
                        time.sleep(2)
                    except:
                        if status == 0:
                            status = 1
                            print("Transmission stopped.")
                else:
                    pass
            except Exception as e:
                print("Error in transmission. " + str(e))
            

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
        try:
            db = mysql.connect(**dbconfig)
        except:
            print("GET_LASTITEM: No database connection. Teminating...")
            os._exit(0)
            time.sleep(2)
        try:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM reports ORDER BY ID DESC LIMIT 1")
            result = cursor.fetchone()
            if result:
                item = result
        except:
            print("Database operation failed.")
        
        try:
            cursor.close()
            db.close()
            self.lock.release()
        except:
            pass

    def node_handler(self, conn, addr):
        global dbconfig
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
        with_args = False
        args = ""
        if "?" in request:
            args = request.split('?')[1]
            request = request.split('?')[0]
            with_args = True

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
                    db = mysql.connect(**dbconfig)
                except:
                    print("GET_LATEST_LOG: No database connection. Teminating...")
                    os._exit(0)
                    time.sleep(2)
                try:
                    cursor = db.cursor()
                    cursor.execute("SELECT * FROM reports WHERE ip = '%s' ORDER BY ID DESC LIMIT 1" % (ip_item))
                    result = cursor.fetchone()
                    cursor.execute("SELECT * FROM tbl_plnames WHERE devicename LIKE '%s' ORDER BY ID DESC LIMIT 1" % (result[1]))
                    name = cursor.fetchone()
                    if name:
                        result = list(result)
                        result[3] = name[2]
                    last_reports.append(result)
                    cursor.close()
                    db.close()
                except Exception as e:
                    print("Database operation failed.", e)
                
                    
            output += str(json.dumps([active_ip,inactive_ip,last_reports]))
        elif method == "GET" and request == "/rename":
            if with_args == True:
                arr_args = args.split('&')
                
                # Get new plname and devicename
                new_plname = arr_args[0].split('=')[1]
                devicename = arr_args[1].split('=')[1]
                try:
                    db = mysql.connect(**dbconfig)
                except:
                    print("GET_LATEST_LOG: No database connection. Teminating...")
                    os._exit(0)
                    time.sleep(2)
                try:
                    cursor = db.cursor()
                    cursor.execute("SELECT * FROM tbl_plnames WHERE devicename LIKE '%s' ORDER BY ID DESC LIMIT 1" % (devicename))
                    result = cursor.fetchone()
                    if result != None:
                        # Update
                        cursor.execute ("""UPDATE tbl_plnames SET plname='%s' WHERE devicename='%s' """ % (new_plname, devicename))
                        output += "GOOD"
                    else:
                        # Insert
                        cursor.execute("INSERT INTO tbl_plnames (devicename, plname) VALUES (%s, %s)", (devicename, new_plname))
                        output += "GOOD"
                except:
                    print("Database operation failed.")
                try:
                    db.commit()
                    cursor.close()
                    db.close()
                except:
                    pass
            else:
                output = self.get_header(404).encode()
                output += "404 Page not found."
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

    try:
        import mysql.connector as mysql
    except:
        print("Error importing module mysql.connector. Please execute: pip install mysql-connector")
        os._exit(0)
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