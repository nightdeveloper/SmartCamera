#!/usr/bin/python3

import io
import sys
import logging
import time
import socketserver
import traceback
from http import server
from threading import Condition, Lock
from enum import Enum

import picamera
from mymemcache import MemCache

from servo import Servo, MOVEMENT_DELAY

HTTP_PORT = 8000

logging.basicConfig(level=logging.INFO)

logging.info("starting smart camera")

isServoAvailable = False

h_servo = None
v_servo = None


class Position(Enum):
    MIN = 1
    CENTER = 2
    MAX = 3

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

    ptz_lock = Lock()

    image_cache = MemCache()

    def send_image(self, image_name):
        self.send_response(200)
        self.send_header('Age', '0')
        self.send_header('Cache-Control', 'no-cache, private')
        self.send_header('Content-Type', 'image/jpeg')
        self.end_headers()

        if self.image_cache.has(image_name):
            image_bytes = self.image_cache.get(image_name)
        else:
            image_stream = io.BytesIO()
            camera.capture(image_stream, format='jpeg')
            image_stream.seek(0)
            image_bytes = image_stream.read()
            self.image_cache.put(image_name, image_bytes)

        self.wfile.write(image_bytes)

    def position_to_servo(self, servo, position):
        if position == Position.MIN:
            servo.min()
        elif position == Position.MAX:
            servo.max()
        else:
            servo.center()

    def has_servos(self):
        return h_servo is not None or v_servo is not None

    def ptz_center(self):
        if self.has_servos():
            self.position_to_servo(h_servo, Position.CENTER)
            self.position_to_servo(v_servo, Position.CENTER)
            time.sleep(MOVEMENT_DELAY)

    def ptz_and_send_image(self, position_h, position_v, is_return_anyway = False):
        image_name = "image_h" + str(position_h) + "_v" + str(position_v)

        if self.has_servos():
            with self.ptz_lock:
                logging.info("requested left image")

                self.position_to_servo(h_servo, position_h)
                self.position_to_servo(v_servo, position_v)
                time.sleep(MOVEMENT_DELAY)

                self.send_image(image_name)
        else:
            if is_return_anyway:
                self.ptz_center()
                self.send_image(image_name)
            else:
                self.send_response(503)

    def do_GET(self):
        if self.path == '/':
            logging.info("requested root")

            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()

        elif self.path == '/index.html':
            logging.info("requested index")

            file = open("web_server.html")
            content = file.read()
            file.close()

            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))

        elif self.path.startswith('/current_image.jpg'):
            logging.info("requested current image")
            self.ptz_and_send_image(Position.CENTER, Position.CENTER, True)

        elif self.path.startswith('/image_left.jpg'):
            self.ptz_and_send_image(Position.MAX, Position.CENTER)

        elif self.path.startswith('/image_right.jpg'):
            self.ptz_and_send_image(Position.MIN, Position.CENTER)

        elif self.path.startswith('/image_up.jpg'):
            self.ptz_and_send_image(Position.CENTER, Position.MIN)

        elif self.path.startswith('/image_down.jpg'):
            self.ptz_and_send_image(Position.CENTER, Position.MAX)

        elif self.path == '/stream.mjpg':
            logging.info("requested stream")

            with self.lock:
                if h_servo is not None and v_servo is not None:
                    h_servo.center()
                    v_servo.center()

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


try:
    h_servo = Servo(0, 0.7, 2.3)  # sg90,  hw address 1, duty 1-2ms
    v_servo = Servo(1, 0.7, 2.3)  # mg90s, hw address 0, duty 1-2ms

    isServoAvailable = True
    logging.info("servo is available")
except Exception as e:
    logging.info("servo not available {0}".format(e))

    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_tb(exc_traceback, file=sys.stdout)

    isServoAvailable = False

try:
    with picamera.PiCamera() as camera:
        output = StreamingOutput()

        camera.rotation = 180
        camera.resolution = (2592, 1944)  # WaveShare J 2592 × 1944
        camera.framerate = 24

        logging.info("start camera recording...")

        camera.start_recording(output, format='mjpeg', resize=(640, 480))
        try:
            logging.info("http server is listening on " + str(HTTP_PORT))
            address = ('', HTTP_PORT)
            server = StreamingServer(address, StreamingHandler)
            server.serve_forever()
        finally:
            logging.info("stop camera recording")
            camera.stop_recording()
except Exception as e:
    logging.error("camera error {0}".format(e))
