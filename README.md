# URL router utility

Version number: 0.0.1
Author: Walter Leibbrandt

## Overview

Route URLs to configured programs/browsers.

## Installation

To install use pip:

    $ pip install uroute


Or clone the repo:

    $ git clone https://github.com/walterl/uroute.git
    $ python setup.py install

## Usage

    $ uroute-config add --default --name "Firefox Private Window" --run "firefox --no-remote --private-window %u"
    $ uroute https://python.org
