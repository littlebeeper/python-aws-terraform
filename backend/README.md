## Context
This package defines a srv stack service

It mainly consists of the following components:
- Fargate ECS cluster to serve the API
- Cloudfront to serve the static website assets
- MongoDB Atlas as the persistent data store

## Setup

```commandline
cd backend
# install and package and activate its environment
poetry install && source .venv/bin/activate 
```

## Environments
```commandline
# test is meant for automated testing
# development is largely testing locally -- data input must be local & not all paths support development
# qa is largely mimicking production on cloud (includes external dependencies when possible)
# - Current caveat: qa points to production for uploading transcripts and calls meaning acct id is how we determine what is in qa, leverage srv acct id to do QA production is production
```

# Running scripts

## create an account id
```commandline
python backend/scripts/account_create.py --env {qa, production} --name {company name}
```

## upload calls
```commandline
python backend/scripts/import_calls.py --call-upload-file ../output/uploads/calldetails.txt --local-upload-directory ../output/uploads
```
```commandline
#call upload file is a CSV in output/uploads in the following format
,call_id,account_id,buyer,date,call_number,seller_names,transcript_format,transcript_file_path,call_file_path
0,,acct_2ebeeababb614536b917fcffe0d16b74,Silo,2022-12-09,1,"['Neha Shah', 'Jay Gokhale']",OTTER,Sabi.txt,
```
```commandline
# qa account id
acct_9aed7960c5aa444b8a06b2746db7311b
```

```commandline
# production account id (use this!)
acct_2ebeeababb614536b917fcffe0d16b74
```

## Running the server locally
### Pre-requisites
- Docker Desktop for Mac: https://docs.docker.com/desktop/install/mac-install/ (ensure it's up and running)
- Brew package manager: https://brew.sh/

Setup local testing environment (working directory: `srv/backend`)

Backend setup (working directory: doesn't matter)
```commandline
brew install supervisord
sudo mkdir -p /usr/local/srv/log/supervisord
sudo chown -R jay: /usr/local/srv
```

Frontend setup (working directory: `srv/backend`)
```commandline
cd backend/srv-fe
```

Run everything locally:
```commandline
# In two separate terminals, run this following: 

# Terminal 1
cd backend/srv-fe && yarn watch:development

# Terminal 2
supervisord -c local_services/supervisord.conf
```

While this is running correctly, you should be able to dynamically change the backend or the frontend code without needing to restart.

## Deploying 

### Prerequisites
- AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html
- AWS IAM user with credentials saved locally at `~/.aws/credentials` (see https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)

(working directory: `srv/backend`)
```commandline
# dryrun to see what will run
python backend/scripts/deploy.py --env {qa, production}

# run the deployment
python backend/scripts/deploy.py --env {qa, production} --real
```

### Db migrations
As we now use a no-sql db, we don't need to run schema migrations. 
However, we do need to run db migrations to update the data model. 
Today, we can run migrations by creating a script, writing tests, running it in qa and then in production.
