import datetime
import os
import pwd
from ipaddress import ip_network
from pathlib import Path

from metadata_management import DB_READ_ERROR, ID_ERROR
from metadata_management.database import DatabaseHandler
from typing import Any, Dict, NamedTuple

LAST_ASSIGNED_NETWORK = "last_assigned_network"
CURRENT_USER = pwd.getpwuid(os.getuid())[0]


class CurrentMetadata(NamedTuple):
    metadata: Dict[str, Any]
    error: int


class Metadata:
    def __init__(self, db_path: Path) -> None:
        self._db_handler = DatabaseHandler(db_path)

    def get_metadata(self) -> Dict[str, Any]:
        """Return the current metadata dict."""
        read = self._db_handler.read_metadata()
        return read.metadata

    def add(
        self, metadata_title: str, metadata_value: str, comment: str
    ) -> CurrentMetadata:
        """Add a new metadata to the database."""
        metadata = {
            "Value": metadata_value,
            "Comment": comment,
            "AssignedBy": CURRENT_USER,
            "AssignedDateUTC": datetime.datetime.utcnow().isoformat(),
            "inactive": False,
        }
        read = self._db_handler.read_metadata()
        if read.error == DB_READ_ERROR:
            return CurrentMetadata(metadata, read.error)
        read.metadata[metadata_title] = metadata
        write = self._db_handler.write_metadata(read.metadata)
        return CurrentMetadata({metadata_title: metadata}, write.error)

    def assign_ip_network(
        self, host: str, size: str = "/24"
    ) -> CurrentMetadata:
        metadata = self.get_metadata()
        last_assigned_network = ip_network(metadata.get(LAST_ASSIGNED_NETWORK))
        next_network = last_assigned_network.broadcast_address + size
        return self.add(host, next_network, "auto-assigned IP")

    def set_inactive(self, metadata_title: str) -> CurrentMetadata:
        """Set a metadata as inactive."""
        read = self._db_handler.read_metadata()
        if read.error:
            return CurrentMetadata({}, read.error)
        try:
            metadata = read.metadata[metadata_title]
        except IndexError:
            return CurrentMetadata({}, ID_ERROR)
        metadata["inactive"] = True
        write = self._db_handler.write_metadata(read.metadata)
        return CurrentMetadata(metadata, write.error)

    def remove(self, metadata_title: str) -> CurrentMetadata:
        """Remove a metadata from the database using its id or index."""
        read = self._db_handler.read_metadata()
        if read.error:
            return CurrentMetadata({}, read.error)
        try:
            metadata = read.metadata.pop(metadata_title)
        except IndexError:
            return CurrentMetadata({}, ID_ERROR)
        write = self._db_handler.write_metadata(read.metadata)
        return CurrentMetadata(metadata, write.error)
