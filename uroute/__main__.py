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
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--program', '-p', help='The program to open the URL with.',
    )
    group.add_argument(
        '--gui', '-g', action='store_true', help='Select program in GTK UI.',
    )

    return parser


def main():
    options = create_argument_parser().parse_args()
    ur = Uroute(options.URL)

    try:
        if options.gui:
            gui = UrouteGui(ur)
            command = gui.run()
        else:
            command = ur.get_command(program=options.program)
        if command:
            ur.run_with_url(command)
    except Exception as error:
        log.error(str(error))
        exit(1)


if __name__ == "__main__":
    main()
