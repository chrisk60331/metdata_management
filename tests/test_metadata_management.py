import os
from unittest.mock import Mock, patch

from freezegun import freeze_time
from typer.testing import CliRunner
import json
import pytest

from metadata_management import __app_name__, __version__, cli, SUCCESS
from metadata_management.manager import Metadata, CurrentMetadata

runner = CliRunner()
TEST_DB = "./test_db.json"


def test_cli_version():
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" in result.stdout


def test_cli_add():
    try:
        result = runner.invoke(cli.app, ["init", "--db-path", TEST_DB])
        assert result.exit_code == 0, result
        result = runner.invoke(cli.app, ["add", "host01#ipv4address", "127.0.0.1", "test"])
        assert result.exit_code == 0, result
    finally:
        os.remove(TEST_DB)


def test_cli_inactive():
    try:
        result = runner.invoke(cli.app, ["init", "--db-path", TEST_DB])
        assert result.exit_code == 0, result
        result = runner.invoke(cli.app, ["add", "host01#ipv4address", "127.0.0.1", "test"])
        assert result.exit_code == 0, result
        result = runner.invoke(cli.app, ["set-inactive", "host01#ipv4address"])
        assert result.exit_code == 0, result
    finally:
        os.remove(TEST_DB)


def test_cli_remove():
    try:
        result = runner.invoke(cli.app, ["init", "--db-path", TEST_DB])
        assert result.exit_code == 0, result
        result = runner.invoke(cli.app, ["add", "host01#ipv4address", "127.0.0.1", "test"])
        assert result.exit_code == 0, result
        result = runner.invoke(cli.app, ["remove", "host01#ipv4address"])
        assert result.exit_code == 0, result
    finally:
        os.remove(TEST_DB)


@pytest.fixture
def mock_json_file(tmp_path):
    metadata = CurrentMetadata(metadata={
        "host03": {
            "Value": "bar",
            "Comment": "baz",
            "AssignedBy": "",
            "AssignedDateUTC": "2022-02-17T16:11:29.093288",
            "inactive": False,
        }
    }, error=SUCCESS)
    db_file = tmp_path / "metadata.json"
    with db_file.open("w") as db:
        json.dumps(metadata)
    return db_file


test_data1 = CurrentMetadata(metadata={
    "host03": {
        "Value": "bar",
        "Comment": "baz",
        "AssignedBy": "bap",
        "AssignedDateUTC": "2022-02-17T16:11:29.093288",
        "inactive": False,
    }
}, error=SUCCESS)
test_data2 = CurrentMetadata({
    "host02": {
        "Value": "bar",
        "Comment": "baz",
        "AssignedBy": "bap",
        "AssignedDateUTC": "2022-02-17T16:11:29.093288",
        "inactive": False,
    }
}, error=SUCCESS)


@pytest.mark.parametrize(
    "metadata_title, metadata_value, comment, expected",
    [
        pytest.param("host03", "bar", "baz", test_data1),
        pytest.param("host02", "bar", "baz", test_data2),
    ],
)
@freeze_time("2022-02-17T16:11:29.093288", tz_offset=-4)
def test_add(mock_json_file, metadata_title, metadata_value, comment, expected):
    metadata_management = Metadata(mock_json_file)
    with patch("metadata_management.manager.CURRENT_USER", "bap"):
        assert metadata_management.add(metadata_title, metadata_value, comment) == expected
    read = metadata_management._db_handler.read_metadata()
    assert len(read.metadata) == 1
