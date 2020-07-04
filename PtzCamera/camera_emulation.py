#!/usr/bin/python3

import logging
import time


class EmulatedCondition:

    def __enter__(self):
        # logging.info("entering emulated stream")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # logging.info("exiting emulated stream")
        return None

    def wait(self):
        # logging.info("sleeping")
        time.sleep(0.5)


class EmulatedStreamingOutput(object):
    def __init__(self):
        self.condition = EmulatedCondition()
        self.frame_number = 1

    @property
    def frame(self):
        if self.frame_number % 2 == 0:
            filename = "current.jpg"
        else:
            filename = "current2.jpg"

        self.frame_number = self.frame_number + 1

        with open("templates/" + filename, mode='rb') as file:
            return file.read()


class PiCamera:

    def log(self, str):
        logging.info("PiCamera emulation: " + str)

    def __enter__(self):
        self.log("entering")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.log("exiting")

    def iso(self):
        return 100

    def exposure_speed(self):
        return 0.2

    def analog_gain(self):
        return 5

    def awb_mode(self):
        return "auto"

    def shutter_speed(self):
        return 0.02

    def awb_gains(self):
        return ["1", "2", "3"]

    def _set_rotation(self, value):
        self.log("set rotation " + str(value))

    def _set_resolution(self, value):
        self.log("set resolution " + str(value))

    def _set_framerate(self, value):
        self.log("set framerate " + str(value))

    def start_recording(
            self, output, format=None, resize=None, splitter_port=1, **options):
        self.log("start recording format = " + format +
                 ", resize = " + str(resize) +
                 " port = " + str(splitter_port))

    def capture(
            self, output, format=None, use_video_port=False, resize=None,
            splitter_port=0, bayer=False, **options):

        self.log("start caoture format = " + format +
                 ", resize = " + str(resize) +
                 ", port = " + str(splitter_port))

        with open("templates/current.jpg", mode='rb') as file:
            output.write(file.read())


    def stop_recording(self):
        self.log("stop recording")
