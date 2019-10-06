#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import os

with open(os.path.join(os.pardir, "selectors.json"), "r") as file:
	selectors = file.read()


class RequestHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path == "/selectors.json":
			self.send_response(200)
			self.end_headers()
			self.wfile.write(selectors.encode())
		else:
			self.send_response(404)


HTTPServer(("127.0.0.1", 8080), RequestHandler).serve_forever()
