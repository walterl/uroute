"""URL parsing and processing functions."""

import json
import logging
import re
from urllib.parse import parse_qsl, unquote, urlencode, urlparse, urlunparse
from urllib.request import Request, urlopen

log = logging.getLogger(__name__)


def extract_url(contents):
    """Attempts to find and extract a URL from the given content."""
    # Based on https://stackoverflow.com/a/840110
    match = re.search(r'(?P<url>https?://[^\s]+)', contents)
    if match and match.group('url'):
        return match.group('url')
    return None


class UrlCleaner:
    """Manages and loads URL cleaning data, and uses it to clean URLs.

    If the specified rules file path (`rules_path`) does not point to a valid
    JSON file, ClearURLs's `data.min.json
    <https://gitlab.com/ClearURLs/rules/-/blob/master/data.min.json>`_
    is automatically downloaded and used.
    """

    URL_CLEARURLS_DATA = (
        'https://rules2.clearurls.xyz/data.minify.json'
    )

    def __init__(self, rules_path):
        self.rules_path = rules_path
        self._init_rules_data()

    def _init_rules_data(self):
        try:
            with open(self.rules_path) as rules_file:
                self.rules_data = json.load(rules_file)
            log.debug('URL cleaning rules loaded from %r', self.rules_path)
        except Exception:
            # If anything went wrong reading the rules file, redownload
            # it.
            self.download_rules_data(self.rules_path)
            with open(self.rules_path) as rules_file:
                self.rules_data = json.load(rules_file)
            log.debug('URL cleaning rules loaded from %r', self.rules_path)

    def clean_url(self, url, recurse_redir=True):
        """Clean the given URL with the loaded rules data.

        The format of `rules_data` is the parsed JSON found in ClearURLs's
        [`data.min.json`](https://gitlab.com/ClearURLs/rules/-/blob/master/data.min.json)
        file.

        URLs matching a provider's `urlPattern` and one of that provider's
        redirection patterns, will cause the URL to be replaced with the
        match's first matched group.

        Another Python implementation to download and apply the rules to a
        URL, written by the ClearURLs author, can be found
        [here](https://gitlab.com/KevinRoebert/ClearUrls/snippets/1834899).

        Set `recurse_redir=False` to prevent cleaning redirect targets
        recursively.
        """
        for provider in self.rules_data.get('providers', {}).values():
            if not re.match(provider['urlPattern'], url, re.IGNORECASE):
                continue

            # If any exceptions are matched, this provider is skipped
            if any(
                re.match(exc, url, re.IGNORECASE)
                for exc in provider.get('exceptions', [])
            ):
                continue

            for redir in provider.get('redirections', []):
                match = re.match(redir, url, re.IGNORECASE)
                try:
                    if match and match.group(1) and match.group(1) != url:
                        url = unquote(match.group(1))
                        # If redirect found, recurse on target
                        if recurse_redir:
                            url = self.clean_url(url, recurse_redir=True)
                        return url
                except IndexError:
                    # If we get here, we got a redirection match, but no
                    # matched grouped. The redirection rule is probably
                    # faulty.
                    pass

            # Explode query parameters to be checked against rules
            parsed_url = urlparse(url)
            query_params = parse_qsl(parsed_url.query)

            for rule in (
                *provider.get('rules', []),
                *provider.get('referralMarketing', [])
            ):
                query_params = [
                    param for param in query_params
                    if not re.match(rule, param[0], re.IGNORECASE)
                ]

            url = urlunparse((
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                parsed_url.params,
                urlencode(query_params),
                parsed_url.fragment,
            ))

            for raw_rule in provider.get('rawRules', []):
                url = re.sub(raw_rule, '', url)

        return url

    def download_rules_data(self, save_path=None):
        log.debug('Downloading rules data to %r', save_path)
        with open(save_path, 'w') as rules_file:
            request = Request(self.URL_CLEARURLS_DATA,
                              headers={'User-Agent': 'uroute URLCleaner (python urllib)'})
            rules_file.write(urlopen(request).read().decode())
