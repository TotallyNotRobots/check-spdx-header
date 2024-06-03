# SPDX-FileCopyrightText: 2024-present linuxdaemon <linuxdaemon.irc@gmail.com>
#
# SPDX-License-Identifier: MIT

from pathlib import Path

from check_spdx_header import util


def test_get_first_existing_file_no_files(tmp_path: Path) -> None:
    possible = [tmp_path / "a.txt", tmp_path / "b.txt"]

    file = util.get_first_existing_file(possible)
    assert file is None


def test_get_first_existing_file_second_file(tmp_path: Path) -> None:
    possible = [tmp_path / "a.txt", tmp_path / "b.txt"]

    possible[1].touch()

    file = util.get_first_existing_file(possible)
    assert file == possible[1]


def test_get_first_existing_file_first_file(tmp_path: Path) -> None:
    possible = [tmp_path / "a.txt", tmp_path / "b.txt"]

    possible[0].touch()

    file = util.get_first_existing_file(possible)
    assert file == possible[0]


def test_get_first_existing_file_both_files(tmp_path: Path) -> None:
    possible = [tmp_path / "a.txt", tmp_path / "b.txt"]

    possible[0].touch()
    possible[1].touch()

    file = util.get_first_existing_file(possible)
    assert file == possible[0]
