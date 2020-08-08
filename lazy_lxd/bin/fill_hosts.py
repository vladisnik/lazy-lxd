#!/usr/bin/env python3

import sys
import argparse

from ipaddress import IPv4Address, AddressValueError
from python_hosts import Hosts, HostsEntry
from python_hosts.exception import UnableToWriteHosts


def parse_option() -> object:
    """
    Set arguments list with which script running

    Args:
        args: Arguments which passed to script.

    Returns:
        object: The parser object with calling parse_args
    """

    def check_ip(parser: argparse.ArgumentParser, arg):
        """
        Verify argument from argparse.
        IP address should be ip address in human readable notation.
        """
        try:
            IPv4Address(arg)
            return arg
        except AddressValueError:
            parser.error(f"{arg} is not a valid IP address")

    def check_hostname(parser: argparse.ArgumentParser, arg):
        """
        Verify argument from argparse.
        Hosname shouldn't contains symbols: !, %, [, ], {, }, _, ;, :, <, >, ?, ,, $,
                                            #, ^, *, (, ), ', ", `, \\, /
        """
        forbidden_symbols = [
            '!', '%', '[', ']', '{', '}', '_', ';', ':', '<', '>', '?',
            ',', '$', '#', '^', '*', '(', ')', '\'', '"', '`', '\\', '/'
        ]
        for symbol in forbidden_symbols:
            if arg.find(symbol) != -1:
                parser.error(f"Hostname {arg} contains forbidden symbol {symbol}")

        return arg

    parser = argparse.ArgumentParser(
        description="Fill the /etc/hosts with hostname "
        "and its ip address from arguments."
    )
    parser.add_argument(
        'hostname', type=lambda a: check_hostname(parser, a),
        help="Hostname with which the ip will be associated."
    )
    parser.add_argument(
        'ip', type=lambda a: check_ip(parser, a),
        help="IP address ehre requests will go."
    )
    parser.add_argument(
        'hosts_file', help="Path hosts file which needs to fill"
    )

    return parser.parse_args()


def main():
    arguments = parse_option()

    hostname = arguments.hostname
    ip_addr = arguments.ip
    hosts_file = Hosts(arguments.hosts_file)

    # chechk if hostname, ip pair esists in hosts file
    if hosts_file.exists(address=ip_addr, names=hostname):
        print(
            f"{ip_addr} {hostname} pair exists in {hosts_file.hosts_path}",
            file=sys.stderr, end=''
        )
        sys.exit(1)

    new_pair = HostsEntry(entry_type='ipv4', address=ip_addr, names=[hostname])
    try:
        hosts_file.add([new_pair])
        hosts_file.write()
    except UnableToWriteHosts:
        print(f"Unable to write to {hosts_file.hosts_path}", file=sys.stderr, end='')
        sys.exit(1)


if __name__ == '__main__':
    main()
