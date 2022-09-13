import logging
import sys
import unittest

from reader.rss_document import RssDocument, RssItem
from reader.rss_formatter import JsonRssFormatter, TextRssFormatter

logging.basicConfig(
                stream=sys.stdout,
                filemode="w",
                level=logging.DEBUG,
                force=True,
                format="%(asctime)s [%(levelname)-5s] %(module)s.%(funcName)s[%(lineno)d]: %(message)s")


class JsonRssFormatterTest(unittest.TestCase):
    def test_format(self):
        formatter = JsonRssFormatter()
        formatted = formatter.format(
            RssDocument(
                title="title",
                updated="1.1.2022",
                items=[
                    RssItem(
                        title="item title",
                        link="http://link",
                        published_date="1.1.2000",
                    )
                ],
            ))
        expected_json = """
        {
          "title": "title",
          "updated": "1.1.2022",
          "items": [
            {
              "title": "item title",
              "link": "http://link",
              "published_date": "1.1.2000"
            }
          ]
        }
        """
        self.assertEqual(expected_json.replace(" ", "").replace("\n", ""), formatted.replace(" ", "").replace("\n", ""))


class TextRssFormatterTest(unittest.TestCase):
    def test_format(self):
        formatter = TextRssFormatter()
        formatted = formatter.format(
            RssDocument(
                title="title",
                updated="1.1.2022",
                items=[
                    RssItem(
                        title="item title",
                        link="http://link",
                        published_date="1.1.2000",
                    )
                ],
            ))
        expected = """Feed: title
Last update: 1.1.2022

Title: item title
Published: 1.1.2000
Link: http://link
"""
        self.assertEqual(expected, formatted)

