# SPDX-FileCopyrightText: 2024-present linuxdaemon <linuxdaemon.irc@gmail.com>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from pathlib import Path
from typing import Sequence


def get_first_existing_file(files: Sequence[str | Path]) -> Path | None:
    for file in files:
        p = Path(file)
        if p.exists():
            return p

    return None
