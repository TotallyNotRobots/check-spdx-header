# SPDX-FileCopyrightText: 2024-present linuxdaemon <linuxdaemon.irc@gmail.com>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from itertools import takewhile
from pathlib import Path
from typing import Sequence, TypeVar

import click
from click.core import ParameterSource

from check_spdx_header._version import __version__
from check_spdx_header.util import get_first_existing_file

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


@dataclass
class Config:
    headers: list[str] = field(default_factory=list)
    license_spec: str | None = None
    fix: bool = False

    def read_config(self, path: Path) -> None:
        data = tomllib.loads(path.read_text())
        tool_cfg = data.get("tool", {}).get("check-spdx-header", {})
        headers = tool_cfg.get("headers")
        license_spec = tool_cfg.get(
            "license_spec", data.get("project", {}).get("license")
        )

        self.set_options(
            fix=tool_cfg.get("fix"), license_spec=license_spec, headers=headers
        )

    def set_option(self, name: str, value: object) -> None:
        self.set_options(**{name: value})  # type: ignore[arg-type]

    def set_options(
        self,
        *,
        fix: bool | None = None,
        license_spec: str | None = None,
        headers: list[str] | None = None,
    ) -> None:
        if fix is not None:
            self.fix = fix

        if license_spec is not None:
            self.license_spec = license_spec

        if headers is not None:
            self.headers = headers


pass_config = click.make_pass_decorator(Config, ensure=True)


def is_header(line: str) -> bool:
    return (
        line.startswith("# SPDX-") or line.rstrip() == "#" or not line.strip()
    )


def strip_lines(lines: list[str]) -> list[str]:
    out = lines.copy()
    while out and not out[-1].strip():
        out.pop()

    return out


def check(file: Path, config: Config) -> bool:
    text = file.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    existing_header = list(takewhile(is_header, lines))
    new_header = [
        f"# SPDX-FileCopyrightText: {item}\n" for item in config.headers
    ] + ["#\n", f"# SPDX-License-Identifier: {config.license_spec}\n"]

    filtered_lines = strip_lines(lines)
    filtered_existing_header = strip_lines(existing_header)
    filtered_new_header = strip_lines(new_header)

    if filtered_existing_header != filtered_lines:
        # If there is text after the header, add a blank line to separate them
        new_header.append("\n")
        # Preserve the final blank line on existing headers
        filtered_new_header.append("\n")
        if existing_header and not existing_header[-1].strip():
            filtered_existing_header.append("\n")

    if filtered_existing_header != filtered_new_header:
        # Fix
        if config.fix:
            click.echo(f"Fixing {file} ...", err=True)
            # Write
            lines[: len(existing_header)] = new_header
            file.write_text("".join(lines))
        else:
            click.echo(f"{file}:1: Missing license header", err=True)

        return True

    return False


FILES = ["pyproject.toml", "spdx_check.toml"]


def read_config(
    ctx: click.Context, _: click.Parameter, value: Path | None
) -> Path | None:
    cfg: Config = ctx.ensure_object(Config)
    if value is None:
        value = get_first_existing_file(FILES)

    if value is not None:
        cfg.read_config(value)

    return value


_T = TypeVar("_T")


@dataclass
class ConfigOptionSetter:
    name: str

    def __call__(
        self, ctx: click.Context, param: click.Parameter, value: _T
    ) -> _T:
        cfg: Config = ctx.ensure_object(Config)

        if param.name is None:
            msg = "Parameter name must be set"
            raise ValueError(msg)

        src = ctx.get_parameter_source(param.name)
        if src not in (ParameterSource.DEFAULT, ParameterSource.DEFAULT_MAP):
            cfg.set_option(self.name, value)

        return value


def config_option_setter(name: str) -> ConfigOptionSetter:
    return ConfigOptionSetter(name)


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--config",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    callback=read_config,
    expose_value=False,
    help="The config file to use instead of the default.",
    is_eager=True,
)
@click.version_option(version=__version__, prog_name="check-spdx-header")
@click.option(
    "--fix",
    "-f",
    is_flag=True,
    help="Automatically add the license header",
    callback=config_option_setter("fix"),
    expose_value=False,
)
@click.argument(
    "path",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    nargs=-1,
)
@click.pass_context
@pass_config
def check_spdx_header(
    config: Config, ctx: click.Context, path: Sequence[Path]
) -> None:
    """
    Check for SPDX license tags in source files.

    By default, configuration is loaded from either `pyproject.toml` or `spdx_check.toml`,
    in that order.
    """
    found_missing = False
    for p in path:
        files = p.rglob("*.py") if p.is_dir() else [p]
        for file in files:
            if check(file, config):
                found_missing = True

    if found_missing:
        click.echo(f"{'Fixed' if config.fix else 'Found'} missing headers.")
        ctx.exit(1)
