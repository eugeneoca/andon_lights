#include <stdio.h>
#include <iostream>
#include <string.h>
#include <winsock2.h>
#include <sys/types.h>
//#include <sys/socket.h>

#define NETWORK_ADDRESS   "192.168.0.0"
#define PORT              2000

using namespace std;

// Prototypes
string scan(string network, int port);

// Global Variables
int fd;
sockaddr_in service;
int service_len;

int main(int argc, char const *argv[])
{
    cout << "Starting service..." << endl;
    cout << "RTU Type:\t\tCLIENT" << endl;
    cout << "Connection Type:\tTCP" << endl;
    cout << "IP Mode:\t\tSTATIC" << endl;
    cout << "Network Address:\t" << NETWORK_ADDRESS << endl;
    cout << "Port No.:\t\t" << PORT << endl;

    // Network Setup
    memset(&service, 0, sizeof service );
    service_len = sizeof(service);
    service.sin_family = AF_INET;
    service.sin_addr.s_addr = inet_addr("127.0.0.1");
    service.sin_port = htons(PORT);
    int result = bind(fd, (sockaddr *) &service, service_len);
    cout << "Bind Status: " << result << endl;
    // Scan Network for open service port
    scan(NETWORK_ADDRESS, PORT);
    return 0;
}

string scan(string network, int port){
    // Get the ip address from network where port is open
    int start_ip = 1;
    int end_ip = 254;
    
    // Get first three octet
    string ip_base = "";
    int octet = 0;
    for(int i=0; i<network.length(); i++){
        if(octet != 3){
            ip_base += network[i];
            if(network[i]=='.'){
                octet++;
            }
        }
    }

    // Scan every address
    string temp = "";
    string target_ip = "";
    for(int i=start_ip; i<=end_ip; i++){
        temp += ip_base;
        temp += to_string(i);
        target_ip = temp;

        // Scanning algorithm
        // End Scanning algorithm

        target_ip="";
        temp = "";
    }
    return "";
}