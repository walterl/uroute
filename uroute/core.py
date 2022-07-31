"""Core logic."""

import logging
import subprocess
from collections import namedtuple

from uroute import url as u, xdgdesktop
from uroute.config import Config


Program = namedtuple('Program', ('name', 'command', 'icon'))

log = logging.getLogger(__name__)


class Uroute:
    def __init__(self, url, preferred_prog=None):
        self.url = url
        self.default_program = None
        self.preferred_prog = preferred_prog
        self.url_cleaning_rules = {}

        # Load config
        self.config = Config()
        self._init_logging()
        self.programs = self._load_config_programs()

    def _init_logging(self):
        logging_config = {
            'level': 'INFO',
            'format': '%(levelname)s %(message)s',
        }

        if 'logging' in self.config:
            logging_config.update(dict(self.config['logging']))

        logging.basicConfig(**logging_config)

    def _load_config_programs(self):
        programs = {}
        for section_name in self.config.sections():
            if not section_name.startswith('program:'):
                continue

            prog_id = section_name[len('program:'):]
            if prog_id in programs:
                log.warn('Duplicate config for program %s', prog_id)
            section = self.config[section_name]

            programs[prog_id] = Program(
                name=section['name'],
                command=section['command'],
                icon=section.get('icon'),
            )

        try:
            self.default_program = self.config['main']['default_program']
        except KeyError:
            # Config does not specify default program
            self.default_program = None

        return programs

    def clean_url(self, url):
        """Cleans the given URL with the configured rules data file.

        The value of ``config['main']['clean_urls_rules_file']`` must
        point to a valid JSON file, from which rule data will be read.

        :seealso: :class:`uroute.url.UrlCleaner`
        """
        if not self.url_cleaning_rules:
            rules_file = self.config['main'].get('clean_urls_rules_file')
            if not rules_file:
                rules_file = xdgdesktop.get_data_file_path('rules.json')
            self.url_cleaning_rules = u.load_cleaning_rules(rules_file)

        return u.clean_url(self.url_cleaning_rules, url)

    def get_program(self, prog_id=None):
        if not self.programs:
            raise ValueError('No programs configured')

        if prog_id is None and self.preferred_prog:
            if self.preferred_prog in self.programs:
                prog_id = self.preferred_prog
            else:
                log.warn(
                    'No such program configured: %s', self.preferred_prog,
                )
        if prog_id is None:
            prog_id = self.default_program

        if not prog_id:
            return self.programs[tuple(self.programs.keys())[0]]

        if prog_id not in self.programs:
            raise ValueError('Unknown program ID: {}'.format(prog_id))
        return self.programs[prog_id]

    def get_command(self, program):
        if not isinstance(program, Program):
            program = self.get_program(program)
        return program.command

    def run_with_url(self, command):
        log.debug('Routing URL %s to command: %s', self.url, command)

        run_args = [
            arg == '@URL' and self.url or arg for arg in command.split()
        ]

        if self.url not in run_args:
            run_args.append(self.url)

        subprocess.run(run_args)

    def set_as_default_browser(self):
        """Installs Uroute as the default browser for the current user."""
        try:
            return xdgdesktop.install_as_default(
                xdgdesktop.get_or_create_desktop_file(),
            )
        except FileNotFoundError as exc:
            log.warn('Command not found %s', exc)
            return False
