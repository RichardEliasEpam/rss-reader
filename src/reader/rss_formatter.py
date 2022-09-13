import io
import json
import logging
from abc import abstractmethod

from reader.rss_document import RssDocument, RssItem

logger = logging.getLogger(__file__)


class RssFormatter:
    @abstractmethod
    def format_internal(self, document: RssDocument):
        raise NotImplemented

    def format(self, document: RssDocument):
        formatted = self.format_internal(document)
        logger.debug("Formatted output\n%s", formatted)
        return formatted


class JsonRssFormatter(RssFormatter):
    def format_internal(self, document: RssDocument):
        def format_item(i: RssItem):
            return {
                'title': i.title,
                'link': i.link,
                'published_date': i.published_date,
                'image_link': i.image_link,
            }

        def format_document(d: RssDocument):
            return {
                'title': d.title,
                'updated': d.updated,
                'items': [format_item(i) for i in d.items],
            }

        return json.dumps(format_document(document), indent=2)


class TextRssFormatter(RssFormatter):
    def format_internal(self, document: RssDocument):
        result = io.StringIO()
        result.write(f"Feed: {document.title}\n")
        result.write(f"Last update: {document.updated}\n")
        for i in document.items:
            result.write("\n")
            result.write(f"Title: {i.title}\n")
            result.write(f"Published: {i.published_date}\n")
            result.write(f"Link: {i.link}")
        result.write("\n")
        return result.getvalue()


class HtmlRssFormatter(RssFormatter):
    def format_internal(self, document: RssDocument):
        result = io.StringIO()
        result.write(f"""
        <html>
            <head>
                <title>{document.title}</title>
                <h1>{document.title}</h1>
            </head>
            <body>
            <p>Last update: {document.updated}</p>
            <h2>Feeds</h2>
        """)
        for i in document.items:
            result.write(f"<p>")
            result.write(f"<a href='{i.link}'>{i.title}</a>")
            result.write(f" (published {i.published_date})")
            if i.image_link:
                result.write("<br/>")
                result.write(f"<img src='{i.image_link}' width='130' height='86'/>")
            result.write(f"</p>")
        result.write(f"""
            </body>
        </html>
        """)
        return result.getvalue()

