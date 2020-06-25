#!/usr/bin/python3
import datetime
import logging

CACHE_LIFETIME = 60


class MemCache:

    cache = {}

    def mylog(self, str):
        logging.info("MemCache: " + str)

    def put(self, name, content_bytes):
        self.mylog("putting bytes in cache " + name)
        self.cache[name] = {"date": datetime.datetime.now(), "bytes": content_bytes}

    def has(self, name):
        is_exist = name in self.cache \
               and (datetime.datetime.now() - self.cache[name]["date"]).total_seconds() < CACHE_LIFETIME

        self.mylog("checking cache " + name + " = " + str(is_exist))

        return is_exist

    def get(self, name):
        self.mylog("get from cache " + name)
        return self.cache[name]["bytes"]
