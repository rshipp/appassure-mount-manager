AppAssure Mount Manager
=======================

A simple web interface to manage AppAssure recovery point mounting,
built on Pyramid, Bootstrap, and [python-appassure][1].

[1]: https://github.com/george2/python-appassure "python-appassure"

## Setup

Install `python-appassure` from git:

    sudo pip install git+https://github.com/george2/python-appassure.git

Rename `aamm/config.example.py` to `aamm/config.py` and set the
variables in that file to reflect your AppAssure server configuration.

Install `aamm`:

    sudo python setup.py install

Finally, serve AppAssure Mount Manager as you would any Pyramid app, using
`pserve` or through your production-ready server of choice.
