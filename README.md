# Uroute: Route URLs to configured browsers

## Overview

Uroute allows you to easily open an URL in one of your configured browsers or
-profiles. It enables privacy concious browsing by opening URLs, for example,
in the Tor browser, with Firefox's *Local* profile, a temporary Iridium
profile, or Firefox's *VPN* profile.

This program was developed for and tested on Ubuntu 18.04 (Bionic). It should
work in other Freedesktop environments with Python 3 and GTK 3 installed.


## Installation

    $ sudo apt install python3-gi
    $ mkvirtualenv -p $(which python3) uroute
    $ pip install git+https://github.com/walterl/uroute.git
    $ ln -s /usr/lib/python3/dist-packages/gi $VIRTUAL_ENV/lib/python3.6/site-packages/


## Usage

    $ uroute https://fsf.org


## Features

* [X] Open command-line argument URL in any of the configured external browsers.
* [X] Detect if Uroute is the default browser, and install it as such.
* [X] Modify URL before opening it in the selected browser.
* [X] Modify command-line of configured browser launching it.
* [ ] Filter/clean URL before launching browser
* [ ] Set default browser dynamically, based on URL
* [ ] GUI for managing configuration
* [ ] Import configuration from installed browsers' XDG desktop entries
  * [ ] Remove tracking parameters
  * [ ] Automatically unshorten links


## Example configuration

    $ cat ~/.uroute.ini
    [main]
    default_program = tor-browser

    [program:firefox-local]
    name = Firefox
    command = firefox -P Local --private-window
    icon = /usr/share/icons/hicolor/64x64/apps/firefox.png

    [program:firefox-vpn]
    name = Firefox: VPN
    command = firefox -P VPN --private-window
    icon = /usr/share/icons/hicolor/64x64/apps/firefox.png

    [program:brave-incog]
    name = Brave: Incognito
    command = brave-browser --incognito
    icon = /usr/share/icons/hicolor/64x64/apps/brave-browser.png

    [program:tor-browser]
    name = Tor browser
    command = /home/walter/.local/share/tor-browser_en-US/Browser/start-tor-browser --detach
    icon = /home/walter/.local/share/tor-browser_en-US/Browser/browser/chrome/icons/default/default128.png

    [program:iridium-incog]
    name = Iridium: Incognito
    command = iridium-browser --incognito
    icon = /usr/share/icons/hicolor/64x64/apps/iridium-browser.png

    [program:iridium-tor-temp]
    name = Iridium: Tor, temp profile
    command = iridium-browser --temp-profile --proxy-server=socks5://127.0.0.1:9050
    icon = /usr/share/icons/hicolor/64x64/apps/iridium-browser.png
