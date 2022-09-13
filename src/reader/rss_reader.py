import argparse
import json
import logging
import os
import sys
import tempfile
import feedparser
from datetime import datetime
from reader.rss_document import RssDocument, RssItem
from reader.rss_formatter import RssFormatter, JsonRssFormatter, TextRssFormatter, HtmlRssFormatter
from version import __version__


class RssException(Exception):
    pass


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
            '--verbose',
            action='store_true',
            help='outputs verbose status messages',
        )
        group2.add_argument(
            '--limit',
            metavar='LIMIT',
            help='limit news topics if this parameter provided',
            type=int,
            default=None,
        )
        group2.add_argument(
            '--date',
            metavar='DATE',
            help='show feeds locally cached with same published date in YYMMDD format. Since version 3.0',
            default=None,
        )
        group2.add_argument(
            '--json',
            action='store_true',
            help='print result as JSON in stdout',
        )
        group2.add_argument(
            '--to-html',
            metavar='FILE',
            help='format results as html file FILE. Argument can be specified multiple times. Since version 4.0',
            action='append',
            dest="html",
        )
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

        class RssOptionException(RssException):
            pass

        raise RssOptionException(message)


class RssDownloader:
    def download(self, url) -> RssDocument:
        class RssDownloadAndParseFailedException(RssException):
            pass

        try:
            downloaded_document = feedparser.parse(url)
            if downloaded_document.bozo:
                raise downloaded_document.bozo_exception
            return RssDocument.parse(downloaded_document)
        except Exception as e:
            raise RssDownloadAndParseFailedException("Failed to download url / parse document", e)


class RssCache:
    class RssCacheException(RssException):
        pass

    def __init__(self, cache_file=tempfile.gettempdir() + os.path.sep + "rss-reader.cache"):
        self.cache_file = cache_file
        self.logger = logging.getLogger("RssCache")

    def store(self, document: RssDocument):
        self.logger.debug("Storing document to cache [cache_file=%s, document=%s]", self.cache_file, document)
        try:
            with open(self.cache_file, "w") as file:
                file.write(JsonRssFormatter().format(document))
        except Exception as e:
            raise self.RssCacheException(f"Failed to save cache to {self.cache_file}", e)

    def load(self) -> RssDocument:
        self.logger.debug("Loading document from cache [cache_file=%s]", self.cache_file)
        try:
            with open(self.cache_file, "r") as file:
                content = " ".join(file.readlines())
                document = json.loads(content)
                return RssDocument(
                    title=document['title'],
                    updated=document['updated'],
                    items=[RssItem(
                        title=item['title'],
                        link=item['link'],
                        published_date=item['published_date'],
                    ) for item in document['items']],
                )
        except Exception as e:
            raise self.RssCacheException(f"Failed to load cache from {self.cache_file}", e)


class RssReader:
    EXIT_CODE_OK = 0
    EXIT_CODE_ERROR = 2
    EXIT_CODE_VALIDATION_ERROR = 3

    logger = logging.getLogger("RssReader")
    downloader = RssDownloader()
    cache = RssCache()

    @staticmethod
    def run(args=None):
        try:
            reader = RssReader(args)
            reader.load_rss()
            print(reader.format_output())
            reader.generate_files()
        except RssException as e:
            RssReader.logger.error("Execution failed", exc_info=e)
            print(f"Execution failed: {e}")

    def __init__(self, args=None):
        self.args = self.validate_args(args)
        self.logger.debug("Using args: %ss", self.args)

    def validate_args(self, args):
        parser = RssReaderOptionsParser()
        try:
            args = parser.parse_args(args)
        except Exception as e:
            print(f"Error: {e}")
            parser.print_usage()
            exit(self.EXIT_CODE_ERROR)
        if args.help:
            parser.print_help()
            exit(self.EXIT_CODE_OK)
        if args.version:
            print(f"Version: {__version__}")
            exit(self.EXIT_CODE_OK)
        # Other validations
        date_format = "YYYYMMDD"
        if args.date and args.date.isdecimal() and len(args.date) != len(date_format):
            print(f"Argument 'date' should have format {date_format}, when specified")
            parser.print_usage()
            exit(self.EXIT_CODE_VALIDATION_ERROR)
        if not args.date and not args.url:
            print(f"Argument 'url' should be present")
            parser.print_usage()
            exit(self.EXIT_CODE_VALIDATION_ERROR)
        if args.limit is not None and args.limit <= 0:
            print(f"Argument 'limit' should be positive number, when specified")
            parser.print_usage()
            exit(self.EXIT_CODE_VALIDATION_ERROR)
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

    def load_rss(self):
        if self.args.url:
            self.document = self.downloader.download(self.args.url)
            self.cache.store(self.document)
        else:
            assert self.args.date  # args.date should be defined
            self.document = self.cache.load()
            filter_date = datetime.strptime(self.args.date, "%Y%m%d")
            items = list(filter(
                lambda i: i.published_day() == filter_date,
                self.document.items
            ))
            if len(items) == 0:
                class NoRssItemFound(RssException):
                    pass

                raise NoRssItemFound(f"No RSS item was found with published_date={self.args.date}")
            self.document.items = items
        self.document.items = self.document.items[:self.args.limit]
        return self.document

    def format_output(self):
        formatter: RssFormatter = JsonRssFormatter() if self.args.json else TextRssFormatter()
        return formatter.format(self.document)

    def generate_files(self):
        failures = []
        generated = []
        if self.args.html:
            html = HtmlRssFormatter().format(self.document)
            for file in self.args.html:
                try:
                    with open(file, "w") as f:
                        f.write(html)
                    generated.append(file)
                    self.logger.debug("File %s was generated", file)
                except Exception as e:
                    self.logger.error(f"Failed to generate file {file}", exc_info=e)
                    failures.append((file, e))
        if failures:
            class RssDocumentGenerationException(RssException):
                pass
            RssDocumentGenerationException(f"Failed to generate files {failures}")
        return generated


