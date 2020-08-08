#!/usr/bin/env python3

"""
Lazy-LXD: Easy Create LXD Container And Run Asible Playbooks Over It.

This module contains the main logic to create container
and running ansible playbooks over it.
"""

import sys


def main():
    from .lazy_lxd import main
    main()
    sys.exit(0)


if __name__ == '__main__':
    main()
