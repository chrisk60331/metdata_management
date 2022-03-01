import os
from unittest import mock
from unittest.mock import Mock

from typer.testing import CliRunner
import json
import pytest

from metadata_management import __app_name__, __version__, cli, SUCCESS
from metadata_management.manager import CurrentMetadata

runner = CliRunner()
TEST_DB = "./test_db.json"
ASSIGNED_DATE = "2022-02-17T16:11:29.093288"
test_data1 = CurrentMetadata(
    metadata={
        "account03": {
            "Value": "bar",
            "Comment": "baz",
            "AssignedBy": "bap",
            "AssignedDateUTC": ASSIGNED_DATE,
            "inactive": False,
        }
    },
    error=SUCCESS,
)
test_data2 = CurrentMetadata(
    {
        "account02": {
            "Value": "bar",
            "Comment": "baz",
            "AssignedBy": "bap",
            "AssignedDateUTC": ASSIGNED_DATE,
            "inactive": False,
        }
    },
    error=SUCCESS,
)


@pytest.fixture
def mock_db(tmp_path):
    try:
        result = runner.invoke(cli.app, ["init", "--db-path", TEST_DB])
        assert result.exit_code == 0, result
        yield result
    finally:
        os.remove(TEST_DB)


@pytest.fixture
def mock_json_file(tmp_path):
    metadata = CurrentMetadata(
        metadata={
            "account03": {
                "Value": "bar",
                "Comment": "baz",
                "AssignedBy": "",
                "AssignedDateUTC": ASSIGNED_DATE,
                "inactive": False,
            }
        },
        error=SUCCESS,
    )
    db_file = tmp_path / "metadata.json"
    with db_file.open("w") as db:
        json.dumps(metadata)
    return db_file


def test_cli_version():
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" in result.stdout


def test_cli_add(mock_db):
    result = runner.invoke(
        cli.app, ["add", "account01#ipv4address", "127.0.0.1", "test"]
    )
    assert result.exit_code == 0, result


def test_cli_reserve_ipv4_network(mock_db):
    with mock.patch(
        "metadata_management.manager.IPAM"
    ) as mock_ipam, mock.patch(
        "metadata_management.manager.Scope"
    ), mock.patch(
        "metadata_management.manager.Pool",
        Mock(
            return_value=Mock(
                from_existing=Mock(side_effect=[
                    Mock(Cidr="10.0.1.0/24"),
                    Mock(Cidr="10.0.2.0/24"),
                ])
            )
        ),
    ):
        mock_ipam.return_value.from_existing.return_value = Mock()
        result = runner.invoke(
            cli.app, ["reserve-ipv4-network", "account01", "24", "foo_pam"]
        )
    assert result.exit_code == 0, result


def test_cli_inactive(mock_db):
    result = runner.invoke(
        cli.app, ["add", "account01#ipv4address", "127.0.0.1", "test"]
    )
    assert result.exit_code == 0, result
    result = runner.invoke(cli.app, ["set-inactive", "account01#ipv4address"])
    assert result.exit_code == 0, result


def test_cli_remove(mock_db):
    result = runner.invoke(
        cli.app, ["add", "account01#ipv4address", "127.0.0.1", "test"]
    )
    assert result.exit_code == 0, result
    result = runner.invoke(cli.app, ["remove", "account01#ipv4address"])
    assert result.exit_code == 0, result
