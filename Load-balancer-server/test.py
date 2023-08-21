import http.server
import http.client
import re
import threading
from flask import Flask

# Create a Flask app for the frontend server
app = Flask(__name__)

# Define the backend server details
backend_host = "backend.example.com"
backend_port = 8080  # Change this to your backend server's port


class ReverseProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Open a connection to the backend server
        backend_conn = http.client.HTTPConnection(backend_host, backend_port)

        # Forward the request to the backend server
        backend_path = self.path
        backend_conn.request("GET", backend_path, headers=self.headers)
        backend_resp = backend_conn.getresponse()

        # Send the backend response back to the client
        self.send_response(backend_resp.status)
        for header, value in backend_resp.getheaders():
            self.send_header(header, value)
        self.end_headers()
        self.wfile.write(backend_resp.read())
        backend_conn.close()


@app.route("/")
def hello():
    return "Hello, this is your Load Balancer!"


def run_servers():
    # Run the frontend server (load balancer) in a separate thread
    frontend_server_address = ("", 80)
    frontend_httpd = http.server.HTTPServer(
        frontend_server_address, ReverseProxyHandler
    )

    frontend_thread = threading.Thread(target=frontend_httpd.serve_forever)
    frontend_thread.start()

    # Run the Flask app (frontend server) in the main thread
    app.run(host="0.0.0.0", port=8080)


if __name__ == "__main__":
    run_servers()
