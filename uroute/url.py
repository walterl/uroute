"""URL parsing and processing functions."""

import re


def extract_url(contents):
    """Attempts to find and extract a URL from the given content."""
    # Based on https://stackoverflow.com/a/840110
    match = re.search(r'(?P<url>https?://[^\s]+)', contents)
    if match and match.group('url'):
        return match.group('url')
    return None


def clean_url(url):
    # XXX stub
    return url
