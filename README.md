# metadata_management
A tool to manage metadata. **Data is stored in a local JSON file**. Integrated with AWS, this tool can also request and store IP CIDR ranges for AWS account provisioning.

**Note:** This tool generates its data and stores it locally! The database needs to be checked into a config repo or copied to s3 or RDS or the like.

***Note:*** Failure to copy the database to a persisted, versioned location ***will*** result in data loss.


## Getting started
```
git checkout https://gitlab.com/boosted-commerce/infra/metadata_management.git
pip install -r requirements.txt
```
## Usage
```
python -m metadata_management init
python -m metadata_management add account-owner user123 "transfer ownership"
python -m metadata_management assign-ipv4-network Account_id_123 24 
python -m metadata_management list-all
```
## Testing
```PYTHONPATH=. pytest tests``` 