#!/usr/bin/python3
import datetime
import logging

CACHE_LIFETIME = 60


class MemCache:

    cache = []

    def put(self, name, content_bytes):
        logging.info("putting bytes in cache " + name)
        self.cache[name] = {"date": datetime.datetime.now(), "bytes": content_bytes}

    def has(self, name):
        is_exist = self.cache[name] is None \
               or (datetime.datetime.now() - self.cache[name]["date"]).total_seconds() < CACHE_LIFETIME

        logging.info("checking cache " + name + " = " + is_exist)

        return is_exist

    def get(self, name):
        logging.info("get from cache " + name)
        return self.cache[name]
