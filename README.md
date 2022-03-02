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
Usage: metadata_management [OPTIONS] COMMAND [ARGS]...

Options:
  -v, --version                   Show the application's version and exit.
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.

Commands:
  add                   Add a new metadata with a comment.
  init                  Initialize the metadata database.
  list                  List all metadata.
  remove                Remove a metadata using its metadata title.
  reserve-ipv4-network  Allocate a new IPv4 range.
  set-inactive          Complete a metadata by setting it as inactive...

```
## Testing
```PYTHONPATH=. pytest tests``` 