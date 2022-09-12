import sys

from reader.rss_reader import RssReader
import logging

logging.basicConfig(
    stream=sys.stdout,
    filemode="w",
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)-5s] %(module)s.%(funcName)s[%(lineno)d]: %(message)s")

if __name__ == '__main__':
    RssReader().download()
