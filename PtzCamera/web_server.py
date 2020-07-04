#!/usr/bin/python3

import io
import sys
import logging
import time
import traceback
from flask import Flask, render_template, send_file, Response
from threading import Condition, Lock

from enums import Position
from mymemcache import MemCache

from servo import Servo, MOVEMENT_DELAY

HTTP_HOST = '0.0.0.0'
HTTP_PORT = 8000
HTTP_DEBUG = True

logging.basicConfig(level=logging.INFO)

logging.info("starting smart camera...")

isServoAvailable = False
h_servo = None
v_servo = None

logging.info("creating memcache and locks...")
ptz_lock = Lock()
camera_lock = Lock()
image_cache = MemCache()


logging.info("starting servo detection...")
try:
    h_servo = Servo(0, 0.7, 2.3)  # sg90,  hw address 1, duty 1-2ms
    v_servo = Servo(1, 0.7, 2.3)  # mg90s, hw address 0, duty 1-2ms

    isServoAvailable = True
    logging.info("servo is available")

except Exception as e:
    logging.info("servo not available: {0}".format(e))
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_tb(exc_traceback, file=sys.stdout)

    h_servo = Servo(0, 1.0, 2.0, True)
    v_servo = Servo(1, 1.0, 2.0, True)
    isServoAvailable = False


logging.info("checking for camera")
camera = None


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


try:
    import picamera
    camera = picamera.PiCamera()
    camera_video_output_stream = StreamingOutput()


except Exception as e:
    logging.info("camera not available: {0}".format(e))
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_tb(exc_traceback, file=sys.stdout)

    import camera_emulation
    camera = camera_emulation.PiCamera()
    camera_video_output_stream = camera_emulation.EmulatedStreamingOutput()


try:
    with camera:
        camera.rotation = 180
        camera.resolution = (2592, 1944)  # WaveShare J 2592 × 1944
        camera.framerate = 24

        logging.info("start camera recording...")
        camera.start_recording(camera_video_output_stream, format='mjpeg', resize=(640, 480))
        try:
            logging.info("starting http server")
            app = Flask("server")

            def position_to_servo(servo, position):
                if position == Position.MIN:
                    servo.min()
                elif position == Position.MAX:
                    servo.max()
                else:
                    servo.center()

            def ptz_center():
                position_to_servo(h_servo, Position.CENTER)
                position_to_servo(v_servo, Position.CENTER)
                time.sleep(MOVEMENT_DELAY)

            def stream():
                while True:
                    # logging.info("requested frame")
                    camera.annotate_text = "ISO " + str(camera.iso) \
                                           + ", exposure " + str(camera.exposure_speed) \
                                           + ", analog gain " + str(camera.analog_gain) \
                                           + ", awb mode " + str(camera.awb_mode)
                    #                      + ", shutter " + str(camera.shutter_speed) \
                    #                      + ", awb gains " + ''.join(str(x) for x in camera.awb_gains)

                    with camera_lock:
                        with camera_video_output_stream.condition:
                            camera_video_output_stream.condition.wait()
                            frame = camera_video_output_stream.frame

                    # logging.info("sending bytes len " + str(len(frame)))

                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            @app.after_request
            def add_header(response):
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                return response

            @app.route('/', endpoint="root")
            def root_endpoint():
                logging.info("requested root")
                return render_template("index.html")

            @app.route('/images/<name>', endpoint="camera_image")
            def image_endpoint(name):
                logging.info("requested image " + name)

                try:
                    if image_cache.has(name):
                        logging.info("getting image from cache")
                        image_bytes = image_cache.get(name)
                    else:
                        if name == "current.jpg":
                            position_h = Position.CENTER
                            position_v = Position.CENTER
                        elif name == "left.jpg":
                            position_h = Position.MAX
                            position_v = Position.CENTER
                        elif name == "right.jpg":
                            position_h = Position.MIN
                            position_v = Position.CENTER
                        elif name == "up.jpg":
                            position_h = Position.CENTER
                            position_v = Position.MIN
                        elif name == "down.jpg":
                            position_h = Position.CENTER
                            position_v = Position.MAX
                        else:
                            return 'invalid position!', 400

                        if not isServoAvailable:
                            with open("templates/current.jpg", mode='rb') as file:
                                image_bytes = file.read()
                        else:
                            with camera_lock:
                                with ptz_lock:
                                    logging.info("requested left image")

                                    position_to_servo(h_servo, position_h)
                                    position_to_servo(v_servo, position_v)
                                    time.sleep(MOVEMENT_DELAY)

                                image_stream = io.BytesIO()
                                camera.capture(image_stream, format='jpeg')
                                image_stream.seek(0)
                                image_bytes = image_stream.read()
                                image_cache.put(name, image_bytes)

                    return send_file(
                        io.BytesIO(image_bytes),
                        mimetype="image/jpeg",
                        as_attachment=True,
                        attachment_filename=name)

                except Exception as ie:
                    logging.info("can't send image: {0}".format(ie))
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    traceback.print_tb(exc_traceback, file=sys.stdout)
                    return 'bad request!', 500

            @app.route('/stream', endpoint="camera_stream")
            def stream_endpoint():
                logging.info("requested stream")

                try:
                    logging.info("requested left image")

                    position_to_servo(h_servo, Position.CENTER)
                    position_to_servo(v_servo, Position.CENTER)
                    time.sleep(MOVEMENT_DELAY)

                    return Response(stream(),
                                    mimetype='multipart/x-mixed-replace; boundary=frame')

                except Exception as ie:
                    logging.info("can't start stream: {0}".format(ie))
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    traceback.print_tb(exc_traceback, file=sys.stdout)
                    return "can't start stream", 500

            app.run(host=HTTP_HOST, port=HTTP_PORT, debug=HTTP_DEBUG, use_reloader=False)

        finally:
            logging.info("stop camera recording")
            camera.stop_recording()

except Exception as e:
    logging.error("camera error {0}".format(e))
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_tb(exc_traceback, file=sys.stdout)
