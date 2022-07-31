import unittest
from urllib.parse import quote

from uroute import url


class TestCleanUrl(unittest.TestCase):
    rules = {'providers': {'dummy provider': {
        'urlPattern': '^',
        'redirections': [
            'https:\\/\\/redir.to\\/([^&]+)',
            'https:\\/\\/another.to\\/\\?t=([^&]+)',
        ]}},
    }
    inner_redir_target = 'https://ddg.co/'
    outer_redir_target = 'https://another.to/?t=' + inner_redir_target
    in_url = 'https://redir.to/' + quote(outer_redir_target)

    def test_removes_single_redirect(self):
        self.assertEqual(
            url.clean_url(self.rules, self.in_url, recurse_redir=False),
            self.outer_redir_target,
        )

    def test_recursively_removes_redirects(self):
        self.assertEqual(
            url.clean_url(self.rules, self.in_url),
            self.inner_redir_target,
        )


if __name__ == '__main__':
    unittest.main()
