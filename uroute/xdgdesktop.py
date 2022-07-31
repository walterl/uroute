"""Contains all freedesktop-related functionality."""

import logging
import os
import shutil
import subprocess

import xdg.BaseDirectory
from xdg.DesktopEntry import DesktopEntry

log = logging.getLogger(__name__)


def get_or_create_desktop_file():
    desktop = lookup_desktop_file('uroute.desktop')

    if desktop is None:
        path = os.path.join(
            xdg.BaseDirectory.xdg_data_home, 'applications', 'uroute.desktop',
        )
        desktop = DesktopEntry(path)
        desktop.set('Version', '1.0')
        desktop.set('Name', 'Uroute')
        desktop.set('Comment', 'URL router.')
        desktop.set('Exec', 'uroute %U')
        desktop.set('StartupNotify', 'true')
        desktop.set('Terminal', 'false')
        desktop.set('Categories', 'Network;WebBrowser;')
        desktop.set(
            'MimeType', ';'.join((
                'text/html',
                'text/xml',
                'application/xhtml_xml',
                'application/xhtml+xml',
                'image/webp',
                'video/webp',
                'x-scheme-handler/http',
                'x-scheme-handler/https',
                'x-scheme-handler/ftp',
                ''  # End with a ;
            ))
        )
        desktop.write(trusted=True)
        log.debug('Created Uroute desktop entry at %s', path)

    return desktop


def lookup_desktop_file(filename):
    """Tries load `filename` from the `applications` sub-directory of
    each directory in `xdg.BaseDirectory.xdg_data_dirs`.

    Returns `None` if not found.
    """
    for dirname in xdg.BaseDirectory.xdg_data_dirs:
        filepath = os.path.join(dirname, 'applications', filename)
        if os.path.isfile(filepath):
            log.debug('Found desktop entry: %s', filepath)
            return DesktopEntry(filepath)
    log.debug('Unable to find desktop file %s', filename)
    return None


def install_as_default(desktop):
    if get_default_browser() == 'uroute.desktop':
        return True  # Uroute is the default browser already

    return set_default_browser(desktop)


def get_default_browser():
    which('xdg-settings', raise_exception=True)

    cmd = 'xdg-settings get default-web-browser'.split()
    try:
        default = subprocess.check_output(cmd).decode().strip()
        log.debug('$ %r => %s', cmd, default)
        return default
    except Exception:  # pylint: disable=broad-except
        log.exception('Unable to get default browser:')
    return None


def set_default_browser(desktop_entry):
    which('xdg-settings', raise_exception=True)
    cmd = 'xdg-settings set default-web-browser'.split()
    cmd.append(os.path.split(desktop_entry.getFileName())[1])
    try:
        subprocess.check_output(cmd)
        log.debug('$ %r', cmd)
        return True
    except Exception:  # pylint: disable=broad-except
        log.exception('Unable to set default browser with cmd %r:', cmd)
    return False


def which(prog, raise_exception=False):
    if shutil.which(prog) is None:
        if raise_exception:
            raise FileNotFoundError(prog)
        return False
    return True


def get_data_file_path(filename):
    """Returns the full path to the *data file* indicated by `filename`.

    Parent directories will be created where they are missing.

    On Ubuntu, it will act like this:

        >>> get_data_file_path('foo.bar')
        /home/myuser/.local/share/uroute/foo.bar

    """
    data_file_name = os.path.join(
        xdg.BaseDirectory.xdg_data_home, 'uroute', filename,
    )

    # Ensure that `data_file_name`'s parent directory exists
    dir_name = os.path.dirname(data_file_name)
    if not os.path.isdir(dir_name):
        log.debug('Creating dirs: %s', dir_name)
        os.makedirs(dir_name)
    else:
        log.debug('Data file dir: %s', dir_name)

    return data_file_name
