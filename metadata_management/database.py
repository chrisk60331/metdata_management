"""Database access module."""
import configparser
import json
from typing import Any, Dict, List, NamedTuple
from pathlib import Path
import configparser
from metadata_management import (
    DB_READ_ERROR,
    DB_WRITE_ERROR,
    JSON_ERROR,
    SUCCESS,
)

DEFAULT_DB_FILE_PATH = Path.home().joinpath(
    "." + Path.home().stem + "_metadata.json"
)


def get_database_path(config_file: Path) -> Path:
    """Return the current path to the metadata database."""
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return Path(config_parser["General"]["database"])


def init_database(db_path: Path) -> int:
    """Create the metadata database."""
    try:
        db_path.write_text("[]")  # Empty metadata list
        return SUCCESS
    except OSError:
        return DB_WRITE_ERROR


class DBResponse(NamedTuple):
    metadata: Dict[str, Any]
    error: int


class DatabaseHandler:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def read_metadata(self) -> DBResponse:
        try:
            with self._db_path.open("r") as db:
                try:
                    data = db.read()
                    return DBResponse(
                        json.loads("{}" if data == "[]" else data), SUCCESS
                    )
                except json.JSONDecodeError:  # Catch wrong JSON format
                    return DBResponse({}, JSON_ERROR)
        except OSError:  # Catch file IO problems
            return DBResponse({}, DB_READ_ERROR)

    def write_metadata(self, metadata: Dict[str, Any]) -> DBResponse:
        try:
            existing_rows = self.read_metadata().metadata
            existing_rows.update(metadata)
            with self._db_path.open("w") as db:
                json.dump(existing_rows, db, indent=4)
            return DBResponse(metadata, SUCCESS)
        except OSError:  # Catch file IO problems
            return DBResponse(metadata, DB_WRITE_ERROR)
