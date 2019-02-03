import argparse
import logging

from uroute import Uroute
from uroute.gui import UrouteGui

log = logging.getLogger(__name__)


def create_argument_parser():
    parser = argparse.ArgumentParser(
        description='Route URL to a configured program.',
    )

    parser.add_argument('URL', help='URL to route.')
    parser.add_argument(
        '--program', '-p', help='Preselect the specified program.',
    )

    return parser


def main():
    options = create_argument_parser().parse_args()
    ur = Uroute(options.URL, preferred_prog=options.program)

    try:
        command = UrouteGui(ur).run()
        if command:
            ur.run_with_url(command)
    except Exception as error:
        log.error(str(error))
        exit(1)


if __name__ == "__main__":
    main()
