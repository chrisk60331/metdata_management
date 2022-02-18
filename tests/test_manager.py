from unittest.mock import patch

import pytest
from freezegun import freeze_time

from metadata_management import SUCCESS
from metadata_management.manager import Metadata, CurrentMetadata
from tests.test_cli import test_data1, test_data2, ASSIGNED_DATE, mock_json_file

test_data3 = CurrentMetadata(
    metadata={
        "account03": {
            "Value": "10.0.1.0/24",
            "Comment": "auto-assigned IP",
            "AssignedBy": "bap",
            "AssignedDateUTC": ASSIGNED_DATE,
            "inactive": False,
        }
    },
    error=SUCCESS,
)
test_data4 = CurrentMetadata(
    metadata={
        "account04": {
            "Value": "10.0.2.0/24",
            "Comment": "auto-assigned IP",
            "AssignedBy": "bap",
            "AssignedDateUTC": ASSIGNED_DATE,
            "inactive": False,
        }
    },
    error=SUCCESS,
)


@pytest.mark.parametrize(
    "metadata_title, metadata_value, comment, expected",
    [
        pytest.param("account03", "bar", "baz", test_data1),
        pytest.param("account02", "bar", "baz", test_data2),
    ],
)
@freeze_time(ASSIGNED_DATE, tz_offset=-4)
def test_add(mock_json_file, metadata_title, metadata_value, comment, expected):
    metadata_management = Metadata(mock_json_file)
    with patch("metadata_management.manager.CURRENT_USER", "bap"):
        assert (
            metadata_management.add(metadata_title, metadata_value, comment) == expected
        )
    read = metadata_management._db_handler.read_metadata()
    assert len(read.metadata) == 1


@pytest.mark.parametrize(
    "metadata_title, expected",
    [
        pytest.param("account03", test_data3),
    ],
)
@freeze_time(ASSIGNED_DATE, tz_offset=-4)
def test_assign_ipv4_network(mock_json_file, metadata_title, expected):
    metadata_management = Metadata(mock_json_file)
    with patch("metadata_management.manager.CURRENT_USER", "bap"):
        actual = metadata_management.assign_ipv4_network(metadata_title, 24)
        assert actual == expected
        read = metadata_management._db_handler.read_metadata()
        assert len(read.metadata) == 2
        actual = metadata_management.assign_ipv4_network("account04", 24)
        assert actual == test_data4