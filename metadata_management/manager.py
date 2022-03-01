"""Manage metadata database."""
import datetime
import os
import pwd
from pathlib import Path

from typing import Any, Dict, NamedTuple

from metadata_management import DB_READ_ERROR, ID_ERROR
from metadata_management.database import DatabaseHandler
from metadata_management.ipam import IPAM, Scope, Pool

CURRENT_USER = pwd.getpwuid(os.getuid())[0]
DEFAULT_BACKEND_IPV4_NETWORK = "10.0.0.0/24"


class CurrentMetadata(NamedTuple):
    """Object representing the row currently in memory."""

    metadata: Dict[str, Any]
    error: int


class Metadata:
    """An object representing a piece of information."""

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

    def reserve_ipv4_network(
        self,
        host: str,
        ipam_name: str = None,
        mask_bits: int = 24,
        region_name=None,
        dry_run: bool = True,
    ) -> CurrentMetadata:
        """Create an IP network reservation and store it in the database."""
        ipam = IPAM(dry_run=dry_run).from_existing(ipam_name)
        pool = Pool(region_name=region_name).from_existing(ipam.pool_name)
        pool.allocate_cidr(mask_bits)
        add_host_result = self.add(host, pool.Cidr, "auto-reserved IP")
        return add_host_result

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
