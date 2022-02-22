import boto3

client = boto3.client("ec2")
DRY_RUN = True


class IPAM:
    def __init__(self, name, region_name=None):
        if name:
            response = client.describe_ipams(
                DryRun=DRY_RUN,
                Filters=[
                    {
                        'Name': 'string',
                        'Values': [
                            name,
                        ]
                    },
                ],
            )
        else:
            response = client.create_ipam(
                DryRun=DRY_RUN,
                OperatingRegions=[
                    {
                        'RegionName': region_name
                    },
                ]
            )
        self.IpamId = response.get("IpamId")

    def delete(self):
        client.delete_ipam(
            DryRun=DRY_RUN,
            IpamId=self.IpamId
        )


class Scope:
    def __init__(self, ipam_id):
        response = client.create_ipam_scope(
            DryRun=DRY_RUN,
            IpamId=ipam_id
        )
        self.IpamScopeId = response.get("IpamScopeId")

    def delete(self):
        client.delete_ipam_scope(
            DryRun=True | False,
            IpamScopeId=self.IpamScopeId
        )


class Pool:
    def __init__(self, ipam_scope_id):

        response = client.create_ipam_pool(
            DryRun=DRY_RUN,
            IpamScopeId=ipam_scope_id,
            AddressFamily='ipv4',
            PubliclyAdvertisable=False,
        )
        self.IpamPoolId = response.get("IpamPoolId")
        response = client.allocate_ipam_pool_cidr(
            DryRun=DRY_RUN,
            IpamPoolId=self.IpamPoolId
        )
        self.Cidr = response.get("Cidr")

    def delete(self):
        client.deprovision_ipam_pool_cidr(
            DryRun=DRY_RUN,
            IpamPoolId=self.IpamPoolId,
        )
        client.delete_ipam_pool(
            DryRun=DRY_RUN,
            IpamPoolId=self.IpamPoolId
        )
