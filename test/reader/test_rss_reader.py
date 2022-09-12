import logging
import unittest

from reader.rss_reader import RssReaderOptionsParser, RssReader
import sys


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

    def test_parse_args_failed_without_providing_url(self):
        try:
            self.parser.parse_args([])
            self.fail('url is required')
        except Exception as e:
            self.assertTrue('the following arguments are required: url' in str(e))

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


class RssReaderTest(unittest.TestCase):
    URL = "https://news.yahoo.com/rss/"

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

    def test_download_url(self):
        reader = RssReader(['--verbose', '--limit', '1', self.URL])
        document = reader.download()
        self.assertEqual(1, len(document.items))
