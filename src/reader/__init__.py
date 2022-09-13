
from reader.rss_reader import RssReader


def run_rss_reader():
    reader = RssReader()
    reader.download()
    reader.format_output()
