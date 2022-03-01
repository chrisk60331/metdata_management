import boto3


class AWSAPIOperation:
    def __init__(self, region_name: str, dry_run: bool = True):
        self.client = boto3.client("ec2")
        self.dry_run = dry_run
        self.region_name = region_name


class IPAM(AWSAPIOperation):
    def __init__(self, region_name: str = None, dry_run: bool = True):
        super().__init__(region_name, dry_run)
        self.name = None
        self.ipam_id = None
        self.pool_name = None

    def from_new(self):
        self.region_name = self.region_name
        response = self.client.create_ipam(
            DryRun=self.dry_run,
            OperatingRegions=[
                {"RegionName": self.region_name},
            ],
        )
        self.ipam_id = response.get("IpamId")
        return self

    def from_existing(self, name: str):
        self.name = name
        response = self.client.describe_ipams(
            DryRun=self.dry_run,
            Filters=[
                {
                    "Name": "string",
                    "Values": [
                        str(self.name),
                    ],
                },
            ],
        )
        self.ipam_id = response.get("IpamId")
        return self

    def delete(self):
        return self.client.delete_ipam(
            DryRun=self.dry_run, IpamId=self.ipam_id
        )


class Scope(AWSAPIOperation):
    def __init__(self, ipam_id, region_name):
        super().__init__(region_name)
        response = self.client.create_ipam_scope(
            DryRun=self.dry_run, IpamId=ipam_id
        )
        self.ipam_scope_id = response.get("IpamScopeId")

    def delete(self):
        return self.client.delete_ipam_scope(
            DryRun=True | False, IpamScopeId=self.ipam_scope_id
        )


class Pool(AWSAPIOperation):
    def __init__(self, region_name: str):
        super().__init__(region_name)
        self.ipam_pool_id = None
        self.Cidr = None

    def from_new(self, ipam):
        response = self.client.create_ipam_pool(
            DryRun=self.dry_run,
            IpamScopeId=ipam.scope_id,
            AddressFamily="ipv4",
            PubliclyAdvertisable=False,
        )
        self.ipam_pool_id = response.get("IpamPoolId")
        return self

    def from_existing(self, pool_id):
        response = self.client.get_ipam_pool_allocations(
            DryRun=self.dry_run,
            IpamPoolId=pool_id,
        )
        self.ipam_pool_id = response.get("IpamPoolId")
        return self

    def allocate_cidr(self, netmask_length):
        response = self.client.allocate_ipam_pool_cidr(
            DryRun=self.dry_run,
            IpamPoolId=self.ipam_pool_id,
            NetmaskLength=netmask_length,
        )
        self.Cidr = response.get("Cidr")
        return self

    def delete(self):
        deprovision = self.client.deprovision_ipam_pool_cidr(
            DryRun=self.dry_run,
            IpamPoolId=self.ipam_pool_id,
        )
        deprovision.update(
            self.client.delete_ipam_pool(
                DryRun=self.dry_run, IpamPoolId=self.ipam_pool_id
            )
        )
        return deprovision