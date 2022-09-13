import logging
import os
import unittest

from reader.rss_document import RssDocument, RssItem
from reader.rss_reader import RssReaderOptionsParser, RssReader, RssDownloader, RssException, RssCache

URL = "https://news.yahoo.com/rss/"


def repeat_failed(times):
    logger = logging.getLogger("repeater")

    def repeat_helper(f):
        def call_helper(*args):
            last_exception = None
            for i in range(0, times):
                try:
                    last_exception = None
                    f(*args)
                    break
                except Exception as e:
                    last_exception = e
                    logger.debug("Failed to execute %s - trying %s/%s", f, i, times, exc_info=e)
            if last_exception:
                raise last_exception

        return call_helper

    return repeat_helper


class RssReaderOptionsParserTest(unittest.TestCase):
    def setUp(self):
        self.parser = RssReaderOptionsParser()

    def test_parse_args(self):
        args = self.parser.parse_args([
            '--help',
            '--version',
            '--json',
            '--verbose',
            '--limit', '5',
            'url'
        ])
        self.assertTrue(args.help)
        self.assertTrue(args.version)
        self.assertTrue(args.json)
        self.assertTrue(args.verbose)
        self.assertEqual(5, args.limit)
        self.assertEqual('url', args.url)

    def test_parse_args_with_single_url(self):
        args = self.parser.parse_args([
            'url'
        ])
        self.assertEqual('url', args.url)

    def test_parse_args_should_succeed_without_providing_url(self):
        self.parser.parse_args([])

    def test_parse_args_failed_for_unknown_argument(self):
        try:
            self.parser.parse_args(['--unknown', 'url'])
            self.fail('should fail for unknown argument')
        except Exception as e:
            self.assertTrue('unrecognized arguments: --unknown' in str(e))

    def test_parse_args_failed_for_multiple_urls(self):
        try:
            self.parser.parse_args(['url', 'url2'])
            self.fail('should fail for two urls specified')
        except Exception as e:
            self.assertTrue('unrecognized arguments: url2' in str(e))

    def test_parse_args_failed_for_invalid_limit(self):
        try:
            self.parser.parse_args(['url', '--limit', 'XXX'])
            self.fail('should fail for two urls specified')
        except Exception as e:
            self.assertTrue('argument --limit: invalid int value' in str(e))


class RssDownloaderTest(unittest.TestCase):
    def test_download(self):
        RssDownloader().download(URL)

    def test_download_fails_for_wrong_url(self):
        try:
            document = RssDownloader().download("https://unknown.url")
            self.fail(f"Should fail for unknown url. Found {document}")
        except RssException as e:
            # OK
            print(e)
            pass


class RssCacheTest(unittest.TestCase):
    def test_store_and_load(self):
        cache = RssCache()
        document = RssDocument('title', 'updated', [RssItem("item title", "link", "published_date")])
        cache.store(document)
        loaded = cache.load()
        self.assertEqual(str(document), str(loaded))

    def test_load_when_cache_file_not_exist(self):
        cache = RssCache()
        try:
            os.remove(cache.cache_file)
        except:
            # ignore if cache did not exist
            pass
        try:
            cache.load()
            self.fail("Should fail if cache file not exist")
        except RssException as e:
            # OK
            print(e)
            pass


class RssReaderTest(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_help(self):
        try:
            RssReader(['--help'])
            self.fail('should exit when --help is specified')
        except SystemExit as e:
            self.assertEqual(0, e.code)

    def test_version(self):
        try:
            RssReader(['--version'])
            self.fail('should exit when --version is specified')
        except SystemExit as e:
            self.assertEqual(0, e.code)

    def test_url_is_not_provided(self):
        try:
            RssReader([])
            self.fail('should fail when no url is specified')
        except SystemExit as e:
            self.assertEqual(3, e.code)

    def test_logs_on_verbose(self):
        RssReader(['--verbose', 'url'])
        logging.getLogger(str(self)).debug("should be printed")

    def test_logs_when_no_verbose(self):
        RssReader(['url'])
        logging.getLogger(str(self)).debug("no output should be present")

    def test_download_url_fails_on_unknown_url(self):
        reader = RssReader(['--verbose', 'https://unknown-url'])
        try:
            reader.load_rss()
            self.fail('Should fail for unknown url')
        except Exception as e:
            self.assertTrue('Failed to download url / parse document' in str(e))

    def test_download_url(self):
        document = RssReader(['--verbose', URL]).load_rss()

    def test_download_url_with_limit(self):
        reader = RssReader(['--verbose', '--limit', '1', URL])
        reader.load_rss()
        self.assertEqual(1, len(reader.document.items))

    @repeat_failed(10)  # can happen, that new feed is posted between two downloads, in that case we repeat the check
    def test_download_url_with_too_large_limit(self):
        document_unlimited = RssReader(['--verbose', URL]).load_rss()
        document_limited = RssReader(['--verbose', '--limit', '100000', URL]).load_rss()
        self.assertEqual(str(document_unlimited), str(document_limited))

    def test_load_from_cache_with_date(self):
        reader = RssReader(['--verbose', '--date', '20220101'])
        reader.cache.store(RssDocument("title",
                                       "updated",
                                       [
                                           RssItem("title1", "link1", "2022-01-01T01:02:03Z"),
                                           RssItem("title2", "link2", "2030-01-01T00:00:00Z"),
                                       ]))
        document = reader.load_rss()
        self.assertEqual(str([RssItem("title1", "link1", "2022-01-01T01:02:03Z")]), str(document.items))

    def test_load_from_cache_with_date_and_limit(self):
        date = '2022-01-01T01:02:03Z'
        reader = RssReader(['--verbose', '--date', '20220101', '--limit', '1'])
        reader.cache.store(RssDocument("title",
                                       "updated",
                                       [
                                           RssItem("title1", "link1", date),
                                           RssItem("title2", "link2", date),
                                       ]))
        document = reader.load_rss()
        self.assertEqual(str([RssItem("title1", "link1", date)]), str(document.items))

    def test_load_from_cache_with_date_fail_when_no_items_are_present(self):
        reader = RssReader(['--verbose', '--date', '20300101'])
        reader.cache.store(RssDocument("title",
                                       "updated",
                                       [
                                           RssItem("title1", "link1", "2022-01-01T01:02:03Z"),
                                           RssItem("title2", "link2", "2022-01-01T01:02:03Z"),
                                       ]))
        try:
            document = reader.load_rss()
            self.fail("Should fail if no items found for date")
        except RssException as e:
            # OK
            print(e)
            pass
