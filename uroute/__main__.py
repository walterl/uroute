import argparse
import logging

from uroute import Uroute

log = logging.getLogger(__name__)


def create_argument_parser():
    parser = argparse.ArgumentParser(
        description='Route URL to a configured program.',
    )

    parser.add_argument('URL', help='URL to route.')
    parser.add_argument(
        '--program', '-p', help='The program to open the URL with.',
    )
    parser.add_argument('--verbose', '-v', action='count', default=0)

    return parser


def main():
    options = create_argument_parser().parse_args()
    ur = Uroute(options.URL, verbose=options.verbose)
    try:
        ur.route(program=options.program)
    except Exception as error:
        log.error(str(error))


if __name__ == "__main__":
    main()
