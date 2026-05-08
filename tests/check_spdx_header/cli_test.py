# SPDX-FileCopyrightText: 2024-present linuxdaemon <linuxdaemon.irc@gmail.com>
#
# SPDX-License-Identifier: MIT

from pathlib import Path

from click.testing import CliRunner

import check_spdx_header
from check_spdx_header import cli


def test_version() -> None:
    runner = CliRunner()
    result = runner.invoke(cli.check_spdx_header, ["--version"])
    assert result.exit_code == 0
    assert (
        result.output
        == f"check-spdx-header, version {check_spdx_header.version}\n"
    )


def test_check(tmp_path: Path) -> None:
    runner = CliRunner()
    test_file = tmp_path / "test_file.py"
    test_file.write_text("#\n")
    result = runner.invoke(cli.check_spdx_header, [str(test_file)])
    assert result.exit_code == 1
    expected_result = f"""\
{test_file}:1: Missing license header
Found missing headers.
"""

    assert result.output == expected_result
    assert test_file.read_text() == "#\n"


def test_fix(tmp_path: Path) -> None:
    runner = CliRunner()
    test_file = tmp_path / "test_file.py"
    test_file.write_text("import foo\n")
    result = runner.invoke(cli.check_spdx_header, ["-f", str(test_file)])
    assert result.exit_code == 1
    expected = f"""\
Fixing {test_file} ...
Fixed missing headers.
"""

    assert result.output == expected

    expected = """\
# SPDX-FileCopyrightText: 2024-present linuxdaemon <linuxdaemon.irc@gmail.com>
#
# SPDX-License-Identifier: MIT

import foo
"""

    assert test_file.read_text() == expected


def test_fix_missing_line_break(tmp_path: Path) -> None:
    runner = CliRunner()
    test_file = tmp_path / "test_file.py"
    expected = """\
# SPDX-FileCopyrightText: 2024-present linuxdaemon <linuxdaemon.irc@gmail.com>
#
# SPDX-License-Identifier: MIT
import foo
"""

    test_file.write_text(expected)
    result = runner.invoke(cli.check_spdx_header, ["-f", str(test_file)])
    assert result.exit_code == 1
    expected = f"""\
Fixing {test_file} ...
Fixed missing headers.
"""

    assert result.output == expected

    expected = """\
# SPDX-FileCopyrightText: 2024-present linuxdaemon <linuxdaemon.irc@gmail.com>
#
# SPDX-License-Identifier: MIT

import foo
"""

    assert test_file.read_text() == expected


def test_fix_existing_2_blank_lines(tmp_path: Path) -> None:
    runner = CliRunner()
    test_file = tmp_path / "test_file.py"
    content = """\
# SPDX-FileCopyrightText: 2024-present linuxdaemon <linuxdaemon.irc@gmail.com>
#
# SPDX-License-Identifier: MIT


def foo():
    ...
"""

    test_file.write_text(content)
    result = runner.invoke(cli.check_spdx_header, ["-f", str(test_file)])
    assert result.exit_code == 0
    assert result.output == ""

    expected = """\
# SPDX-FileCopyrightText: 2024-present linuxdaemon <linuxdaemon.irc@gmail.com>
#
# SPDX-License-Identifier: MIT


def foo():
    ...
"""

    assert test_file.read_text() == expected


def test_fix_empty_file(tmp_path: Path) -> None:
    runner = CliRunner()
    test_file = tmp_path / "test_file.py"
    test_file.write_text("")
    result = runner.invoke(cli.check_spdx_header, ["-f", str(test_file)])
    assert result.exit_code == 1
    expected = f"""\
Fixing {test_file} ...
Fixed missing headers.
"""

    assert result.output == expected

    expected = """\
# SPDX-FileCopyrightText: 2024-present linuxdaemon <linuxdaemon.irc@gmail.com>
#
# SPDX-License-Identifier: MIT
"""

    assert test_file.read_text() == expected


def test_fix_empty_file_newline(tmp_path: Path) -> None:
    runner = CliRunner()
    test_file = tmp_path / "test_file.py"
    test_file.write_text("\n")
    result = runner.invoke(cli.check_spdx_header, ["-f", str(test_file)])
    assert result.exit_code == 1
    expected = f"""\
Fixing {test_file} ...
Fixed missing headers.
"""

    assert result.output == expected

    expected = """\
# SPDX-FileCopyrightText: 2024-present linuxdaemon <linuxdaemon.irc@gmail.com>
#
# SPDX-License-Identifier: MIT
"""

    assert test_file.read_text() == expected


def test_check_not_missing(tmp_path: Path) -> None:
    runner = CliRunner()
    test_file = tmp_path / "test_file.py"
    content = """\
# SPDX-FileCopyrightText: 2024-present linuxdaemon <linuxdaemon.irc@gmail.com>
#
# SPDX-License-Identifier: MIT
"""

    test_file.write_text(content)
    result = runner.invoke(cli.check_spdx_header, ["-f", str(test_file)])
    assert result.exit_code == 0
    assert result.output == ""

    expected = """\
# SPDX-FileCopyrightText: 2024-present linuxdaemon <linuxdaemon.irc@gmail.com>
#
# SPDX-License-Identifier: MIT
"""
    assert test_file.read_text() == expected
