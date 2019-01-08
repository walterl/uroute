import configparser
import logging
import os
import subprocess
from collections import namedtuple


Program = namedtuple('Program', ('name', 'command'))
DEFAULT_CONFIG = os.path.expanduser('~/.uroute.ini')

log = logging.getLogger(__name__)


class Uroute:
    def __init__(self, verbose=False):
        self.config = configparser.ConfigParser()
        self.programs = {}
        self.default_program = None
        self.verbose = verbose

        self.load_config()

    def load_config(self, filename=None):
        if filename is None:
            filename = DEFAULT_CONFIG

        self.config.clear()
        self.config.read(filename)

        if 'uroute' in self.config:
            section = self.config['uroute']

            if 'default_program' in section:
                self.default_program = section['default_program']
            self._init_logging(section)

        self.programs = self._read_programs(self.config)

    def _init_logging(self, config_section):
        logging_config = {}
        if 'log_level' in config_section:
            logging_config['level'] = config_section['log_level']
        else:
            logging_config['level'] = 'INFO'
        if 'log_format' in config_section:
            logging_config['format'] = config_section['log_format']

        logging.basicConfig(**logging_config)

    def _read_programs(self, config):
        programs = {}
        for section_name in config.sections():
            if not section_name.startswith('program:'):
                continue

            prog_id = section_name[len('program:'):]
            if prog_id in programs:
                log.warn('Duplicate config for program %s', prog_id)
            section = config[section_name]

            programs[prog_id] = Program(
                name=section['name'],
                command=section['command'],
            )
        return programs

    def get_program(self, prog_id=None):
        if not self.programs:
            raise ValueError('No programs configured')

        if prog_id is None:
            prog_id = self.default_program

        if not prog_id:
            return self.programs[self.programs.keys()[0]]

        if prog_id not in self.programs:
            raise ValueError('Unknown program ID: {}'.format(prog_id))
        return self.programs[prog_id]

    def route(self, url, program=None):
        if isinstance(program, str) or program is None:
            program = self.get_program(program)

        if self.verbose > 0:
            log.debug('Routing URL {} to program {}'.format(url, program))

        run_args = [
            arg == '@URL' and url or arg for arg in program.command.split()
        ]

        if url not in run_args:
            run_args.append(url)

        log.info(repr(run_args))
        subprocess.run(run_args)
