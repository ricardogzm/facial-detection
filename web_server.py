# Create web server using HTTPServer and BaseHTTPRequestHandler on port 3004
# Serve index.html

from http.server import HTTPServer, BaseHTTPRequestHandler


class VideoWebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        with open("index.html", "rb") as f:
            self.wfile.write(f.read())


def run():
    server_address = ("", 3004)
    httpd = HTTPServer(server_address, VideoWebServer)
    print("Web server running on port 3004")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    httpd.server_close()
    print("Server stopped.")


if __name__ == "__main__":
    run()
