"""This module provides the CLI."""
from pathlib import Path
from typing import List, Optional

import typer

from metadata_management import (
    ERRORS,
    __app_name__,
    __version__,
    config,
    database,
)
from metadata_management.manager import Metadata

app = typer.Typer()


@app.command()
def init(
    db_path: str = typer.Option(
        str(database.DEFAULT_DB_FILE_PATH),
        "--db-path",
        "-db",
        prompt="metadata database location?",
    ),
) -> None:
    """Initialize the metadata database."""
    app_init_error = config.init_app(db_path)
    if app_init_error:
        typer.secho(
            f'Creating config file failed with "{ERRORS[app_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    db_init_error = database.init_database(Path(db_path))
    if db_init_error:
        typer.secho(
            f'Creating database failed with "{ERRORS[db_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(
            f"The metadata database is {db_path}", fg=typer.colors.GREEN
        )


def get_manager() -> Metadata:
    if config.CONFIG_FILE_PATH.exists():
        db_path = database.get_database_path(config.CONFIG_FILE_PATH)
    else:
        typer.secho(
            'Config file not found. Please, run "metadata_management init"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    if db_path.exists():
        return Metadata(db_path)
    else:
        typer.secho(
            'Database not found. Please, run "metadata_management init"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)


@app.command()
def add(
    metadata_title: str = typer.Argument(...),
    metadata_value: str = typer.Argument(...),
    comment: str = typer.Argument(...),
) -> None:
    """Add a new metadata with a comment."""
    manager = get_manager()
    metadata, error = manager.add(metadata_title, metadata_value, comment)
    if error:
        typer.secho(
            f'Adding metadata failed with "{ERRORS[error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(
            f"""metadata: "{metadata}" was added """,
            fg=typer.colors.GREEN,
        )


@app.command()
def reserve_ipv4_network(
    host: str = typer.Argument(...),
    network_mask_bits: int = typer.Argument(...),
    ipam_name: str = typer.Argument(...),
) -> None:
    """Allocate a new IPv4 range."""
    manager = get_manager()
    metadata, error = manager.reserve_ipv4_network(
        host, ipam_name=ipam_name, mask_bits=network_mask_bits
    )
    if error:
        typer.secho(
            f'Adding IPv4 network failed with "{ERRORS[error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(
            f"""metadata: "{metadata}" was added """,
            fg=typer.colors.GREEN,
        )


@app.command(name="list")
def list_all() -> None:
    """List all metadata."""
    manager = get_manager()
    metadata = manager.get_metadata()
    if len(metadata) == 0:
        typer.secho(
            "There are no entries in the metadata list yet",
            fg=typer.colors.RED,
        )
        raise typer.Exit()
    typer.secho("\nmetadata list:\n", fg=typer.colors.BLUE, bold=True)
    columns = ("Value", "Content", "ReservedBy", "ReservedDateUTC", "inactive")
    headers = " ".join(columns)
    typer.secho(headers, fg=typer.colors.BLUE, bold=True)
    typer.secho("-" * len(headers), fg=typer.colors.BLUE)
    for _id in metadata.keys():
        output = [_id] + [str(_key) for _key in metadata[_id].values()]
        typer.secho(
            " ".join(output),
            fg=typer.colors.BLUE,
        )
    typer.secho("-" * len(headers) + "\n", fg=typer.colors.BLUE)


@app.command(name="set-inactive")
def set_inactive(metadata_title: str = typer.Argument(...)) -> None:
    """Complete a metadata by setting it as inactive using its metadata_ID."""
    manager = get_manager()
    metadata, error = manager.set_inactive(metadata_title)
    if error:
        typer.secho(
            f'Completing metadata # "{metadata_title}" failed with "{ERRORS[error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(
            f"""metadata # {metadata_title} completed!""",
            fg=typer.colors.GREEN,
        )


@app.command()
def remove(
    metadata_title: str = typer.Argument(...),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force deletion without confirmation.",
    ),
) -> None:
    """Remove a metadata using its metadata title."""
    manager = get_manager()

    def _remove():
        _metadata, error = manager.remove(metadata_title)
        if error:
            typer.secho(
                f'Removing metadata # {metadata_title} failed with "{ERRORS[error]}"',
                fg=typer.colors.RED,
            )
            raise typer.Exit(1)
        else:
            typer.secho(
                f"""metadata # {metadata_title}: '{_metadata}' was removed""",
                fg=typer.colors.GREEN,
            )

    if force:
        _remove()
    else:
        metadata = manager.get_metadata()
        try:
            metadata = metadata[metadata_title]
        except IndexError:
            typer.secho("Invalid metadata_ID", fg=typer.colors.RED)
            raise typer.Exit(1)
        delete = typer.confirm(f"Delete metadata # {metadata_title}?")
        if delete:
            _remove()
        else:
            typer.echo("Operation canceled")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return
