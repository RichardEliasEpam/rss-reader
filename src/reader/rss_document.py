import logging
import feedparser

logger = logging.getLogger(__file__)


class RssItem:
    def __init__(self, title, link, published_date):
        self.title = title
        self.link = link
        self.published_date = published_date

    @staticmethod
    def parse(d: feedparser.FeedParserDict):
        result = RssItem(
            title=d['title'],
            link=d['link'],
            published_date=d['published'],
        )
        logger.debug("Parsed RssItem %s", result)
        return result

    def __repr__(self):
        return f"RssItem(" \
               f"title={self.title}, " \
               f"link={self.link}, " \
               f"published_date={self.published_date}, " \
               f")"


class RssDocument:
    def __init__(self, title, updated, items):
        self.title: str = title
        self.updated: str = updated
        self.items: [RssItem] = items

    @staticmethod
    def parse(d: feedparser.FeedParserDict, limit):
        result = RssDocument(
            title=d['feed']['title'],
            updated=d['updated'],
            items=[RssItem.parse(item) for item in d['items'][:limit]],
        )
        logger.debug("Parsed RssDocument %s", result)
        return result

    def __repr__(self):
        return f"RssDocument(" \
               f"title={self.title}, " \
               f"updated={self.updated}, " \
               f"items={self.items}" \
               f")"
