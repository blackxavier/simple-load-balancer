import http.server
import http.client
import threading
import time

backend_servers = [
    {"host": "localhost", "port": 8000},
    {"host": "localhost", "port": 8001},
    {"host": "localhost", "port": 8002},
    # Add more backend servers as needed
]


class HealthChecker:
    def __init__(self):
        self.check_interval = 10  # Set the interval for health checks
        self.running = False
        self.backoff = 5
        self.long_interval = 120

    def start(self):
        self.running = True
        self.check_thread = threading.Thread(target=self._check_loop)
        # if self.layoff != 0:
        #     self.layoff = self.layoff - 1
        # else:
        #     time.sleep(30)
        self.check_thread.start()

    def stop(self):
        self.running = False
        self.check_thread.join()

    def _check_loop(self):
        while self.running:
            self.backoff = self.backoff - 1
            print(self.backoff)
            for server in backend_servers:
                if not self.check_health(server["host"], server["port"]):
                    print(f"Server {server['host']}:{server['port']} is not healthy.")
            if self.backoff == 0:
                time.sleep(self.long_interval)
                self.backoff = 5
            else:
                time.sleep(self.check_interval)

    def check_health(self, host, port):
        try:
            conn = http.client.HTTPConnection(host, port, timeout=2)
            conn.request("GET", "")  # Adjust the health check path as needed
            response = conn.getresponse()
            conn.close()
            return response.status == 200
        except:
            return False


# Create an instance of the HealthChecker
health_checker = HealthChecker()

# Start the health checker in the background
health_checker.start()


class ReverseProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        healthy_server = None
        for server in backend_servers:
            if self.check_health(server["host"], server["port"]):
                healthy_server = server
                break
        if healthy_server:
            # Define backend server details
            # list_of_backend_servers = ["localhost"]
            # list_of_backend_ports = [8000, 8001, 8002]

            # Open a connection to the backend server
            # backend_host = random.choice(list_of_backend_servers)
            # backend_port = random.choice(list_of_backend_ports)
            print(healthy_server["host"], healthy_server["port"])
            backend_conn = http.client.HTTPConnection(
                healthy_server["host"], healthy_server["port"]
            )

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
        else:
            self.send_response(503)  # Service Unavailable
            self.end_headers()
            self.wfile.write(b"No healthy backend servers available.")

    def check_health(self, host, port):
        try:
            conn = http.client.HTTPConnection(host, port, timeout=2)
            conn.request("GET", "")  # Adjust the health check path as needed
            response = conn.getresponse()
            conn.close()
            return response.status == 200
        except:
            return False


if __name__ == "__main__":
    server_address = ("localhost", 80)
    httpd = http.server.HTTPServer(server_address, ReverseProxyHandler)
    httpd.serve_forever()
