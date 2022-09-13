# Rss reader utility

Rss reader utility is python utility for downloading RSS news.

## Usage
Utility can be installed using `pip install .`. Utility is installed with all dependencies
and can be run as command `rss-reader <args>` or can be executed using `python rss_reader.py <args>`.

Usage of utility is as followed
```shell
usage: rss_reader.py [--help] [--version] [--json] [--verbose] [--limit LIMIT] [url]

Pure Python command-line RSS reader.

  --help, -h     show this help message and exit
  --version      print version of Rss reader utility and exit

  --json         print result as JSON in stdout
  --verbose      outputs verbose status messages
  --limit LIMIT  limit news topics if this parameter provided
  url            RSS url to be used
```

### RSS url
Argument `url` is used to specify RSS server for downloading RSS feeds.

### Formatting output
Utility provides two formatting options, plain text (default) and json (when `--json` is specified).

#### Text formatter (default)
Plain text output format is
```text
Feed: $rssFeedName
Last update: $rssLastUpdate

Title: $feed1Title
Published: $feed1PublishedDate
Link: $feed1Link

Title: $feed2Title
Published: $feed2PublishedDate
Link: $feed2Link

...
```

#### Json formatter (`--json`)
Json output format is
```json
{
  "title": "$rssFeedName",
  "updated": "$rssLastUpdate",
  "items": [
    {
      "title": "$feed1Title",
      "link": "$feed1Link",
      "published_date": "$feed1PublishedDate"
    },
    {
      "title": "$feed2Title",
      "link": "$feed2Link",
      "published_date": "$feed2PublishedDate"
    }
  ]
}
```

