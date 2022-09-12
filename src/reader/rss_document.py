import logging
from typing import TypedDict

import feedparser

logger = logging.getLogger(__file__)


class RssItem:
    """Example:
    <item>
        <title>
            Diana's last moments: French doctor recalls 'tragic night'
        </title>
        <link>
            https://news.yahoo.com/dianas-last-moments-french-medic-063826757.html
        </link>
        <pubDate>2022-08-29T06:38:26Z</pubDate>
        <source url="http://www.ap.org/">Associated Press</source>
        <guid isPermaLink="false">dianas-last-moments-french-medic-063826757.html</guid>
        <media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/yqGArLJ2zmrvTqDfFZDb4Q--~B/aD0xNDg4O3c9MjA0ODthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/ap.org/f0e3a0f5516d6e0ce4a71d18151e3260" width="130"/>
        <media:credit role="publishing company"/>
    </item>
    """

    def __init__(self, d: dict):
        logger.debug("Parsing RssItem %s", d)
        self.title = d['title']
        self.link = d['link']
        self.published_date = d['published']

    def __repr__(self):
        return f"RssItem(" \
               f"title={self.title}, "\
               f"link={self.link}, "\
               f"published_date={self.published_date}, "\
               f")"


class RssDocument:
    """ Example:
    <rss version="2.0">
        <channel>
            <title>Yahoo News - Latest News & Headlines</title>
            <link>https://www.yahoo.com/news</link>
            <description>
                The latest news and headlines from Yahoo! News. Get breaking news stories and in-depth coverage with videos and photos.
            </description>
            <language>en-US</language>
            <copyright>Copyright (c) 2022 Yahoo! Inc. All rights reserved</copyright>
            <pubDate>Tue, 30 Aug 2022 05:34:10 -0400</pubDate>
            <ttl>5</ttl>
            <image>
                <title>Yahoo News - Latest News & Headlines</title>
                <link>https://www.yahoo.com/news</link>
                <url>
                    http://l.yimg.com/rz/d/yahoo_news_en-US_s_f_p_168x21_news.png
                </url>
            </image>
            <item>
                ...
            </item>
        </channel>
    </rss>
    """

    def __init__(self, d: feedparser.FeedParserDict, limit):
        logger.debug("Parsing RssDocument %s", d)
        self.title = d['feed']['title']
        self.updated = d['updated']
        self.items = [RssItem(item) for item in d['items'][:limit]]
        logger.debug(f'Parsed document {self}')

    def __repr__(self):
        return f"RssDocument(" \
               f"title={self.title}, " \
               f"updated={self.updated}" \
               f"items={self.items}" \
               f")"

