import socket

server   = "www.google.com"
port        = 80

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_ip = socket.gethostbyname(server)

request = "GET / HTTP/1.1\nHost: "+server+"\n\n"

sock.connect((server_ip, port))
sock.send(request)
print(server_ip)
print(sock.recv(4096))