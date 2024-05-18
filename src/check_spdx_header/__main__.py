# SPDX-FileCopyrightText: 2024-present linuxdaemon <linuxdaemon.irc@gmail.com>
#
# SPDX-License-Identifier: MIT

if __name__ == "__main__":
    import sys

    from check_spdx_header.cli import check_spdx_header

    sys.exit(check_spdx_header())
