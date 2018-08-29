#!/usr/bin/python3
#
# Wesleyan University
# COMP 332, Spring 2018
# Homework 3: Simple multi-threaded web proxy

# Usage:
#   python3 web_proxy.py <proxy_host> <proxy_port> <requested_url>
#
#************************************************************************************************
#                                   COMP332: Homework 4
#                                 Author: Shota Nakamura
#Usage: run python3 web_proxy.py
#Purpose: This Server (web_proxy) listens for connections from the web_client and acts as the "middle-man" 
#         to connect the client to the requested webserver. This means that this server takes multiple clients.
#         Therefore, once it receives a GET request, it then sends it to the webserver by using port 80.
#         However, this server also has a cache that is implemented as a dictionary. It uses URL as the KEY to find the VALUE
#         which is the date the url was last modified and also its contents.
#         
#         If the program finds the URL in the cache, it then as a If-Modified-Since statement to the GET request and sends it to the server.
#         if it is not modified, it will send back a 304 Not Modified, where the server send the contents of its cache.
#         If the web server sends back a 200 OK, or it is modified, then the proxy sends back the server request to the client. 
#************************************************************************************************

# Python modules
import socket
import sys
import threading

# Project modules
import http_constants as const
import http_util


class WebProxy():

    def __init__(self, proxy_host, proxy_port):
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.proxy_backlog = 1
        self.cache = {}
        self.start()

    def start(self):

        # Initialize server socket on which to listen for connections
        try:
            proxy_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            proxy_sock.bind((self.proxy_host, self.proxy_port))
            proxy_sock.listen(self.proxy_backlog)
        except OSError as e:
            print ("Unable to open proxy socket: ", e)
            if proxy_sock:
                proxy_sock.close()
            sys.exit(1)

        # Wait for client connection
        while True:
            conn, addr = proxy_sock.accept()
            print ('Client has connected', addr)
            thread = threading.Thread(target = self.serve_content, args = (conn, addr))
            thread.start()
        
    def serve_content(self, conn, addr):

        # Receive binary request from client
        bin_req = conn.recv(4096)
        try:
            str_req = bin_req.decode('utf-8')
            print(str_req)
        except ValueError as e:
            print ("Unable to decode request, not utf-8", e)
            conn.close()
            return

        # Extract host and path
        hostname = http_util.get_http_field(str_req, 'Host: ', const.END_LINE)
        pathname = http_util.get_http_field(str_req, 'GET ', ' HTTP/1.1')
        if hostname == -1 or pathname == -1:
            print ("Cannot determine host")
            client_conn.close()
            return
        elif pathname[0] != '/':
            [hostname, pathname] = http_util.parse_url(pathname)
        str_req = http_util.create_http_req(hostname, pathname)

        url = hostname + pathname
        #-----------------------------My Code----------------------------------------
        #Checks if url is in the cache and if is, save to keyVal
        if(url in self.cache):
            print("url is in cache")
            cache_temp = self.cache[url]
            add_date = cache_temp[0]
            new_str_req = http_util.add_http_field(str_req, "If-Modified-Since", str(add_date))
            str_req = new_str_req
            #Check the cache contents		
        # Open connection to host and send binary request
        bin_req = str_req.encode('utf-8')
        try:
            web_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            web_sock.connect((hostname, 80))
            print ("Sending request to web server: ", str_req)
            web_sock.sendall(bin_req)
        except OSError as e:
            print ("Unable to open web socket: ", e)
            if web_sock:
                web_sock.close()
            conn.close()
            return

        # Wait for response from web server
        bin_reply = b''
        while True:
            more = web_sock.recv(4096)
            if not more:
                 break
            bin_reply += more
        #-------Decode here----------
        try:
            decoded = bin_reply.decode('utf-8')
            try:
                date = http_util.get_http_field(decoded, "Last-Modified: ","\r\n")
            except:
                date = http_util.get_http_field(decoded, "Date: ", "\r\n")
        except ValueError as e:
            print("Unable to Decode Url Object", e)            
        #Proxy now Checks Server Response

        #-----if there is no modification to dict---
        if(http_util.get_http_field(decoded, "HTTP/1.1 ", "\r\n") == "304 Not Modified"):
            print("Server sent back 304 Not Modified.")
            #Update cache to not modified...
            conn.sendall(self.cache[url][1])
            print("Came from the Cache, 304 Not Modified")
        #---------if server returns 200 OK--------	
        elif(http_util.get_http_field(decoded, "HTTP/1.1 ", "\r\n") == "200 OK"):
            self.cache[url] = [date,bin_reply]
            print('Proxy received from server (showing 1st 300 bytes): ', bin_reply[:300])
            conn.sendall(bin_reply)
        #----------if there is some kind of error----
        else: #if there is a problem
            print("Error with Request, Closing connection.")
            conn.close() 
        #---------Close connection to client------
        conn.close()

def main():

    print (sys.argv, len(sys.argv))

    proxy_host = 'localhost'
    proxy_port = 50007

    if len(sys.argv) > 1:
        proxy_host = sys.argv[1]
        proxy_port = int(sys.argv[2])

    web_proxy = WebProxy(proxy_host, proxy_port)

if __name__ == '__main__':

    main()
