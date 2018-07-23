
import socket
import threading
import sys

connections = []

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = '0.0.0.0'
port = 2000

def handler(conn, addr):
    global connections
    while True:
        data = conn.recv(1024)
        for node in connections:
            node.send(bytes(data))
        if not data:
            print(addr[0]+":"+str(addr[1])+" disconnected.")
            connections.remove(conn)
            conn.close()
            break

if len(sys.argv) > 1:
    # Script for Client
    pass

else:
    # Script for Server
    sock.bind((ip, port))
    sock.listen(5)
    print("Server started at "+ip+" on port "+str(port))
    while True:
        conn, addr = sock.accept()
        connections.append(conn)
        process = threading.Thread(target=handler, args=(conn,addr))
        process.daemon = True
        process.start()
        print("Connection established from "+addr[0]+":"+str(addr[1]))