import logging
import sys
import unittest

from reader.rss_document import RssDocument, RssItem
from reader.rss_formatter import JsonRssFormatter, TextRssFormatter, HtmlRssFormatter

logging.basicConfig(
    stream=sys.stdout,
    filemode="w",
    level=logging.DEBUG,
    force=True,
    format="%(asctime)s [%(levelname)-5s] %(module)s.%(funcName)s[%(lineno)d]: %(message)s")

IMAGE_LINK = "https://s.yimg.com/uu/api/res/1.2/R5j0twnGjY3dFUsENIcKcA--~B/aD00MDAwO3c9NjAwMDthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/ap.org/cf6457b451fe2161f930f26932654a0b"
FEED_LINK = "https://news.yahoo.com/womans-rape-cries-unheard-unmonitored-142708098.html"
DOCUMENT = RssDocument(
    title="document title",
    updated="1.1.2022",
    items=[
        RssItem(
            title="item title",
            link=FEED_LINK,
            published_date="1.1.2000",
            image_link=IMAGE_LINK
        )
    ],
)


class JsonRssFormatterTest(unittest.TestCase):
    def test_format(self):
        formatter = JsonRssFormatter()
        formatted = formatter.format(DOCUMENT)
        expected_json = """
        {
          "title": "document title",
          "updated": "1.1.2022",
          "items": [
            {
              "title": "item title",
              "link": """ + '"' + FEED_LINK + '"' + """,
              "published_date": "1.1.2000",
              "image_link": """ + '"' + IMAGE_LINK + '"' + """ 
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


class HtmlRssFormatterTest(unittest.TestCase):
    def test_format(self):
        formatter = HtmlRssFormatter()
        formatted = formatter.format(DOCUMENT)
        expected = """
<html>
    <head>
        <title>document title</title>
        <h1>document title</h1>
    </head>
    <body>
        <p>Last update: 1.1.2022</p>
        <h2>Feeds</h2>
        <p>
            <a href='""" + FEED_LINK + """'>item title</a> (published 1.1.2000)
            <br/>
            <img src='""" + IMAGE_LINK + """' width='130' height='86'/>
        </p>
    </body>
</html>
"""
        self.assertEqual(expected.replace(" ", "").replace("\n", ""), formatted.replace(" ", "").replace("\n", ""))
