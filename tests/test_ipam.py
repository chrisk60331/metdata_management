from unittest import mock
from unittest.mock import Mock

from moto import mock_ec2

import metadata_management
from metadata_management.ipam import IPAM


@mock_ec2
def test_ipam_initializes():
    # given.
    ipam = IPAM()
    expected = [
        "region_name",
        "name",
        "ipam_id",
    ]

    # when.
    actual = [hasattr(ipam, attribute) for attribute in expected]

    # then.
    assert all(actual)


def test_ipam_from_new():
    with mock.patch(
        "metadata_management.aws.boto3",
        Mock(
            client=Mock(return_value=Mock(create_ipam=Mock(return_value={})))
        ),
    ):
        from metadata_management.ipam import IPAM

        ipam = IPAM(region_name="foo-region")

        actual = ipam.from_new()

    assert isinstance(actual, IPAM)


def test_ipam_from_existing():
    with mock.patch(
        "metadata_management.aws.boto3",
        Mock(
            client=Mock(return_value=Mock(create_ipam=Mock(return_value={})))
        ),
    ):
        from metadata_management.ipam import IPAM

        ipam = IPAM(region_name="foo-region")

        actual = ipam.from_existing("foo-ipam")

    assert isinstance(actual, IPAM)
