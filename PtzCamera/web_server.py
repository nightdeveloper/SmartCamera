#!/usr/bin/python3

import io
import logging
import socketserver
from http import server
from threading import Condition

import picamera

logging.basicConfig(level=logging.INFO)


class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)


class StreamingHandler(server.BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()

        elif self.path == '/index.html':
            file = open("web_server.html")
            content = file.read()
            file.close()

            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))

        elif self.path.startswith('/current_image.jpg'):
            self.send_response(200)
            self.send_header('Age', '0')
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Content-Type', 'image/jpeg')
            self.end_headers()

            image_stream = io.BytesIO()
            camera.capture(image_stream, format='jpeg')
            image_stream.seek(0)

            self.wfile.write(image_stream.read())

        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', '0')
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:

                    camera.annotate_text = "ISO " + str(camera.iso) \
                                           + ", exposure " + str(camera.exposure_speed) \
                                           + ", analog gain " + str(camera.analog_gain) \
                                           + ", awb mode " + str(camera.awb_mode)
#                                          + ", shutter " + str(camera.shutter_speed) \
#                                          + ", awb gains " + ''.join(str(x) for x in camera.awb_gains)

                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', str(len(frame)))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


logging.info("starting smart camera")

with picamera.PiCamera() as camera:
    output = StreamingOutput()

    camera.rotation = 180
    camera.resolution = (2592, 1944)  # WaveShare J 2592 × 1944
    camera.framerate = 24

    camera.start_recording(output, format='mjpeg', resize=(640, 480))
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()
