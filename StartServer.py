from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
import socket
import os
import webbrowser

PORT = 80  # Desired web server port

# Start the server and open the web page
Handler = SimpleHTTPRequestHandler
httpd = TCPServer(("", PORT), Handler)
print(f"Web server started: http://www.thegame.com:{PORT}")
webbrowser.open_new(f"http://www.thegame.com:{PORT}")
httpd.serve_forever()
