from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')

server = HTTPServer(('127.0.0.1', 8001), Handler)
print('Servidor en puerto 8001')
server.serve_forever()