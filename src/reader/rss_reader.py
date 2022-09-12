import argparse
import logging
import sys

import feedparser
from src.reader.rss_document import RssDocument


class RssReaderOptionsParser(argparse.ArgumentParser):
    def __init__(self):
        super().__init__(
            description='Pure Python command-line RSS reader.',
            add_help=False,
            exit_on_error=False,
        )
        # group1 - when specified, application terminates
        group1 = self.add_argument_group()
        group1.add_argument(
            '--help', '-h',
            action='store_true',
            help='show this help message and exit',
        )
        group1.add_argument(
            '--version',
            action='store_true',
            help='print version of Rss reader utility and exit',
        )
        # group2 - normal application run
        group2 = self.add_argument_group()
        group2.add_argument(
            '--json',
            action='store_true',
            help='print result as JSON in stdout',
        )
        group2.add_argument(
            '--verbose',
            action='store_true',
            help='outputs verbose status messages',
        )
        group2.add_argument(
            '--limit',
            metavar='LIMIT',
            help='limit news topics if this parameter provided',
            type=int,
            default=-1)
        group2.add_argument(
            'url',
            help='RSS url to be used',
            nargs='?',
            default=None,
        )

    def error(self, message):
        """
        Overriding parent implementation as it calls exit(2) - instead we just throw exception
        """
        raise Exception(message)


class RssReader:
    logger = logging.getLogger("RssReader")
    VERSION = '0.1'

    def __init__(self, args):
        self.args = self.handle_args(args)
        self.logger.debug("Using args: %ss", self.args)

    def handle_args(self, args):
        parser = RssReaderOptionsParser()
        try:
            args = parser.parse_args(args)
        except Exception as e:
            print(f"Error: {e}")
            parser.print_usage()
            exit(2)
        if args.help:
            parser.print_help()
            exit(0)
        if args.version:
            print(f"Version: {self.VERSION}")
            exit(0)
        # URL should be present on normal run
        if not args.url:
            print(f"Argument 'url' should be present")
            parser.print_usage()
            exit(3)
        # setup logger
        if args.verbose:
            logging.basicConfig(
                stream=sys.stdout,
                filemode="w",
                level=logging.DEBUG,
                force=True,
                format="%(asctime)s [%(levelname)-5s] %(module)s.%(funcName)s[%(lineno)d]: %(message)s")
        else:
            class NoOpStream:
                def write(self, output):
                    pass
            logging.basicConfig(
                stream=NoOpStream(),
                force=True,
            )
        return args

    def download(self):
        return RssDocument(feedparser.parse(self.args.url), self.args.limit)
