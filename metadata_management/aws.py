"""A module for interacting AWS API."""
import boto3


class AWSAPIOperation:
    def __init__(self, region_name: str, dry_run: bool = True):
        self.client = boto3.client("ec2")
        self.dry_run = dry_run
        self.region_name = region_name